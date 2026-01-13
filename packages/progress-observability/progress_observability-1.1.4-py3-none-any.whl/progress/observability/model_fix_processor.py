"""Model Fix Processor

Custom span processor to fix missing gen_ai attributes in AI model spans.
This processor addresses bugs where AI model instrumentations fail to set
critical gen_ai attributes like gen_ai.provider.name, gen_ai.request.model, etc.

IMPORTANT: Model identifiers are preserved in their full form (including regional 
prefixes, dates, and version suffixes) to maintain accurate pricing information
and version specificity.

SUPPORTED CASES & FIXES:

1. OpenAI API Spans ("openai.chat", "ChatOpenAI.chat"):
   - Fixes gen_ai.provider.name (and gen_ai.system for backwards compatibility): "OpenAI" (default) vs "Azure" (when azure in endpoint) vs "OpenRouter" (when openrouter in endpoint OR model has provider prefix like google/, anthropic/, etc.) vs "Ollama" (when :11434 or ollama in endpoint)
   - Fixes missing gen_ai.request.model from gen_ai.response.model
   - Fixes missing/incorrect gen_ai.response.model
   - Preserves full model identifiers (e.g., gpt-4o-2024-11-20, google/gemini-2.0-flash-001)

2. Azure OpenAI LlamaIndex Spans ("AzureOpenAI.workflow"):
   - Forces gen_ai.provider.name to "Azure" (and gen_ai.system for backwards compatibility)
   - Aggressively fixes gen_ai.request.model when it differs from response model
   - Handles cases like request="gpt-35-turbo" vs response="gpt-4o-2024-11-20"
   - Preserves full model identifiers

3. Ollama Direct Spans ("ChatOllama.chat", "Ollama.workflow"):
   - Forces gen_ai.provider.name to "Ollama" (and gen_ai.system for backwards compatibility) 
   - Extracts model name from traceloop.association.properties.ls_model_name
   - Derives token usage from Ollama-specific attributes:
     * prompt_eval_count → gen_ai.usage.input_tokens (and gen_ai.usage.prompt_tokens for backwards compatibility)
     * eval_count → gen_ai.usage.output_tokens (and gen_ai.usage.completion_tokens for backwards compatibility)
     * prompt_eval_count + eval_count → llm.usage.total_tokens
   - Parses JSON in traceloop.entity.output for token counts when direct attributes missing

4. AWS Bedrock Spans ("bedrock.converse", "BedrockConverse.workflow"):
   - Forces gen_ai.provider.name to "AWS" (and gen_ai.system for backwards compatibility)
   - Fixes missing gen_ai.response.model from gen_ai.request.model
   - Preserves full Bedrock model IDs (e.g., us.anthropic.claude-sonnet-4-5-20250929-v1:0)
   - Regional prefixes (us., eu., au., jp., global.) preserved for accurate pricing
   - Derives token usage from traceloop.entity.output JSON:
     * raw.usage.inputTokens → gen_ai.usage.input_tokens (and gen_ai.usage.prompt_tokens for backwards compatibility)
     * raw.usage.outputTokens → gen_ai.usage.output_tokens (and gen_ai.usage.completion_tokens for backwards compatibility)
     * raw.usage.totalTokens → llm.usage.total_tokens
     * alternative_kwargs.prompt_tokens/completion_tokens/total_tokens (fallback)

5. Provider Detection Logic:
   - Azure: "azure" keyword in any endpoint/URL attribute
   - OpenRouter: "openrouter" keyword in any endpoint/URL attribute OR model name with provider prefix (google/, anthropic/, meta-llama/, etc.)
   - Ollama: ":11434" port or "ollama" keyword in endpoint
   - AWS: "AWS" in gen_ai.provider.name/gen_ai.system attribute or bedrock span names
   - OpenAI: Default fallback for openai.chat spans

"""

import os
import re
import logging
from collections import deque
from typing import Tuple, Optional, Any, Set
from opentelemetry.sdk.trace import SpanProcessor, ReadableSpan

logger = logging.getLogger(__name__)

# ---- Constants & simple helpers -------------------------------------------------

# System names
SYSTEM_AZURE = "Azure"
SYSTEM_OPENAI = "OpenAI"
SYSTEM_OPENROUTER = "OpenRouter"
SYSTEM_OLLAMA = "Ollama"
SYSTEM_AWS = "AWS"

