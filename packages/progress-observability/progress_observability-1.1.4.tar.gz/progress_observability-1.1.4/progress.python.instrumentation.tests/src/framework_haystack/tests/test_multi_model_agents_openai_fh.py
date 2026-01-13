"""
Tests for multi-model Haystack agents using different Azure OpenAI deployments.
Example: Using Haystack with two different Azure deployments in sequence.
Model 1: Generates a question from a passage.
Model 2: Answers the generated question.
"""
import os
import time
import pytest
from haystack.components.generators.chat import AzureOpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
import vcr
from pathlib import Path

from test_utils.llm_span_helpers import (
    check_required_attributes,
    check_system_value,
    check_model_attributes,
    check_resource_validation,
    get_llm_spans,
    use_vcr_cassette
)

# Haystack framework instrument fixtures
INSTRUMENT_FIXTURES = [
    "instrument_auto",
    # "instrument_haystack",
    # "instrument_openai",
    # "instrument_haystack_openai",
]


MODEL_COMBINATIONS = [
    ("gpt-4o", "gpt-4o-mini"),
    ("gpt-4.1-nano", "gpt-4o-mini"),
]

def get_agent_data(model_1, model_2):
    passage = """
    Artificial intelligence (AI) is rapidly transforming industries by enabling machines to perform tasks that typically require human intelligence. AI technologies such as machine learning, natural language processing, and computer vision are being used in healthcare, finance, transportation, and many other fields. These advancements allow for improved diagnostics, personalized recommendations, autonomous vehicles, and enhanced decision-making. However, the rise of AI also brings challenges, including ethical concerns, job displacement, and the need for robust regulatory frameworks. As AI continues to evolve, it is expected to play an increasingly important role in shaping the future of society.
    """
    return {
        "passage": passage,
        "expected_llm_spans": 2,
        "model_1": model_1,
        "model_2": model_2
    }


def _run_multi_model_agent(agent_data):
    """Run the multi-model agent and return llm spans and model names"""
    passage = agent_data["passage"]
    model_1_name = agent_data["model_1"]
    model_2_name = agent_data["model_2"]

    api_key = Secret.from_env_var("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

    # Model 1: Generate a question
    generator_1 = AzureOpenAIChatGenerator(
        azure_deployment=model_1_name,
        api_key=api_key,
        azure_endpoint=azure_endpoint,
        api_version=api_version,
        generation_kwargs={"temperature": 0.1}
    )
    
    messages_1 = [
        ChatMessage.from_system("You are a helpful assistant. Read the passage and generate a challenging question about it."),
        ChatMessage.from_user(f"Passage: {passage}")
    ]
    
    result_1 = generator_1.run(messages=messages_1)
    question = result_1["replies"][0].text

    time.sleep(1)

    # Model 2: Answer the question
    generator_2 = AzureOpenAIChatGenerator(
        azure_deployment=model_2_name,
        api_key=api_key,
        azure_endpoint=azure_endpoint,
        api_version=api_version,
        generation_kwargs={"temperature": 0.1}
    )
    
    messages_2 = [
        ChatMessage.from_system("You are a knowledgeable assistant. Answer the following question based on the passage."),
        ChatMessage.from_user(f"Passage: {passage}\n\nQuestion: {question}")
    ]
    
    result_2 = generator_2.run(messages=messages_2)
    answer = result_2["replies"][0].text

    return question, answer, [model_1_name, model_2_name]


def run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path):
    instrument = request.getfixturevalue(instrument_fixture)
    cassette_name = f"{instrument_fixture}-{agent_data['model_1'].replace(':', '-')}-{agent_data['model_2'].replace(':', '-')}"
    
    with use_vcr_cassette(cassette_path, cassette_name, vcr_config):
        question, answer, model_names = _run_multi_model_agent(agent_data)
        assert question and answer
        spans = span_exporter.get_finished_spans()
        assert spans, "No spans were created"
        llm_spans = get_llm_spans(spans)
        assert llm_spans, "No LLM spans were created"
        return llm_spans, model_names, agent_data


@pytest.mark.parametrize("model_1,model_2", MODEL_COMBINATIONS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_multi_model_agent_required_attributes(request, instrument_fixture, model_1, model_2, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(model_1, model_2)
    llm_spans, _, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_required_attributes(span)


@pytest.mark.parametrize("model_1,model_2", MODEL_COMBINATIONS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_multi_model_agent_system_value(request, instrument_fixture, model_1, model_2, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(model_1, model_2)
    llm_spans, _, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_system_value(span)


@pytest.mark.parametrize("model_1,model_2", MODEL_COMBINATIONS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_multi_model_agent_model_attributes(request, instrument_fixture, model_1, model_2, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(model_1, model_2)
    llm_spans, model_names, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span, model_name in zip(llm_spans, model_names):
        check_model_attributes(span, model_name)


@pytest.mark.parametrize("model_1,model_2", MODEL_COMBINATIONS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_multi_model_agent_resource_validation(request, instrument_fixture, model_1, model_2, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(model_1, model_2)
    llm_spans, _, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_resource_validation(span)


@pytest.mark.parametrize("model_1,model_2", MODEL_COMBINATIONS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_multi_model_agent_llm_span_count(request, instrument_fixture, model_1, model_2, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(model_1, model_2)
    llm_spans, _, agent_data = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    assert len(llm_spans) == agent_data["expected_llm_spans"], f"Expected {agent_data['expected_llm_spans']} LLM spans, got {len(llm_spans)}"
