import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if ROOT not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "src"))
import pytest
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_anthropic import ChatAnthropic

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
]

# Fixture for LLM setup with parametrization
@pytest.fixture(scope="module", params=["claude-sonnet-4-20250514"])
def anthropic_llm(request):
    from os import getenv
    model = request.param
    llm = ChatAnthropic(
        model=model,
        api_key=getenv("ANTHROPIC_API_KEY"),
        max_tokens=1024,
        temperature=0.1
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


def _run_and_get_span(request, instrument_fixture, anthropic_llm, agent_messages, span_exporter, vcr_config, cassette_path):
    instrument = request.getfixturevalue(instrument_fixture)
    model_name = anthropic_llm.model
    cassette_name = f"simple_agent_{model_name.replace(':', '-')}"
    
    with use_vcr_cassette(cassette_path, cassette_name, vcr_config):
        answer = anthropic_llm.invoke(agent_messages)
        assert "Paris" in answer.content
        spans = span_exporter.get_finished_spans()
        assert len(spans) == 1, f"Expected exactly one span, got {len(spans)}"
        return spans[0], model_name

@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_required_attributes(request, instrument_fixture, anthropic_llm, agent_messages, span_exporter, vcr_config, cassette_path):
    span, _ = _run_and_get_span(request, instrument_fixture, anthropic_llm, agent_messages, span_exporter, vcr_config, cassette_path)
    check_required_attributes(span)

@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_system_value(request, instrument_fixture, anthropic_llm, agent_messages, span_exporter, vcr_config, cassette_path):
    span, _ = _run_and_get_span(request, instrument_fixture, anthropic_llm, agent_messages, span_exporter, vcr_config, cassette_path)
    check_system_value(span)

@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_model_attributes(request, instrument_fixture, anthropic_llm, agent_messages, span_exporter, vcr_config, cassette_path):
    span, model_name = _run_and_get_span(request, instrument_fixture, anthropic_llm, agent_messages, span_exporter, vcr_config, cassette_path)
    check_model_attributes(span, model_name)

@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_resource_validation(request, instrument_fixture, anthropic_llm, agent_messages, span_exporter, vcr_config, cassette_path):
    span, _ = _run_and_get_span(request, instrument_fixture, anthropic_llm, agent_messages, span_exporter, vcr_config, cassette_path)
    check_resource_validation(span)


if __name__ == "__main__":
    from progress.observability import Observability
    from dotenv import load_dotenv
    from os import getenv
    load_dotenv()

    AGENT_CLARITY_ENDPOINT = getenv("AGENT_CLARITY_ENDPOINT")
    AGENT_CLARITY_API_KEY = getenv("AGENT_CLARITY_API_KEY")

    Observability.instrument(
        app_name="langchain_simple_agent_anthropic_auto_python",
        endpoint=AGENT_CLARITY_ENDPOINT,
        api_key=AGENT_CLARITY_API_KEY,
    )

    # Create the LLM and messages
    model = "claude-3-5-sonnet-20241022"
    llm = ChatAnthropic(
        model=model,
        api_key=getenv("ANTHROPIC_API_KEY"),
        max_tokens=1024,
        temperature=0.1
    )       

    system_prompt = "You are a helpful AI assistant. Provide clear, accurate, and concise answers to user questions."
    question = "What is the capital of France?"
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=question)
    ]

    # Run the agent
    answer = llm.invoke(messages)
    print(f"Answer: {answer.content}")
