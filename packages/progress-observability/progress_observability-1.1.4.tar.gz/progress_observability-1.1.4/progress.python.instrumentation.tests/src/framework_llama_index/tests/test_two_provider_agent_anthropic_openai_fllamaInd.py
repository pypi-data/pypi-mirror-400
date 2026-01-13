"""
Tests for two-provider LlamaIndex agents using Anthropic and Azure OpenAI.
Provider 1 (Anthropic): Generates a question from a passage.
Provider 2 (Azure OpenAI): Answers the generated question.
"""
import os
import time
import pytest
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core.llms import ChatMessage

# Only auto instrumentation by default; legacy fixtures commented for future use
INSTRUMENT_FIXTURES = [
    "instrument_auto",
    # "instrument_openai",
    # "instrument_anthropic",
    # "instrument_llama_index",
    # "instrument_llama_index_openai",
    # "instrument_anthropic_llama_index",
    # "instrument_anthropic_openai",
    # "instrument_anthropic_openai_llama_index",
]

from test_utils.llm_span_helpers import (
    check_required_attributes,
    check_system_value,
    check_model_attributes,
    check_resource_validation,
    get_llm_spans,
    use_vcr_cassette,
    shorten_model_name,
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
    from os import getenv
    passage = agent_data["passage"]
    anthropic_model_name = agent_data["anthropic_model"]
    openai_model_name = agent_data["openai_model"]

    # Provider 1: Anthropic generates a question
    llm_anthropic = Anthropic(
        api_key=getenv("ANTHROPIC_API_KEY"),
        model=anthropic_model_name, 
        max_tokens=1024, 
        temperature=0.1)

    messages_1 = [
        ChatMessage(role="system", content="You are a helpful assistant. Read the passage and generate a challenging question about it."),
        ChatMessage(role="user", content=f"Passage: {passage}"),
    ]

    response_1 = llm_anthropic.chat(messages_1)
    question = response_1.message.content

    time.sleep(1)

    # Provider 2: Azure OpenAI answers the question
    llm_openai = AzureOpenAI(
        deployment_name=openai_model_name,
        api_key=getenv("AZURE_OPENAI_API_KEY"),
        api_version=getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=getenv("AZURE_OPENAI_ENDPOINT"),
        temperature=0.1,
    )

    messages_2 = [
        ChatMessage(role="system", content="You are a knowledgeable assistant. Answer the following question based on the passage."),
        ChatMessage(role="user", content=f"Passage: {passage}\nQuestion: {question}"),
    ]

    response_2 = llm_openai.chat(messages_2)
    answer = response_2.message.content

    return question, answer, [anthropic_model_name, openai_model_name]


def run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path):
    instrument = request.getfixturevalue(instrument_fixture)
    # Shorten model names for cassette filename
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
def test_two_provider_agent_required_attributes(request, instrument_fixture, anthropic_model, openai_model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(anthropic_model, openai_model)
    llm_spans, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_required_attributes(span)


@pytest.mark.parametrize("anthropic_model", ANTHROPIC_MODELS)
@pytest.mark.parametrize("openai_model", OPENAI_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_system_value(request, instrument_fixture, anthropic_model, openai_model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(anthropic_model, openai_model)
    llm_spans, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_system_value(span)


@pytest.mark.parametrize("anthropic_model", ANTHROPIC_MODELS)
@pytest.mark.parametrize("openai_model", OPENAI_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_model_attributes(request, instrument_fixture, anthropic_model, openai_model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(anthropic_model, openai_model)
    llm_spans, model_names = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span, model_name in zip(llm_spans, model_names):
        check_model_attributes(span, model_name)


@pytest.mark.parametrize("anthropic_model", ANTHROPIC_MODELS)
@pytest.mark.parametrize("openai_model", OPENAI_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_resource_validation(request, instrument_fixture, anthropic_model, openai_model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(anthropic_model, openai_model)
    llm_spans, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_resource_validation(span)


@pytest.mark.parametrize("anthropic_model", ANTHROPIC_MODELS)
@pytest.mark.parametrize("openai_model", OPENAI_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_llm_span_count(request, instrument_fixture, anthropic_model, openai_model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(anthropic_model, openai_model)
    llm_spans, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    if instrument_fixture == "instrument_openai":
        expected_llm_spans = 1
    elif instrument_fixture == "instrument_anthropic":
        expected_llm_spans = 1
    else:
        expected_llm_spans = 2
    assert len(llm_spans) == expected_llm_spans, f"Expected {expected_llm_spans} LLM spans, got {len(llm_spans)}"
