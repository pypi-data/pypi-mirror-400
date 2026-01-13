"""
Tests for two-provider Haystack agents using Anthropic and Azure OpenAI.
Example: Using Haystack with different providers in sequence.
Provider 1 (Anthropic): Generates a question from a passage.
Provider 2 (Azure OpenAI): Answers the generated question.
"""
import os
import time
import pytest
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.components.generators.anthropic import AnthropicChatGenerator

# Haystack framework instrument fixtures
INSTRUMENT_FIXTURES = [
    "instrument_auto",
    # "instrument_haystack",
    # "instrument_openai",
    # "instrument_haystack_openai",
    # missing fixtures for Anthropic
]

from test_utils.llm_span_helpers import (
    check_required_attributes,
    check_system_value,
    check_model_attributes,
    check_resource_validation,
    get_llm_spans,
    use_vcr_cassette,
    shorten_model_name
)

# Test combinations of Anthropic and OpenAI models
ANTHROPIC_MODELS = ["claude-3-5-sonnet-20241022"]
OPENAI_MODELS = ["gpt-4o"]

def get_agent_data(anthropic_model, openai_model):
    passage = """
    The Amazon rainforest is the largest tropical rainforest in the world, covering over five and a half million square kilometers. It is home to an incredibly diverse range of species, many of which are not found anywhere else on Earth. The rainforest plays a critical role in regulating the global climate and is often referred to as the "lungs of the planet" because it produces about 20% of the world's oxygen.
    """
    return {
        "passage": passage,
        "expected_total_spans": 6,
        "expected_llm_spans": 2,
        "anthropic_model": anthropic_model,
        "openai_model": openai_model
    }


def _run_two_provider_agent(agent_data):
    """Run the two-provider agent and return responses and model names"""
    passage = agent_data["passage"]
    anthropic_model_name = agent_data["anthropic_model"]
    openai_model_name = agent_data["openai_model"]

    # Provider 1: Anthropic generates a question
    # Import the Anthropic Haystack generator if available; otherwise tests will be skipped by pytest.importorskip
   
    generator_anthropic = AnthropicChatGenerator(
        model=anthropic_model_name,
        api_key=Secret.from_env_var("ANTHROPIC_API_KEY"),
        generation_kwargs={"temperature": 0.1}
    )

    messages_1 = [
        ChatMessage.from_system("You are a helpful assistant. Read the passage and generate a challenging question about it."),
        ChatMessage.from_user(f"Passage: {passage}"),
    ]

    result_1 = generator_anthropic.run(messages=messages_1)
    # result structure mirrors Ollama generator (replies list)
    question = result_1["replies"][0].text if "replies" in result_1 and result_1["replies"] else None

    time.sleep(1)

    # Provider 2: Azure OpenAI answers the question
    generator_openai = pytest.importorskip("haystack.components.generators.chat", reason="Haystack OpenAI generator not available")
    AzureOpenAIChatGenerator = getattr(generator_openai, "AzureOpenAIChatGenerator", None)
    if AzureOpenAIChatGenerator is None:
        pytest.skip("AzureOpenAIChatGenerator not available in haystack.components.generators.chat")

    generator_openai = AzureOpenAIChatGenerator(
        azure_deployment=openai_model_name,
        api_key=Secret.from_env_var("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        generation_kwargs={"temperature": 0.1}
    )

    messages_2 = [
        ChatMessage.from_system("You are a knowledgeable assistant. Answer the following question based on the passage."),
        ChatMessage.from_user(f"Passage: {passage}\nQuestion: {question}"),
    ]

    result_2 = generator_openai.run(messages=messages_2)
    answer = result_2["replies"][0].text if "replies" in result_2 and result_2["replies"] else None

    return question, answer, [anthropic_model_name, openai_model_name]


def run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path):
    instrument = request.getfixturevalue(instrument_fixture)
    short_anthropic = shorten_model_name(agent_data['anthropic_model'])
    short_openai = shorten_model_name(agent_data['openai_model'])
    cassette_name = f"{instrument_fixture}-{short_anthropic}-{short_openai}"
    
    with use_vcr_cassette(cassette_path, cassette_name, vcr_config):
        question, answer, model_names = _run_two_provider_agent(agent_data)
        assert question and answer
        spans = span_exporter.get_finished_spans()
        assert spans, "No spans were created"
        llm_spans = get_llm_spans(spans)
        assert llm_spans, "No LLM spans were created"
        return llm_spans, model_names


@pytest.mark.parametrize("anthropic_model", ANTHROPIC_MODELS)
@pytest.mark.parametrize("openai_model", OPENAI_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_required_attributes(request, instrument_fixture, openai_model, anthropic_model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(anthropic_model, openai_model)
    llm_spans, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_required_attributes(span)


@pytest.mark.parametrize("anthropic_model", ANTHROPIC_MODELS)
@pytest.mark.parametrize("openai_model", OPENAI_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_system_value(request, instrument_fixture, openai_model, anthropic_model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(anthropic_model, openai_model)
    llm_spans, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_system_value(span)


@pytest.mark.parametrize("anthropic_model", ANTHROPIC_MODELS)
@pytest.mark.parametrize("openai_model", OPENAI_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_model_attributes(request, instrument_fixture, openai_model, anthropic_model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(anthropic_model, openai_model)
    llm_spans, model_names = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span, model_name in zip(llm_spans, model_names):
        check_model_attributes(span, model_name)


@pytest.mark.parametrize("anthropic_model", ANTHROPIC_MODELS)
@pytest.mark.parametrize("openai_model", OPENAI_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_resource_validation(request, instrument_fixture, openai_model, anthropic_model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(anthropic_model, openai_model)
    llm_spans, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_resource_validation(span)


@pytest.mark.parametrize("anthropic_model", ANTHROPIC_MODELS)
@pytest.mark.parametrize("openai_model", OPENAI_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_llm_span_count(request, instrument_fixture, openai_model, anthropic_model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(anthropic_model, openai_model)
    llm_spans, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    if instrument_fixture == "instrument_openai":
        expected_llm_spans = 1
    elif instrument_fixture == "instrument_anthropic":
        expected_llm_spans = 1
    else:
        expected_llm_spans = 2
    assert len(llm_spans) == expected_llm_spans, f"Expected {expected_llm_spans} LLM spans, got {len(llm_spans)}"
