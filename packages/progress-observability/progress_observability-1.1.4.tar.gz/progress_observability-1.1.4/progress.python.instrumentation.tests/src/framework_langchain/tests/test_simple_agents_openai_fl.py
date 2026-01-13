import pytest
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import AzureChatOpenAI


from test_utils.llm_span_helpers import (
    check_required_attributes,
    check_system_value,
    check_model_attributes,
    check_resource_validation,
    use_vcr_cassette
)

# Define the instrument fixture list once for reuse
INSTRUMENT_FIXTURES = [
    "instrument_auto",
    # "instrument_langchain",
    # "instrument_openai",
    # "instrument_langchain_openai",
]

# Fixture for LLM setup with parametrization
@pytest.fixture(scope="module", params=["gpt-4o-mini", "gpt-4o", "gpt-4.1-nano"])
def azure_llm(request):
    from os import getenv
    model = request.param
    llm = AzureChatOpenAI(
        deployment_name=model,
        api_key=getenv("AZURE_OPENAI_API_KEY"),
        api_version=getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=getenv("AZURE_OPENAI_ENDPOINT")
    )
    return llm

# Fixture for prompt and messages
@pytest.fixture(scope="module")
def agent_messages():
    system_prompt = "You are a helpful AI assistant. Provide clear, accurate, and concise answers to user questions."
    question = "What is the capital of France?"
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=question)
    ]
    return messages


def _run_and_get_span(request, instrument_fixture, azure_llm, agent_messages, span_exporter, vcr_config, cassette_path):
    instrument = request.getfixturevalue(instrument_fixture)
    model_name = azure_llm.deployment_name
    cassette_name = f"simple_agent_{model_name.replace(':', '-')}"
    
    with use_vcr_cassette(cassette_path, cassette_name, vcr_config):
        answer = azure_llm.invoke(agent_messages)
        assert "Paris" in answer.content
        spans = span_exporter.get_finished_spans()
        assert len(spans) == 1, f"Expected exactly one span, got {len(spans)}"
        return spans[0], model_name

@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_required_attributes(request, instrument_fixture, azure_llm, agent_messages, span_exporter, vcr_config, cassette_path):
    span, _ = _run_and_get_span(request, instrument_fixture, azure_llm, agent_messages, span_exporter, vcr_config, cassette_path)
    check_required_attributes(span)

@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_system_value(request, instrument_fixture, azure_llm, agent_messages, span_exporter, vcr_config, cassette_path):
    span, _ = _run_and_get_span(request, instrument_fixture, azure_llm, agent_messages, span_exporter, vcr_config, cassette_path)
    check_system_value(span)

@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_model_attributes(request, instrument_fixture, azure_llm, agent_messages, span_exporter, vcr_config, cassette_path):
    span, model_name = _run_and_get_span(request, instrument_fixture, azure_llm, agent_messages, span_exporter, vcr_config, cassette_path)
    check_model_attributes(span, model_name)

@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_resource_validation(request, instrument_fixture, azure_llm, agent_messages, span_exporter, vcr_config, cassette_path):
    span, _ = _run_and_get_span(request, instrument_fixture, azure_llm, agent_messages, span_exporter, vcr_config, cassette_path)
    check_resource_validation(span)


