"""
Tests for multi-model agent chains using different Azure OpenAI deployments.
Example: Using LangChain with OpenAI, chaining GPT-4o and GPT-4o-mini.
Model 1 (GPT-4o): Generates a question from a passage.
Model 2 (GPT-4o-mini): Answers the generated question.
"""
import time
import pytest
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


# Define the instrument fixture list once for reuse (like in simple agent tests)
INSTRUMENT_FIXTURES = [
    "instrument_auto",
    # "instrument_langchain",
    # "instrument_openai",
    # "instrument_langchain_openai",
]

from test_utils.llm_span_helpers import (
    check_required_attributes,
    check_system_value,
    check_model_attributes,
    check_resource_validation,
    get_llm_spans,
    use_vcr_cassette
)


# Parametrize model_1 and model_2 for all combinations
MODEL_COMBINATIONS = [
    ("gpt-4o", "gpt-4o-mini"),
    ("gpt-4.1-nano", "gpt-4o-mini"),
    # ("gpt-4o", "gpt-4.1-nano"),
    # ("gpt-4.1-nano", "gpt-4.1-nano"),
    # ("gpt-4o-mini", "gpt-4.1-nano"),
    # ("gpt-4.1-nano", "gpt-4o"),
    # ("gpt-4o-mini", "gpt-4o"),
    # ("gpt-4o-mini", "gpt-4o-mini"),
    # ("gpt-4o", "gpt-4o"),
]

def get_agent_data(model_1, model_2):
    passage = """
    The Amazon rainforest is the largest tropical rainforest in the world, covering over five and a half million square kilometers. It is home to an incredibly diverse range of species, many of which are not found anywhere else on Earth. The rainforest plays a critical role in regulating the global climate and is often referred to as the "lungs of the planet" because it produces about 20% of the world's oxygen.
    """
    return {
        "passage": passage,
        "expected_llm_spans": 2,
        "model_1": model_1,
        "model_2": model_2
    }


def _run_multi_model_agent(agent_data):
    """Run the multi-model agent and return llm spans and model names"""
    from os import getenv
    passage = agent_data["passage"]
    model_1_name = agent_data["model_1"]
    model_2_name = agent_data["model_2"]

    # Model 1: GPT-4o generates a question
    model_1 = AzureChatOpenAI(
        deployment_name=model_1_name,
        api_key=getenv("AZURE_OPENAI_API_KEY"),
        api_version=getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=getenv("AZURE_OPENAI_ENDPOINT")
    )
    prompt_1 = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Read the passage and generate a challenging question about it."),
        ("human", "Passage: {passage}")
    ])
    chain_1 = prompt_1 | model_1
    question = chain_1.invoke({"passage": passage}).content

    time.sleep(1)

    # Model 2: GPT-4o-mini answers the question
    model_2 = AzureChatOpenAI(
        deployment_name=model_2_name,
        api_key=getenv("AZURE_OPENAI_API_KEY"),
        api_version=getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=getenv("AZURE_OPENAI_ENDPOINT")
    )
    prompt_2 = ChatPromptTemplate.from_messages([
        ("system", "You are a knowledgeable assistant. Answer the following question based on the passage."),
        ("human", "Passage: {passage}\nQuestion: {question}")
    ])
    chain_2 = prompt_2 | model_2
    answer = chain_2.invoke({"passage": passage, "question": question}).content

    return question, answer, [model_1_name, model_2_name]


# Helper to reduce duplicate setup code
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