# Invalid/empty model values
INVALID_MODEL_VALUES = (None, "", "unknown")

# Keywords for endpoint detection
AZURE_KEYWORD = "azure"
OPENROUTER_KEYWORD = "openrouter"
OLLAMA_KEYWORD = "ollama"

# OpenRouter model name prefixes (these indicate OpenRouter is being used)
OPENROUTER_MODEL_PREFIXES = (
    "google/", "anthropic/", "openai/", "meta-llama/", "meta/", "microsoft/", 
    "mistralai/", "cohere/", "ai21/", "huggingfaceh4/", "teknium/",
    "nousresearch/", "openchat/", "codellama/", "phind/", "wizardlm/",
    "upstage/", "01-ai/", "alpindale/", "austism/", "cognitivecomputations/",
    "databricks/", "deepseek/", "gryphe/", "intel/", "jondurbin/",
    "lizpreciator/", "migtissera/", "neversleep/", "undi95/", "xwin-lm/"
)

OLLAMA_DEFAULT_PORT = 11434
OLLAMA_SPAN_NAMES = ("ChatOllama.chat", "Ollama.workflow")
BEDROCK_SPAN_NAMES = ("bedrock.converse", "BedrockConverse.workflow")
ANTHROPIC_SPAN_NAMES = ("anthropic.converse", "Anthropic.workflow")

# Span names we explicitly care about (OpenAI, Azure OpenAI via LlamaIndex, Ollama, Bedrock)
SUPPORTED_SPAN_NAMES = {
    "openai.chat", 
    "openai.response",
    "ChatOpenAI.chat",
    "AzureOpenAI.workflow", 
    "Agent Workflow",
    *OLLAMA_SPAN_NAMES,
    *BEDROCK_SPAN_NAMES,
    *ANTHROPIC_SPAN_NAMES
}

def _is_ollama_span(span_name: str) -> bool:
    return span_name in OLLAMA_SPAN_NAMES

def _is_bedrock_span(span_name: str) -> bool:
    return span_name in BEDROCK_SPAN_NAMES

def _is_openrouter_model(model_name: Optional[str]) -> bool:
    """Check if a model name indicates OpenRouter usage."""
    if not model_name:
        return False
    model_name_lower = model_name.lower()
    return any(model_name_lower.startswith(prefix) for prefix in OPENROUTER_MODEL_PREFIXES)

def _is_invalid_model(value: Optional[str]) -> bool:
    """Check if a model value is invalid/empty."""
    return value in INVALID_MODEL_VALUES

def _extract_endpoint_info(attributes: dict) -> tuple[str, bool, bool, bool]:
    """
    Extract and analyze endpoint information from span attributes.
    
    Args:
        attributes: Dictionary of span attributes
        
    Returns:
        Tuple of (endpoint_string, is_azure, is_openrouter, is_ollama)
    """
    api_base = attributes.get("gen_ai.openai.api_base", "")
    endpoint = attributes.get("server.address") or attributes.get("http.url") or api_base
    endpoint_str = str(endpoint or "").lower()
    
    is_azure = AZURE_KEYWORD in endpoint_str
    is_openrouter = OPENROUTER_KEYWORD in endpoint_str
    is_ollama = f":{OLLAMA_DEFAULT_PORT}" in endpoint_str or OLLAMA_KEYWORD in endpoint_str
    
    return endpoint_str, is_azure, is_openrouter, is_ollama


