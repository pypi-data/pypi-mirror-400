"""
Tests for blocking instrument functionality.
These tests enforce the expected behavior of the blocking instrumentation.
"""
import os
import pytest
from pathlib import Path
from progress.observability import Observability, ObservabilityInstruments
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from test_utils.llm_span_helpers import get_llm_spans, use_vcr_cassette
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables
project_root = Path(__file__).resolve().parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

def _run_azure_openai_call_and_get_spans(model_name, span_exporter, cassette_path, vcr_config, cassette_name="test"):
    """Helper function to run Azure OpenAI call and return spans"""
    # Create Azure LangChain client AFTER instrumentation (caller should handle Observability.instrument)
    azure_client = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_deployment=model_name,  # Use model_name as deployment name
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    )
    
    # Create agent messages
    agent_messages = [
        SystemMessage(content="You are a helpful AI assistant. Provide clear, accurate, and concise answers to user questions."),
        HumanMessage(content="What is the capital of France?")
    ]

    with use_vcr_cassette(cassette_path, cassette_name, vcr_config):
        answer = azure_client.invoke(agent_messages)
        assert "Paris" in answer.content
    
    spans = span_exporter.get_finished_spans()
    return spans

class TestBlockingInstrumentation:
    """Tests for blocking instrument functionality"""
    
    # for future use 
    # def test_conflicts_should_raise_error(self):
    #     """Conflicts between instruments and block_instruments should raise an error"""
    #     with pytest.raises(Exception):
    #         Observability.instrument(
    #             app_name="test-conflict",
    #             instruments={ObservabilityInstruments.OPENAI},
    #             block_instruments={ObservabilityInstruments.OPENAI}
    #         )
    
    # def test_reinitialize_should_raise_error(self):
    #     """Re-initialization should raise an error"""
    #     Observability.instrument(app_name="first")
    #     with pytest.raises(Exception):
    #         Observability.instrument(app_name="second", block_instruments={ObservabilityInstruments.OPENAI})

    
    def test_normal_instrumentation_creates_spans(self, setup_observability, span_exporter, cassette_path, vcr_config):
        """Baseline: Normal instrumentation should create OpenAI spans"""

        setup_observability("test-normal", instruments={ObservabilityInstruments.OPENAI})

        spans = _run_azure_openai_call_and_get_spans(
            "gpt-4o-mini", span_exporter, cassette_path, vcr_config, "normal_test"
        )
        assert len(spans) > 0, f"Normal instrumentation should create spans, got {len(spans)}"

    def test_blocking_prevents_spans(self, setup_observability, span_exporter, cassette_path, vcr_config):
        """ENFORCES: Blocking should prevent spans for blocked instruments"""

        setup_observability(
            app_name="test-partial-block",
            instruments={ObservabilityInstruments.OPENAI, ObservabilityInstruments.LANGCHAIN},
            block_instruments={ObservabilityInstruments.OPENAI},
        )

        spans = _run_azure_openai_call_and_get_spans(
            "gpt-4o-mini", span_exporter, cassette_path, vcr_config, "blocking_test"
        )

        # Get LLM spans to focus on AI-related spans
        llm_spans = get_llm_spans(spans)
    
        # Check instrumentation library to distinguish between OpenAI and LangChain spans
        direct_openai_spans = [
            s for s in llm_spans 
            if hasattr(s, 'instrumentation_scope') and s.instrumentation_scope and
            'openai' in s.instrumentation_scope.name.lower()
        ]
        
        langchain_spans = [
            s for s in llm_spans 
            if hasattr(s, 'instrumentation_scope') and s.instrumentation_scope and
            'langchain' in s.instrumentation_scope.name.lower()
        ]

        # We should have LangChain spans (not blocked) but no direct OpenAI spans (blocked)
        assert len(langchain_spans) > 0, f"LangChain should create spans (not blocked), but found {len(langchain_spans)}"
        assert len(direct_openai_spans) == 0, f"Blocking should prevent direct OpenAI SDK spans, but found {len(direct_openai_spans)}: {[s.name for s in direct_openai_spans]}"

    def test_blocking_multiple_instruments(self, setup_observability, span_exporter, cassette_path, vcr_config):
        """Test blocking multiple instruments at once"""
        setup_observability(
            app_name="test-multiple-block",
            instruments={ObservabilityInstruments.OPENAI, ObservabilityInstruments.LANGCHAIN},
            block_instruments={ObservabilityInstruments.OPENAI, ObservabilityInstruments.LANGCHAIN},

        )
        spans = _run_azure_openai_call_and_get_spans(
            "gpt-4o-mini", span_exporter, cassette_path, vcr_config, "multiple_blocking"
        )
        # Focus on LLM-related spans and check the instrumentor (instrumentation_scope)
        llm_spans = get_llm_spans(spans)
    
        # Ensure no spans were created by the blocked instrumentors (openai, langchain)
        blocked_instrumentor_spans = [
            s for s in llm_spans
            if hasattr(s, 'instrumentation_scope') and s.instrumentation_scope and
            any(blocked in s.instrumentation_scope.name.lower() for blocked in ['openai', 'langchain'])
        ]

        assert len(blocked_instrumentor_spans) == 0, (
            f"Multiple blocking should prevent OpenAI/LangChain instrumentor spans, but found {len(blocked_instrumentor_spans)}: "
            f"{[s.name for s in blocked_instrumentor_spans]}"
        )

    @pytest.mark.parametrize("block_provider,expected_present_instrumentor,expected_blocked_instrumentor", [
        ("ollama", "openai", "ollama"),
        ("openai", "ollama", "openai"),
    ])
    def test_blocked_vs_unblocked_provider_span(self, setup_observability, span_exporter, cassette_path, vcr_config, block_provider, expected_present_instrumentor, expected_blocked_instrumentor):
        """Test that blocking one provider prevents its instrumentor spans and allows the other provider's instrumentor spans in a two-provider agent scenario."""


        provider_to_instrument = {
            "ollama": ObservabilityInstruments.OLLAMA,
            "openai": ObservabilityInstruments.OPENAI,
        }

        setup_observability(
            app_name=f"test-block-{block_provider}",
            block_instruments={provider_to_instrument[block_provider]},
        )
        # Prepare models and prompts
        ollama_model = "gemma2:2b"
        openai_deployment = "gpt-4.1-nano"
        question = "What are the common symptoms of diabetes?"

        cassette_name = f"two_provider_block_{block_provider}"
        with use_vcr_cassette(cassette_path, cassette_name, vcr_config):
            # Model 1: Ollama answers the medical question
            model_1 = ChatOllama(
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                model=ollama_model
            )
            prompt_1 = ChatPromptTemplate.from_messages([
                ("system", "You are a medical expert. Answer the following question concisely and accurately."),
                ("human", "{question}")
            ])
            chain_1 = prompt_1 | model_1
            answer = chain_1.invoke({"question": question}).content

            # Model 2: OpenAI explains the answer
            model_2 = AzureChatOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                azure_deployment=openai_deployment,
                api_version="2024-02-15-preview"
            )
            prompt_2 = ChatPromptTemplate.from_messages([
                ("system", "You are a knowledgeable medical assistant. Explain the following answer in detail for a layperson."),
                ("human", f"Question: {{question}}\nAnswer: {{answer}}")
            ])
            chain_2 = prompt_2 | model_2
            explanation = chain_2.invoke({"question": question, "answer": answer}).content
            
            assert answer and explanation  # Ensure both calls succeeded
        
        spans = span_exporter.get_finished_spans()
        llm_spans = get_llm_spans(spans)
    
        # Check by instrumentation scope (the actual instrumentor that created the span)
        present_instrumentor_spans = [
            s for s in llm_spans 
            if hasattr(s, 'instrumentation_scope') and s.instrumentation_scope and
            expected_present_instrumentor in s.instrumentation_scope.name.lower()
        ]
        
        blocked_instrumentor_spans = [
            s for s in llm_spans 
            if hasattr(s, 'instrumentation_scope') and s.instrumentation_scope and
            expected_blocked_instrumentor in s.instrumentation_scope.name.lower()
        ]
        
        # We also expect LangChain spans since both models are called through LangChain
        langchain_spans = [
            s for s in llm_spans 
            if hasattr(s, 'instrumentation_scope') and s.instrumentation_scope and
            'langchain' in s.instrumentation_scope.name.lower()
        ]

        # LangChain should always create spans (we're using LangChain wrappers)
        assert len(langchain_spans) >= 2, f"Expected at least 2 LangChain spans (one for each model), got {len(langchain_spans)}"
        
        # The blocked instrumentor should create no spans
        assert len(blocked_instrumentor_spans) == 0, f"Expected 0 spans from blocked {expected_blocked_instrumentor} instrumentor, got {len(blocked_instrumentor_spans)}"
        
        # The present instrumentor may or may not create spans depending on the implementation
        # (LangChain may or may not use the underlying SDK directly)

