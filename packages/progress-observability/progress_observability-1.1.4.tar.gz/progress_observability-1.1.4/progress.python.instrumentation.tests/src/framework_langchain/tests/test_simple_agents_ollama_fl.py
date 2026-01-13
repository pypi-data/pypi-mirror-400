import pytest
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

from test_utils.llm_span_helpers import (
    check_required_attributes,
    check_system_value,
    check_model_attributes,
    check_resource_validation,
    use_vcr_cassette
)


# Default: only use auto instrumentation for new tests
INSTRUMENT_FIXTURES = [
    "instrument_auto",
    # "instrument_langchain",
    # "instrument_ollama",
    # "instrument_ollama_langchain",
]


@pytest.fixture(scope="module", params=["gemma2:2b", "qwen2.5:3b"])
def ollama_llm(request):
    from os import getenv
    model = request.param
    llm = ChatOllama(
        model=model,
        base_url=getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )
    return llm

@pytest.fixture(scope="module")
def agent_messages():
    system_prompt = "You are a helpful AI assistant. Provide clear, accurate, and concise answers to user questions."
    question = "What is the capital of France?"
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=question)
    ]
    return messages


def _run_and_get_span(request, instrument_fixture, ollama_llm, agent_messages, span_exporter, vcr_config, cassette_path):
    instrument = request.getfixturevalue(instrument_fixture)
    model_name = ollama_llm.model
    cassette_name = f"simple_agent_{model_name.replace(':', '-')}"
    
    with use_vcr_cassette(cassette_path, cassette_name, vcr_config):
        answer = ollama_llm.invoke(agent_messages)
        assert "Paris" in answer.content
        spans = span_exporter.get_finished_spans()
        assert len(spans) == 1, f"Expected exactly one span, got {len(spans)}"
        return spans[0], model_name

@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_required_attributes(request, instrument_fixture, ollama_llm, agent_messages, span_exporter, vcr_config, cassette_path):
    span, _ = _run_and_get_span(request, instrument_fixture, ollama_llm, agent_messages, span_exporter, vcr_config, cassette_path)
    check_required_attributes(span)

@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_system_value(request, instrument_fixture, ollama_llm, agent_messages, span_exporter, vcr_config, cassette_path):
    span, _ = _run_and_get_span(request, instrument_fixture, ollama_llm, agent_messages, span_exporter, vcr_config, cassette_path)
    check_system_value(span)

@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_model_attributes(request, instrument_fixture, ollama_llm, agent_messages, span_exporter, vcr_config, cassette_path):
    span, model_name = _run_and_get_span(request, instrument_fixture, ollama_llm, agent_messages, span_exporter, vcr_config, cassette_path)
    check_model_attributes(span, model_name)

@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_resource_validation(request, instrument_fixture, ollama_llm, agent_messages, span_exporter, vcr_config, cassette_path):
    span, _ = _run_and_get_span(request, instrument_fixture, ollama_llm, agent_messages, span_exporter, vcr_config, cassette_path)
    check_resource_validation(span)