class ModelFixProcessor(SpanProcessor):
    """
    Custom span processor to fix missing gen_ai attributes in AI model spans.
    
    This processor addresses bugs where AI model instrumentations fail to set
    critical gen_ai attributes like gen_ai.system, gen_ai.request.model, etc.
    
    Since we cannot modify span attributes after the span ends, we use a different
    approach: we monitor spans and try to set missing attributes during the span
    lifecycle by setting them as early as possible.
    
    Currently fixes:
    - gen_ai.provider.name (e.g., "Azure", "Ollama", "AWS") and gen_ai.system (backwards compatibility)
    - gen_ai.request.model (when missing but response.model is present)
    - gen_ai.response.model (when missing or incorrect)
    - gen_ai.usage.input_tokens and gen_ai.usage.prompt_tokens (for Ollama/Bedrock spans from provider-specific attributes)
    - gen_ai.usage.output_tokens and gen_ai.usage.completion_tokens (for Ollama/Bedrock spans from provider-specific attributes)
    - llm.usage.total_tokens (for Ollama/Bedrock spans from provider-specific attributes)
    
    Supported span types:
    - OpenAI models (openai.chat spans) - including Azure OpenAI
    - Azure OpenAI via LlamaIndex (AzureOpenAI.workflow spans)
    - Ollama models (ChatOllama.chat spans and Ollama.workflow spans)
    - AWS Bedrock models (bedrock.converse spans and BedrockConverse.workflow spans)
    
    Args:
        debug: Enable verbose debugging output. Can also be controlled via 
            OBSERVABILITY_DEBUG environment variable. Defaults to False.
        max_processed_spans: Maximum number of span IDs to track for double-processing
            prevention. Uses LRU eviction. Defaults to 10000.
    """
    
    # Backwards compatibility: retain attribute for external inspection if needed
    SUPPORTED_SPAN_NAMES = SUPPORTED_SPAN_NAMES

    def __init__(self, debug: bool = False, max_processed_spans: int = 10000):
        # Track processed spans with LRU eviction to prevent unbounded memory growth
        # Using deque for O(1) append and automatic size limiting
        self._processed_spans_deque: deque = deque(maxlen=max_processed_spans)
        self._processed_spans_set: Set[Tuple[int, int]] = set()
        
        # Debug flag - check env var or use parameter
        self.debug_enabled = debug or os.getenv('OBSERVABILITY_DEBUG', '').lower() in ('1', 'true', 'yes')
        
        if self.debug_enabled:
            logger.info(f"ModelFixProcessor initialized with debug mode enabled, max_processed_spans={max_processed_spans}")
    
    def on_start(self, span: Any, parent_context=None) -> None:
        """
        Called when a span is started (SpanProcessor interface method).
        
        This implementation intentionally does nothing as all processing happens in on_end()
        via the span_postprocess_callback mechanism.
        
        Args:
            span: The span being started
            parent_context: Optional parent context
        """
        pass
    
    def on_end(self, readable_span: ReadableSpan) -> None:
        """
        Called when a span is ended. Attempts to fix missing gen_ai attributes.
        
        This method is invoked via the span_postprocess_callback mechanism, allowing
        us to inspect and modify span attributes before they are exported.
        
        Args:
            readable_span: The span that has ended, containing attributes to potentially fix
        """
        # Skip unsupported span types
        if readable_span.name not in self.SUPPORTED_SPAN_NAMES:
            return
            
        # Prevent double-processing with LRU eviction
        span_context_id = (readable_span.context.span_id, readable_span.context.trace_id)
        
        if span_context_id in self._processed_spans_set:
            if self.debug_enabled:
                print(f"[ModelFixProcessor.on_end] Span {readable_span.name} already processed, skipping")
            return
        
        # Mark as processed - add to both deque and set
        self._processed_spans_deque.append(span_context_id)
        self._processed_spans_set.add(span_context_id)
        
        # Clean up set when deque evicts old items (deque auto-evicts at maxlen)
        if len(self._processed_spans_set) > len(self._processed_spans_deque):
            # Rebuild set from deque to match current LRU state
            self._processed_spans_set = set(self._processed_spans_deque)
        
        if self.debug_enabled:
            print(f"\n{'='*80}")
            print(f"[ModelFixProcessor.on_end] Processing span: {readable_span.name}")
            print(f"{'='*80}\n")
        
        logger.debug(f"on_end called for span: {readable_span.name}")
        
        attributes = dict(readable_span.attributes or {})
        request_model_attr = attributes.get("gen_ai.request.model")
        response_model_attr = attributes.get("gen_ai.response.model")
        system_attr = attributes.get("gen_ai.provider.name") if "gen_ai.provider.name" in attributes else attributes.get("gen_ai.system")

        if self.debug_enabled:
            print(f"[ModelFixProcessor] BEFORE: request={request_model_attr}, response={response_model_attr}, system={system_attr}")
        
        logger.debug(f"Attributes before fixes: request_model={request_model_attr}, response_model={response_model_attr}, system={system_attr}")
        
        # Get correct values from various sources
        correct_model_name = self._get_correct_model_name(attributes, readable_span.name)
        correct_system = self._get_correct_system(attributes, readable_span.name)
        
        # Apply fixes
        self._apply_attribute_fixes(
            readable_span=readable_span,
            span_name=readable_span.name,
            system_attr=system_attr,
            correct_system=correct_system,
            request_model_attr=request_model_attr,
            response_model_attr=response_model_attr,
            correct_model_name=correct_model_name,
        )
        
        if self.debug_enabled:
            final_attrs = self._get_target_attributes(readable_span)
            if final_attrs:
                print(f"[ModelFixProcessor] AFTER: request={final_attrs.get('gen_ai.request.model')}, response={final_attrs.get('gen_ai.response.model')}, system={final_attrs.get('gen_ai.system')}")
            print(f"{'='*80}\n")
    
    def _get_correct_model_name(self, attributes: dict, span_name: str) -> Optional[str]:
        """
        Get the correct model name from various attribute sources.
        
        Returns the full model identifier to preserve regional and version information.
        
        Args:
            attributes: Dictionary of span attributes
            span_name: Name of the span
            
        Returns:
            The correct model name if found, None otherwise
        """
        # For Bedrock spans, prioritize request model since response model is often missing
        if _is_bedrock_span(span_name):
            request_model = attributes.get("gen_ai.request.model")
            if request_model and not _is_invalid_model(request_model):
                return request_model
        
        # For other spans, try to get from standard response model if it's valid
        response_model = attributes.get("gen_ai.response.model")
        if response_model and not _is_invalid_model(response_model):
            return response_model
        
        # For Ollama spans, check the traceloop association properties
        if _is_ollama_span(span_name):
            ls_model_name = attributes.get("traceloop.association.properties.ls_model_name")
            if ls_model_name:
                return ls_model_name
            
        return None


    def _get_correct_system(self, attributes: dict, span_name: str) -> Optional[str]:
        """
        Get the correct gen_ai.system value based on span characteristics.
        
        Args:
            attributes: Dictionary of span attributes
            span_name: Name of the span
            
        Returns:
            The correct system value if determinable, None otherwise
        """
        # For Azure OpenAI workflow spans (LlamaIndex Azure OpenAI)
        if span_name == "AzureOpenAI.workflow":
            return SYSTEM_AZURE
        
        # For Bedrock spans
        if _is_bedrock_span(span_name):
            return SYSTEM_AWS
            
        # For Ollama spans  
        if _is_ollama_span(span_name):
            return SYSTEM_OLLAMA
            
        # For OpenAI-compatible spans, use unified detection logic
        if span_name in ("openai.chat", "openai.response", "ChatOpenAI.chat", "Agent Workflow"):
            return self._detect_openai_compatible_system(attributes)
            
        # For other spans, try to infer from existing attributes
        return self._detect_openai_compatible_system(attributes)
    
    def _detect_openai_compatible_system(self, attributes: dict) -> Optional[str]:
        """
        Detect the correct system for OpenAI-compatible spans using endpoint and model name patterns.
        
        Args:
            attributes: Dictionary of span attributes
            
        Returns:
            The correct system value if determinable, None otherwise
        """
        # Try endpoint detection first
        _, is_azure, is_openrouter, is_ollama = _extract_endpoint_info(attributes)
        
        if is_azure:
            return SYSTEM_AZURE
        if is_openrouter:
            return SYSTEM_OPENROUTER
        if is_ollama:
            return SYSTEM_OLLAMA
            
        # If endpoint detection fails, try model name detection for OpenRouter
        request_model = attributes.get("gen_ai.request.model")
        response_model = attributes.get("gen_ai.response.model")
        llm_model_name = attributes.get("traceloop.association.properties.ls_model_name")
        
        if _is_openrouter_model(request_model) or _is_openrouter_model(response_model) or _is_openrouter_model(llm_model_name):
            return SYSTEM_OPENROUTER
            
        # Default to OpenAI for OpenAI-compatible spans
        return SYSTEM_OPENAI
    
    def _should_fix_request_model(self, span_name: str, request_model: Optional[str], response_model: Optional[str]) -> bool:
        """
        Determine whether we should fix the gen_ai.request.model attribute.
        
        Args:
            span_name: Name of the span
            request_model: Current gen_ai.request.model value
            response_model: Current gen_ai.response.model value
            
        Returns:
            True if we should fix the request model, False otherwise
        """
        # Always fix if request model is missing or unknown
        if _is_invalid_model(request_model):
            return True
            
        # For AzureOpenAI.workflow spans, be more aggressive about fixing request model
        # since the response model tends to be more accurate
        if span_name in ("AzureOpenAI.workflow", "Agent Workflow") and response_model:
            if response_model and request_model != response_model:
                return True
        
        return False
    
    def _fix_ollama_usage_attributes(self, attributes_dict: dict) -> None:
        """
        Fix missing Ollama token usage attributes by extracting from raw response attributes.
        
        Ollama responses include token counts in different attribute names:
        - prompt_eval_count → gen_ai.usage.input_tokens (and gen_ai.usage.prompt_tokens for backwards compatibility)
        - eval_count → gen_ai.usage.output_tokens (and gen_ai.usage.completion_tokens for backwards compatibility)
        - prompt_eval_count + eval_count → llm.usage.total_tokens
        
        Args:
            attributes_dict: Dictionary of span attributes to modify
        """
        try:
            # Prefer new attribute names; legacy names used only as fallback/presence indicator
            new_prompt_val = attributes_dict.get("gen_ai.usage.input_tokens")
            new_completion_val = attributes_dict.get("gen_ai.usage.output_tokens")
            legacy_prompt_present = "gen_ai.usage.prompt_tokens" in attributes_dict
            legacy_completion_present = "gen_ai.usage.completion_tokens" in attributes_dict
            has_total_tokens = attributes_dict.get("llm.usage.total_tokens") not in (None, "", 0)
            
            # Look for Ollama-specific attributes
            prompt_eval_count = attributes_dict.get("prompt_eval_count")
            eval_count = attributes_dict.get("eval_count")
            
            # Try to extract from traceloop entity output (JSON response data)
            if prompt_eval_count is None or eval_count is None:
                entity_output = attributes_dict.get("traceloop.entity.output")
                if entity_output and isinstance(entity_output, str):
                    prompt_eval_count, eval_count = self._extract_ollama_tokens_from_json(entity_output)
            
            if prompt_eval_count is not None and eval_count is not None:
                # Convert to integers
                prompt_eval_count = int(prompt_eval_count) if isinstance(prompt_eval_count, (str, int, float)) else 0
                eval_count = int(eval_count) if isinstance(eval_count, (str, int, float)) else 0
                
                # Fix missing standard attributes (set both old and new names for backwards compatibility)
                # Set new attributes when missing or falsy; only write legacy keys if they already exist
                if not new_prompt_val and prompt_eval_count > 0:
                    attributes_dict["gen_ai.usage.input_tokens"] = prompt_eval_count
                if legacy_prompt_present:
                    # update legacy key only if it already existed on the span
                    attributes_dict["gen_ai.usage.prompt_tokens"] = prompt_eval_count

                if not new_completion_val and eval_count > 0:
                    attributes_dict["gen_ai.usage.output_tokens"] = eval_count
                if legacy_completion_present:
                    attributes_dict["gen_ai.usage.completion_tokens"] = eval_count
                    
                if not has_total_tokens and (prompt_eval_count > 0 or eval_count > 0):
                    attributes_dict["llm.usage.total_tokens"] = prompt_eval_count + eval_count
                    
        except (ValueError, TypeError, AttributeError):
            pass

    def _fix_bedrock_usage_attributes(self, attributes_dict: dict) -> None:
        """
        Fix missing Bedrock token usage attributes by extracting from traceloop.entity.output.
        
        Bedrock responses include token counts in the raw.usage structure:
        - inputTokens → gen_ai.usage.input_tokens (and gen_ai.usage.prompt_tokens for backwards compatibility)
        - outputTokens → gen_ai.usage.output_tokens (and gen_ai.usage.completion_tokens for backwards compatibility)
        - totalTokens → llm.usage.total_tokens
        
        Args:
            attributes_dict: Dictionary of span attributes to modify
        """
        try:
            # Prefer new attribute names; legacy names used only as fallback/presence indicator
            new_prompt_val = attributes_dict.get("gen_ai.usage.input_tokens")
            new_completion_val = attributes_dict.get("gen_ai.usage.output_tokens")
            legacy_prompt_val = attributes_dict.get("gen_ai.usage.prompt_tokens")
            legacy_completion_val = attributes_dict.get("gen_ai.usage.completion_tokens")
            has_total_tokens = attributes_dict.get("llm.usage.total_tokens") not in (None, "", 0)
            
            # If all attributes are already present with valid values, no need to extract
            if (new_prompt_val or legacy_prompt_val) and (new_completion_val or legacy_completion_val) and has_total_tokens:
                return
            
            # Try to extract from traceloop entity output (JSON response data)
            entity_output = attributes_dict.get("traceloop.entity.output")
            if entity_output and isinstance(entity_output, str):
                prompt_tokens, completion_tokens, total_tokens = self._extract_bedrock_tokens_from_json(entity_output)
                
                if prompt_tokens is not None and completion_tokens is not None:
                    # Fix missing standard attributes: set new names first; set legacy keys only if they existed
                    if not new_prompt_val and prompt_tokens > 0:
                        attributes_dict["gen_ai.usage.input_tokens"] = prompt_tokens
                    if "gen_ai.usage.prompt_tokens" in attributes_dict:
                        attributes_dict["gen_ai.usage.prompt_tokens"] = prompt_tokens

                    if not new_completion_val and completion_tokens > 0:
                        attributes_dict["gen_ai.usage.output_tokens"] = completion_tokens
                    if "gen_ai.usage.completion_tokens" in attributes_dict:
                        attributes_dict["gen_ai.usage.completion_tokens"] = completion_tokens
                        
                    if not has_total_tokens:
                        if total_tokens is not None and total_tokens > 0:
                            attributes_dict["llm.usage.total_tokens"] = total_tokens
                        elif prompt_tokens > 0 or completion_tokens > 0:
                            attributes_dict["llm.usage.total_tokens"] = prompt_tokens + completion_tokens
                    
        except (ValueError, TypeError, AttributeError):
            pass

    
    def _extract_ollama_tokens_from_json(self, json_output: str) -> Tuple[Optional[int], Optional[int]]:
        """
        Extract prompt_eval_count and eval_count from Ollama JSON response in traceloop.entity.output.
        
        The JSON structure is expected to be:
        {"message": {...}, "raw": {"prompt_eval_count": X, "eval_count": Y, ...}}
        
        Args:
            json_output: JSON string from traceloop.entity.output
            
        Returns:
            Tuple of (prompt_eval_count, eval_count) or (None, None) if not found
        """
        try:
            import json
            data = json.loads(json_output)
            
            # Handle double-encoded JSON (data might be a JSON string)
            if isinstance(data, str):
                data = json.loads(data)
            
            # Use defensive extraction
            prompt_eval_count = self._safe_extract_nested(data, 'raw', 'prompt_eval_count')
            eval_count = self._safe_extract_nested(data, 'raw', 'eval_count')
            
            if prompt_eval_count is not None and eval_count is not None:
                return int(prompt_eval_count), int(eval_count)
                
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            if self.debug_enabled:
                logger.warning(f"Failed to extract Ollama tokens from JSON: {e}")
            
        return None, None

    def _extract_bedrock_tokens_from_json(self, json_output: str) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """
        Extract token usage from Bedrock JSON response in traceloop.entity.output.
        
        The JSON structure is expected to be:
        {"raw": {"usage": {"inputTokens": X, "outputTokens": Y, "totalTokens": Z, ...}}}
        or
        {"additional_kwargs": {"prompt_tokens": X, "completion_tokens": Y, "total_tokens": Z}}
        
        Args:
            json_output: JSON string from traceloop.entity.output
            
        Returns:
            Tuple of (prompt_tokens, completion_tokens, total_tokens) or (None, None, None) if not found
        """
        try:
            import json
            data = json.loads(json_output)
            
            # Handle double-encoded JSON (data might be a JSON string)
            if isinstance(data, str):
                data = json.loads(data)
            
            # Try to extract from raw.usage (Bedrock native format)
            input_tokens = self._safe_extract_nested(data, 'raw', 'usage', 'inputTokens')
            output_tokens = self._safe_extract_nested(data, 'raw', 'usage', 'outputTokens')
            total_tokens = self._safe_extract_nested(data, 'raw', 'usage', 'totalTokens')
            
            if input_tokens is not None and output_tokens is not None:
                return (
                    int(input_tokens),
                    int(output_tokens),
                    int(total_tokens) if total_tokens is not None else None
                )
            
            # Try to extract from additional_kwargs (alternative format)
            prompt_tokens = self._safe_extract_nested(data, 'additional_kwargs', 'prompt_tokens')
            completion_tokens = self._safe_extract_nested(data, 'additional_kwargs', 'completion_tokens')
            total_tokens_alt = self._safe_extract_nested(data, 'additional_kwargs', 'total_tokens')
            
            if prompt_tokens is not None and completion_tokens is not None:
                return (
                    int(prompt_tokens),
                    int(completion_tokens),
                    int(total_tokens_alt) if total_tokens_alt is not None else None
                )
                    
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            if self.debug_enabled:
                logger.warning(f"Failed to extract Bedrock tokens from JSON: {e}")
            
        return None, None, None

    # ---- Internal helper methods -------------------------------------------------

    def _safe_extract_nested(self, data: Any, *keys: str, default: Any = None) -> Any:
        """
        Safely extract a nested dictionary value using a sequence of keys.
        
        This helper provides defensive access to nested dictionary structures,
        commonly found in JSON responses from AI providers. It handles:
        - Missing keys gracefully
        - Non-dict intermediate values
        - Empty dict results
        
        Args:
            data: The root dictionary or data structure to extract from
            *keys: Variable number of keys to traverse (e.g., 'raw', 'usage', 'inputTokens')
            default: Value to return if extraction fails or result is empty. Defaults to None.
            
        Returns:
            The extracted value if found, otherwise the default value.
            
        Example:
            >>> data = {"raw": {"usage": {"inputTokens": 100}}}
            >>> self._safe_extract_nested(data, 'raw', 'usage', 'inputTokens')
            100
            >>> self._safe_extract_nested(data, 'raw', 'missing', 'key', default=0)
            0
        """
        result = data
        for key in keys:
            if not isinstance(result, dict):
                if self.debug_enabled:
                    logger.debug(f"_safe_extract_nested: Expected dict at key '{key}', got {type(result).__name__}")
                return default
            result = result.get(key)
            if result is None:
                if self.debug_enabled:
                    logger.debug(f"_safe_extract_nested: Key '{key}' not found in path {keys}")
                return default
        
        # Return default if result is empty dict
        if result == {}:
            return default
            
        return result

    def _get_target_attributes(self, readable_span: ReadableSpan) -> Optional[dict]:
        """
        Get the target attributes dictionary for modification.
        
        Args:
            readable_span: The span whose attributes we want to access
            
        Returns:
            Writable attributes dictionary if available, None otherwise
        """
        if hasattr(readable_span, '_attributes'):
            readable_span._attributes = readable_span._attributes or {}
            logger.debug(f"Got target attributes via _attributes, type={type(readable_span._attributes)}")
            return readable_span._attributes
        elif hasattr(readable_span, 'attributes') and isinstance(readable_span.attributes, dict):
            logger.warning("Using attributes property directly (may not persist changes)")
            return readable_span.attributes
        
        logger.error(f"Could not find writable attributes on span '{readable_span.name}'!")
        return None

    def _fix_system_attribute(self, target_attrs: dict, system_attr: Optional[str], correct_system: Optional[str]) -> None:
        """
        Fix the gen_ai.system and gen_ai.provider.name attributes if needed.
        
        Args:
            target_attrs: Dictionary of span attributes to modify
            system_attr: Current gen_ai.system or gen_ai.provider.name value
            correct_system: Correct system value to set
        """
        if correct_system and system_attr != correct_system:
            if self.debug_enabled:
                logger.debug(f"Fixing gen_ai.system/gen_ai.provider.name: '{system_attr}' -> '{correct_system}'")
            target_attrs["gen_ai.provider.name"] = correct_system
            if "gen_ai.system" in target_attrs:
                target_attrs["gen_ai.system"] = correct_system  # Backwards compatibility
            target_attrs["traceloop.association.properties.ls_provider"] = correct_system

    def _fix_model_attributes(
        self, 
        target_attrs: dict, 
        span_name: str,
        request_model_attr: Optional[str], 
        response_model_attr: Optional[str], 
        correct_model_name: Optional[str]
    ) -> None:
        """
        Fix the gen_ai.request.model and gen_ai.response.model attributes if needed.
        
        This method implements different strategies for different span types:
        - Bedrock spans: Use request model as source of truth (response often missing)
        - Other spans: Prefer response model, fall back to request or correct_model_name
        
        Args:
            target_attrs: Dictionary of span attributes to modify
            span_name: Name of the span being processed
            request_model_attr: Current gen_ai.request.model value
            response_model_attr: Current gen_ai.response.model value
            correct_model_name: Correct model name from alternative sources
        """
        
        # For Bedrock spans, always use request model as the source of truth
        if _is_bedrock_span(span_name):
            if request_model_attr and not _is_invalid_model(request_model_attr):
                # Keep the full model name to preserve regional and version information
                logger.debug(f"Bedrock span: using full model name {request_model_attr}")
                
                # Set both request and response model to the full model name
                target_attrs["gen_ai.request.model"] = request_model_attr
                target_attrs["gen_ai.response.model"] = request_model_attr
            else:
                logger.warning(f"Cannot set Bedrock model: request_model={request_model_attr}")
            return
        
        # For non-Bedrock spans, use existing logic
        final_request_model = None
        final_response_model = None
        
        # Check if we have valid models
        has_valid_request = not _is_invalid_model(request_model_attr)
        has_valid_response = not _is_invalid_model(response_model_attr)
        has_correct_model = correct_model_name is not None
        
        if has_valid_response and has_valid_request:
            # Both valid - prefer response model
            final_request_model = response_model_attr
            final_response_model = response_model_attr
        elif has_valid_response:
            # Only response is valid
            final_request_model = response_model_attr
            final_response_model = response_model_attr
        elif has_valid_request:
            # Only request is valid
            final_request_model = request_model_attr
            final_response_model = request_model_attr
        elif has_correct_model:
            # Neither is valid but we have correct_model_name
            final_request_model = correct_model_name
            final_response_model = correct_model_name
        
        # Apply fixes only if we determined new values and they differ from current
        if final_request_model and final_request_model != request_model_attr:
            if self._should_fix_request_model(span_name, request_model_attr, response_model_attr):
                if self.debug_enabled:
                    logger.debug(f"Fixing gen_ai.request.model: '{request_model_attr}' -> '{final_request_model}'")
                target_attrs["gen_ai.request.model"] = final_request_model
        
        if final_response_model and final_response_model != response_model_attr:
            if self.debug_enabled:
                logger.debug(f"Fixing gen_ai.response.model: '{response_model_attr}' -> '{final_response_model}'")
            target_attrs["gen_ai.response.model"] = final_response_model
    def _apply_attribute_fixes(
        self,
        *,
        readable_span: ReadableSpan,
        span_name: str,
        system_attr: Optional[str],
        correct_system: Optional[str],
        request_model_attr: Optional[str],
        response_model_attr: Optional[str],
        correct_model_name: Optional[str],
    ) -> None:
        """
        Apply system, model and token usage fixes to the span attributes.
        
        Args:
            readable_span: The span to fix
            span_name: Name of the span being processed
            system_attr: Current gen_ai.system value
            correct_system: Correct system value
            request_model_attr: Current request model value
            response_model_attr: Current response model value
            correct_model_name: Correct model name value
        """
        try:
            target_attrs = self._get_target_attributes(readable_span)
            if target_attrs is None:
                logger.warning(f"Cannot apply fixes to span '{span_name}': no writable attributes found")
                return

            self._fix_system_attribute(target_attrs, system_attr, correct_system)
            self._fix_model_attributes(target_attrs, span_name, request_model_attr, response_model_attr, correct_model_name)
            
            # Ollama usage metrics
            if _is_ollama_span(span_name):
                self._fix_ollama_usage_attributes(target_attrs)
            
            # Bedrock usage metrics
            if _is_bedrock_span(span_name):
                self._fix_bedrock_usage_attributes(target_attrs)
        except Exception as e:
            logger.error(f"ModelFixProcessor._apply_attribute_fixes failed for span '{span_name}': {e}", exc_info=self.debug_enabled)

    def shutdown(self) -> None:
        """
        Called when the processor is shut down.
        
        This is part of the SpanProcessor interface. Currently no cleanup is needed
        as the processor doesn't hold any resources that require explicit cleanup.
        """
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """
        Called to force flush any buffered spans.
        
        This is part of the SpanProcessor interface. Since this processor doesn't
        buffer spans (it processes them synchronously in on_end), this always returns True.
        
        Args:
            timeout_millis: Maximum time to wait for flush in milliseconds (unused)
            
        Returns:
            True indicating successful flush (no-op in this processor)
        """
        return True