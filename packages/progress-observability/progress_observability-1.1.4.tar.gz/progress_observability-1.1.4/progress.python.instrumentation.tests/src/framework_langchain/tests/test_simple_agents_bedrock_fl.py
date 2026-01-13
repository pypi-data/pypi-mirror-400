import pytest
from dotenv import load_dotenv
load_dotenv() 

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_aws import ChatBedrockConverse

from test_utils.llm_span_helpers import (
    check_required_attributes,
    check_system_value,
    check_model_attributes,
    check_resource_validation,
    use_vcr_cassette,
    shorten_model_name,
)

# Define the instrument fixture list once for reuse
INSTRUMENT_FIXTURES = [
    "instrument_auto",
    # "instrument_langchain",
]

@pytest.fixture(scope="module", params=["us.anthropic.claude-sonnet-4-5-20250929-v1:0"])
def bedrock_llm(request):
    model = request.param
    llm = ChatBedrockConverse(
        model=model,
        temperature=0,
        max_tokens=None,
    )
    return llm
    

@pytest.fixture(scope="module")
def agent_messages():
    system_prompt = "You are a helpful AI assistant. Provide clear, accurate, and concise answers to user questions."
    question = "What is the capital of France?"
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=question),
    ]
    return messages


def _run_and_get_span(request, instrument_fixture, bedrock_llm, agent_messages, span_exporter, vcr_config, cassette_path):
    instrument = request.getfixturevalue(instrument_fixture)
    model_name = bedrock_llm.model_id
    short_model = shorten_model_name(model_name)
    cassette_name = f"simple_agent_{short_model}"

    with use_vcr_cassette(cassette_path, cassette_name, vcr_config):
        answer = bedrock_llm.invoke(agent_messages)
        assert answer is not None
        assert isinstance(answer.content, str)
        spans = span_exporter.get_finished_spans()
        assert len(spans) == 1, f"Expected exactly one span, got {len(spans)}"
        return spans[0], model_name


@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_required_attributes(request, instrument_fixture, bedrock_llm, agent_messages, span_exporter, vcr_config, cassette_path):
    span, _ = _run_and_get_span(request, instrument_fixture, bedrock_llm, agent_messages, span_exporter, vcr_config, cassette_path)
    check_required_attributes(span)


@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_system_value(request, instrument_fixture, bedrock_llm, agent_messages, span_exporter, vcr_config, cassette_path):
    span, _ = _run_and_get_span(request, instrument_fixture, bedrock_llm, agent_messages, span_exporter, vcr_config, cassette_path)
    check_system_value(span)


@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_model_attributes(request, instrument_fixture, bedrock_llm, agent_messages, span_exporter, vcr_config, cassette_path):
    span, model_name = _run_and_get_span(request, instrument_fixture, bedrock_llm, agent_messages, span_exporter, vcr_config, cassette_path)
    check_model_attributes(span, model_name)


@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_resource_validation(request, instrument_fixture, bedrock_llm, agent_messages, span_exporter, vcr_config, cassette_path):
    span, _ = _run_and_get_span(request, instrument_fixture, bedrock_llm, agent_messages, span_exporter, vcr_config, cassette_path)
    check_resource_validation(span)
