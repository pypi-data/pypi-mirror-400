"""
Tests for two-provider OpenAI agents using Azure OpenAI and Ollama.
Example: Using both AzureOpenAI and OpenAI client with Ollama.
Provider 1 (Azure): Generates a question from a passage.
Provider 2 (Ollama): Answers the generated question.
"""
import os
import time
import pytest
from openai import AzureOpenAI, OpenAI
import vcr
from pathlib import Path

# OpenAI framework instrument fixtures
INSTRUMENT_FIXTURES = [
    "instrument_auto",
    # "instrument_openai",
    # "instrument_ollama",
    # "instrument_ollama_openai",
]

from test_utils.llm_span_helpers import (
    check_required_attributes,
    check_system_value,
    check_model_attributes,
    check_resource_validation,
    get_llm_spans,
    use_vcr_cassette
)

# Parametrize azure_model and ollama_model
PROVIDER_COMBINATIONS = [
    ("gpt-4o-mini", "gemma2:2b"),
]

def get_agent_data(azure_model, ollama_model):
    passage = """
    The Amazon rainforest is the largest tropical rainforest in the world, covering over five and a half million square kilometers. It is home to an incredibly diverse range of species, many of which are not found anywhere else on Earth. The rainforest plays a critical role in regulating the global climate and is often referred to as the "lungs of the planet" because it produces about 20% of the world's oxygen.
    """
    return {
        "passage": passage,
        "expected_total_spans": 6,
        "expected_llm_spans": 2,
        "azure_model": azure_model,
        "ollama_model": ollama_model
    }


def _run_two_provider_agent(agent_data):
    """Run the two-provider agent and return llm spans and model names"""
    passage = agent_data["passage"]
    azure_model = agent_data["azure_model"]
    ollama_model = agent_data["ollama_model"]

    # Create Azure OpenAI client
    azure_client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    # Create OpenAI client for Ollama
    ollama_client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    )

    # Provider 1 (Azure): Generate a question
    response_1 = azure_client.chat.completions.create(
        model=azure_model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Read the passage and generate a challenging question about it."},
            {"role": "user", "content": f"Passage: {passage}"}
        ],
        temperature=0.1
    )
    question = response_1.choices[0].message.content

    time.sleep(1)

    # Provider 2 (Ollama): Answer the question
    response_2 = ollama_client.chat.completions.create(
        model=ollama_model,
        messages=[
            {"role": "system", "content": "You are a knowledgeable assistant. Answer the following question based on the passage."},
            {"role": "user", "content": f"Passage: {passage}\nQuestion: {question}"}
        ],
        temperature=0.1
    )
    answer = response_2.choices[0].message.content

    return question, answer, [azure_model, ollama_model]


def run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path):
    instrument = request.getfixturevalue(instrument_fixture)
    cassette_name = f"{instrument_fixture}-{agent_data['azure_model'].replace(':', '-')}-{agent_data['ollama_model'].replace(':', '-')}"
    
    with use_vcr_cassette(cassette_path, cassette_name, vcr_config):
        question, answer, model_names = _run_two_provider_agent(agent_data)
        assert question and answer
        spans = span_exporter.get_finished_spans()
        assert spans, "No spans were created"
        llm_spans = get_llm_spans(spans)
        assert llm_spans, "No LLM spans were created"
        return llm_spans, model_names, agent_data


@pytest.mark.parametrize("azure_model,ollama_model", PROVIDER_COMBINATIONS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_required_attributes(request, instrument_fixture, azure_model, ollama_model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(azure_model, ollama_model)
    llm_spans, _, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_required_attributes(span)


@pytest.mark.parametrize("azure_model,ollama_model", PROVIDER_COMBINATIONS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_system_value(request, instrument_fixture, azure_model, ollama_model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(azure_model, ollama_model)
    llm_spans, _, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_system_value(span)


@pytest.mark.parametrize("azure_model,ollama_model", PROVIDER_COMBINATIONS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_model_attributes(request, instrument_fixture, azure_model, ollama_model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(azure_model, ollama_model)
    llm_spans, model_names, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span, model_name in zip(llm_spans, model_names):
        check_model_attributes(span, model_name)


@pytest.mark.parametrize("azure_model,ollama_model", PROVIDER_COMBINATIONS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_resource_validation(request, instrument_fixture, azure_model, ollama_model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(azure_model, ollama_model)
    llm_spans, _, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_resource_validation(span)


@pytest.mark.parametrize("azure_model,ollama_model", PROVIDER_COMBINATIONS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_llm_span_count(request, instrument_fixture, azure_model, ollama_model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(azure_model, ollama_model)
    llm_spans, _, agent_data = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    if instrument_fixture == "instrument_openai":
        expected_llm_spans = 1
    elif instrument_fixture == "instrument_ollama":
        expected_llm_spans = 1
    else:
        expected_llm_spans = 2
    assert len(llm_spans) == expected_llm_spans, f"Expected {expected_llm_spans} LLM spans, got {len(llm_spans)}"
