from opentelemetry.sdk.trace import StatusCode
import vcr
import hashlib


# Cassette filename aliases - for shortening long model names in cassette filenames
CASSETTE_MODEL_ALIASES = {
    # Anthropic models
    "claude-sonnet-4-20250514": "cs4-0514",
    "us.anthropic.claude-sonnet-4-5-20250929-v1:0": "cs45-bedrock",
    "claude-3-5-sonnet-20241022": "cs35-1022",
    "anthropic.claude-sonnet-4-5-20250929-v1:0": "cs45-bedrock-alt",
    
    # OpenAI models
    "gpt-4o": "gpt4o",
    "gpt-4o-mini": "gpt4om",
    "gpt-4.1-nano": "gpt41n",
    
    # Ollama models
    "gemma2:2b": "gemma2-2b",
    "qwen2.5:3b": "qwen25-3b",
}


def shorten_model_name(model_name):
    """
    Shorten model names for cassette filenames while preserving information.
    Uses predefined aliases or generates a short version for unknown models.
    
    Args:
        model_name: Full model name (e.g., "claude-sonnet-4-20250514")
    
    Returns:
        Shortened model name (e.g., "cs4-0514")
    
    Examples:
        >>> shorten_model_name("claude-sonnet-4-20250514")
        "cs4-0514"
        >>> shorten_model_name("us.anthropic.claude-sonnet-4-5-20250929-v1:0")
        "cs45-bedrock"
    """
    # Check if we have a predefined alias
    if model_name in CASSETTE_MODEL_ALIASES:
        return CASSETTE_MODEL_ALIASES[model_name]
    
    # For unknown models, create a readable short version
    # Remove common prefixes and suffixes
    clean_name = model_name.replace("us.anthropic.", "").replace("anthropic.", "")
    clean_name = clean_name.replace(":0", "").replace("-v1", "").replace(":", "-")
    
    # If still too long (> 20 chars), use first 15 chars + hash for uniqueness
    if len(clean_name) > 20:
        hash_suffix = hashlib.sha256(model_name.encode()).hexdigest()[:6]
        return f"{clean_name[:15]}-{hash_suffix}"
    
    return clean_name


def use_vcr_cassette(cassette_path, cassette_name, vcr_config, record_mode="once"):
    return vcr.use_cassette(
        str(cassette_path / f"{cassette_name}.yaml"),
        **vcr_config,
        record_mode=record_mode
    )

# New attributes with backwards compatibility checking
# Primary: "gen_ai.usage.input_tokens", "gen_ai.usage.output_tokens", "gen_ai.provider.name"
# Legacy: "gen_ai.usage.prompt_tokens", "gen_ai.usage.completion_tokens", "gen_ai.system"
REQUIRED_ATTRIBUTES = [
    "llm.request.type", 
    "gen_ai.response.model", "gen_ai.request.model",
    "llm.usage.total_tokens",
]
# Attributes that need at least one version (new or old) present
REQUIRED_EITHER_OR_ATTRIBUTES = [
    ("gen_ai.provider.name", "gen_ai.system"),
    ("gen_ai.usage.input_tokens", "gen_ai.usage.prompt_tokens"),
    ("gen_ai.usage.output_tokens", "gen_ai.usage.completion_tokens"),
]
REQUIRED_RESOURCE = "service.name"

# Small alias table for model name equivalences (request -> response form)
MODEL_ALIASES = {
    # Anthropic / Bedrock variant: full resource -> shortened model name returned by Bedrock
    "us.anthropic.claude-sonnet-4-5-20250929-v1:0": "claude-sonnet-4-5-20250929",
}
known_providers = {"Azure", "Ollama", "Anthropic", "AWS", "OpenAI", "OpenRouter"}


def get_llm_spans(spans):
    result = []
    for span in spans:
        attrs = span.attributes or {}
        if (
            attrs.get("gen_ai.provider.name") in known_providers
            or attrs.get("gen_ai.system") in known_providers
            or "gen_ai.request.model" in attrs
            or "gen_ai.response.model" in attrs
            or "gen_ai.usage.input_tokens" in attrs
            or "gen_ai.usage.output_tokens" in attrs
            or "gen_ai.usage.prompt_tokens" in attrs
            or "gen_ai.usage.completion_tokens" in attrs
            or "llm.usage.total_tokens" in attrs
        ):
            result.append(span)
    return result


