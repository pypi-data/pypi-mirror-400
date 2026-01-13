"""
Tests for simple LlamaIndex agents using Anthropic models.
Example: Simple question-answering using different Anthropic models.
"""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if ROOT not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "src"))
import pytest
from llama_index.llms.anthropic import Anthropic
from llama_index.core.llms import ChatMessage

# Only auto instrumentation by default; legacy fixtures commented for future use
INSTRUMENT_FIXTURES = [
    "instrument_auto",
    # "instrument_anthropic",
    # "instrument_llama_index",
    # "instrument_llama_index_anthropic",
]

from test_utils.llm_span_helpers import (
    check_required_attributes,
    check_system_value,
    check_model_attributes,
    check_resource_validation,
    get_llm_spans,
    use_vcr_cassette
)

# Test different Anthropic models
MODELS = [
    "claude-3-5-sonnet-20241022",
    "claude-3-5-haiku-20241022",
]

def get_agent_data(model):
    question = "What is the capital of France?"
    return {
        "question": question,
        "model": model,
        "expected_total_spans": 3,
        "expected_llm_spans": 1,
    }


def _run_simple_agent(agent_data):
    """Run the simple agent and return response"""
    from os import getenv
    question = agent_data["question"]
    model_name = agent_data["model"]

    # Create Anthropic LLM
    llm = Anthropic(
        api_key=getenv("ANTHROPIC_API_KEY"),
        model=model_name,
        max_tokens=1024,
        temperature=0.1
    )

    # Create chat messages
    messages = [
        ChatMessage(role="system", content="You are a helpful assistant."),
        ChatMessage(role="user", content=question),
    ]

    # Get response
    response = llm.chat(messages)
    return response.message.content, model_name


def run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path):
    instrument = request.getfixturevalue(instrument_fixture)
    cassette_name = f"simple_agent_{agent_data['model'].replace(':', '-')}"
    with use_vcr_cassette(cassette_path, cassette_name, vcr_config):
        response, model_name = _run_simple_agent(agent_data)
        assert response
        spans = span_exporter.get_finished_spans()
        assert spans, "No spans were created"
        llm_spans = get_llm_spans(spans)
        assert llm_spans, "No LLM spans were created"
        return llm_spans, model_name, agent_data


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_required_attributes(request, instrument_fixture, model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(model)
    llm_spans, _, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_required_attributes(span)


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_system_value(request, instrument_fixture, model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(model)
    llm_spans, _, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_system_value(span)


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_model_attributes(request, instrument_fixture, model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(model)
    llm_spans, model_name, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_model_attributes(span, model_name)


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_resource_validation(request, instrument_fixture, model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(model)
    llm_spans, _, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_resource_validation(span)


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_llm_span_count(request, instrument_fixture, model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(model)
    llm_spans, _, agent_data = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    assert len(llm_spans) == agent_data["expected_llm_spans"], f"Expected {agent_data['expected_llm_spans']} LLM spans, got {len(llm_spans)}"


if __name__ == "__main__":
    from progress.observability import Observability
    from dotenv import load_dotenv
    from os import getenv
    load_dotenv()

    AGENT_CLARITY_ENDPOINT = getenv("AGENT_CLARITY_ENDPOINT")
    AGENT_CLARITY_API_KEY = getenv("AGENT_CLARITY_API_KEY")

    Observability.instrument(
        app_name="llamaindex_simple_agent_anthropic_auto_python",
        endpoint=AGENT_CLARITY_ENDPOINT,
        api_key=AGENT_CLARITY_API_KEY,
        debug=True
    )
    agent_data = get_agent_data(MODELS[0])
    answer, _ = _run_simple_agent(agent_data)
    print(f"Answer: {answer}")
