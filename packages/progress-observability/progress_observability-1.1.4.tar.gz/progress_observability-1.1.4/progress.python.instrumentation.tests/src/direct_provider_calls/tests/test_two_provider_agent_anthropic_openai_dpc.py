"""
Tests for two-provider agents using Anthropic and Azure OpenAI (direct provider calls).
Provider 1 (Anthropic): Generates a question from a passage.
Provider 2 (Azure OpenAI): Answers the generated question.
"""
import os
import time
import pytest
from anthropic import Anthropic
from openai import AzureOpenAI
from dotenv import load_dotenv
load_dotenv()

# Instrument fixtures used for these direct-provider tests
INSTRUMENT_FIXTURES = [
    "instrument_auto",
    # "instrument_openai",
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

# Parametrize anthropic and azure models
PROVIDER_COMBINATIONS = [
    ("claude-sonnet-4-20250514", "gpt-4o"),
]


def get_agent_data(anthropic_model, azure_model):
    passage = """
    The Amazon rainforest is the largest tropical rainforest in the world, covering over five and a half million square kilometers. It is home to an incredibly diverse range of species, many of which are not found anywhere else on Earth. The rainforest plays a critical role in regulating the global climate and is often referred to as the "lungs of the planet" because it produces about 20% of the world's oxygen.
    """
    return {
        "passage": passage,
        "expected_total_spans": 6,
        "expected_llm_spans": 2,
        "anthropic_model": anthropic_model,
        "azure_model": azure_model
    }


def _run_two_provider_agent(agent_data):
    """Run the two-provider flow using Anthropic then Azure OpenAI and return outputs"""
    passage = agent_data["passage"]
    anthropic_model = agent_data["anthropic_model"]
    azure_model = agent_data["azure_model"]

    # Create Anthropic client
    anth_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), )

    # Provider 1 (Anthropic): Generate a question
    response_1 = anth_client.messages.create(
        model=anthropic_model,
        temperature=0.1,
        max_tokens=1000,
        system="You are a helpful assistant. Read the passage and generate a challenging question about it.",
        messages=[{"role": "user", "content": f"Passage: {passage}"}],
    )
    # Anthropic returns a 'content' field in the message; adapt for different client versions
    question = None
    if hasattr(response_1, "body") and isinstance(response_1.body, dict):
        # anthropic SDK v0.69+ may return body dict
        question = response_1.body.get("content") or response_1.body.get("text")
    else:
        # fallback to attribute access
        question = getattr(response_1, "content", None) or getattr(response_1, "text", None)

    time.sleep(1)

    # Provider 2 (Azure OpenAI): Answer the question
    azure_client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    response_2 = azure_client.chat.completions.create(
        model=azure_model,
        messages=[
            {"role": "system", "content": "You are a knowledgeable assistant. Answer the following question based on the passage."},
            {"role": "user", "content": f"Passage: {passage}\nQuestion: {question}"}
        ],
        temperature=0.1
    )
    answer = response_2.choices[0].message.content

    return question, answer, [anthropic_model, azure_model]


def run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path):
    instrument = request.getfixturevalue(instrument_fixture)
    short_anthropic = shorten_model_name(agent_data['anthropic_model'])
    short_azure = shorten_model_name(agent_data['azure_model'])
    cassette_name = f"{instrument_fixture}-{short_anthropic}-{short_azure}"
    with use_vcr_cassette(cassette_path, cassette_name, vcr_config):
        question, answer, model_names = _run_two_provider_agent(agent_data)
        assert question and answer
        spans = span_exporter.get_finished_spans()
        assert spans, "No spans were created"
        llm_spans = get_llm_spans(spans)
        assert llm_spans, "No LLM spans were created"
        return llm_spans, model_names, agent_data


@pytest.mark.parametrize("anthropic_model,azure_model", PROVIDER_COMBINATIONS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_required_attributes(request, instrument_fixture, anthropic_model, azure_model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(anthropic_model, azure_model)
    llm_spans, _, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_required_attributes(span)


@pytest.mark.parametrize("anthropic_model,azure_model", PROVIDER_COMBINATIONS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_system_value(request, instrument_fixture, anthropic_model, azure_model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(anthropic_model, azure_model)
    llm_spans, _, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_system_value(span)


@pytest.mark.parametrize("anthropic_model,azure_model", PROVIDER_COMBINATIONS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_model_attributes(request, instrument_fixture, anthropic_model, azure_model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(anthropic_model, azure_model)
    llm_spans, model_names, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span, model_name in zip(llm_spans, model_names):
        check_model_attributes(span, model_name)


@pytest.mark.parametrize("anthropic_model,azure_model", PROVIDER_COMBINATIONS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_resource_validation(request, instrument_fixture, anthropic_model, azure_model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(anthropic_model, azure_model)
    llm_spans, _, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_resource_validation(span)


@pytest.mark.parametrize("anthropic_model,azure_model", PROVIDER_COMBINATIONS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_llm_span_count(request, instrument_fixture, anthropic_model, azure_model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(anthropic_model, azure_model)
    llm_spans, _, agent_data = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    if instrument_fixture == "instrument_anthropic":
        expected_llm_spans = 1
    elif instrument_fixture == "instrument_openai":
        expected_llm_spans = 1
    else:
        expected_llm_spans = 2
    assert len(llm_spans) == expected_llm_spans, f"Expected {expected_llm_spans} LLM spans, got {len(llm_spans)}"