def check_required_attributes(span):
    """Check that all required attributes are present and not None/empty"""
    missing = [
        attr for attr in REQUIRED_ATTRIBUTES
        if attr not in span.attributes or span.attributes[attr] in (None, "")
    ]
    assert not missing, f"Missing required attributes (present, not None, not empty): {missing} in span {span}"

    # Check either-or attributes (at least one of each pair must be present)
    for new_attr, old_attr in REQUIRED_EITHER_OR_ATTRIBUTES:
        has_new = new_attr in span.attributes and span.attributes[new_attr] not in (None, "")
        has_old = old_attr in span.attributes and span.attributes[old_attr] not in (None, "")
        assert has_new or has_old, f"Missing both '{new_attr}' and '{old_attr}' (need at least one) in span {span}"


def check_system_value(span):
    """Check that gen_ai.provider.name (or gen_ai.system for backwards compat) has a valid value and matches the provider context."""
    # Check for new attribute first, fall back to old one
    provider = span.attributes.get("gen_ai.provider.name") or span.attributes.get("gen_ai.system")

    assert provider is not None, "Neither gen_ai.provider.name nor gen_ai.system is set"

    assert provider in known_providers, f"Unexpected provider/system value: {provider}"

    # If provider/system is 'Ollama', that's authoritative (even if span name contains 'openai')
    if provider == "Ollama":
        return

    # If provider/system is 'Azure', span name should indicate Azure/OpenAI
    if provider == "Azure":
        assert (
            "openai" in span.name.lower() or "azure" in span.name.lower()
        ), f"Azure span should have 'openai' or 'azure' in name, got '{span.name}'"


def check_model_attributes(span, expected_model):
    """Check that model attributes are consistent and match expected model"""
    response_model = span.attributes.get("gen_ai.response.model")
    request_model = span.attributes.get("gen_ai.request.model")
    # Check for new attribute first, fall back to old one
    provider = span.attributes.get("gen_ai.provider.name") or span.attributes.get("gen_ai.system")

    if provider == "Azure":
        # For Azure, request model name should be contained in the response model
        assert request_model in response_model, f"Request model '{request_model}' should be contained in response model '{response_model}'"
    elif provider == "AWS":
        assert response_model in request_model, f"Response model '{response_model}' should be contained in request model '{request_model}'"
    else:
        assert response_model == request_model, f"Model mismatch: response={response_model}, request={request_model}"
    # Allow known aliases for expected_model (e.g., full resource -> shortened returned form)
    aliases = {expected_model}
    if expected_model in MODEL_ALIASES:
        aliases.add(MODEL_ALIASES[expected_model])
    # Also allow reverse mapping (response -> request)
    for k, v in MODEL_ALIASES.items():
        if v == expected_model:
            aliases.add(k)

    found = any(a in (response_model or "") or a in (request_model or "") for a in aliases)
    assert found, f"Expected model '{expected_model}' (aliases={aliases}) in response_model '{response_model}' or request_model '{request_model}'"

def check_resource_validation(span):
    """Check that span resource and metadata are valid"""
    assert hasattr(span, "resource") and hasattr(span.resource, "attributes"), "Span missing resource attributes"
    service_name = span.resource.attributes.get(REQUIRED_RESOURCE)
    assert service_name == "test", f"Expected service.name='test', got '{service_name}'"
    assert getattr(span, "start_time", 0) > 0, "Span should have start_time > 0"
    assert getattr(span, "end_time", 0) > 0, "Span should have end_time > 0"
    assert hasattr(span, "status") and span.status is not None, "Span should have status"
    valid_status_codes = {StatusCode.UNSET, StatusCode.OK, StatusCode.ERROR}
    assert span.status.status_code in valid_status_codes, f"Span status should be UNSET, OK, or ERROR, got {span.status.status_code}"

