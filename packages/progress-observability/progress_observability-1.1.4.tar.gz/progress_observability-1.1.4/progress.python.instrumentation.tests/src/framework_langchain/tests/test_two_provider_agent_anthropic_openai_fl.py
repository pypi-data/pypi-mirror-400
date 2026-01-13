"""
Tests for two-provider agent chain using Anthropic and OpenAI (LangChain framework).
Model 1 (Anthropic): Answers a medical question.
Model 2 (OpenAI): Explains the answer in detail.
"""
from os import getenv
import time
import pytest
from langchain_anthropic import ChatAnthropic
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from test_utils.llm_span_helpers import (
    get_llm_spans,
    check_required_attributes,
    check_system_value,
    check_model_attributes,
    check_resource_validation,
    use_vcr_cassette,
    shorten_model_name
)

# Parametrize anthropic and openai models, check types, and instrument fixtures
ANTHROPIC_MODELS = ["claude-sonnet-4-20250514"]
OPENAI_MODELS = [
    # "gpt-4o-mini", 
    "gpt-4o", 
]
CHECK_TYPES = [
    "required_attributes",
    "system_value",
    "model_attributes",
    "resource_validation",
    "llm_span_count"
]
INSTRUMENT_FIXTURES = [
    "instrument_auto",
    # "instrument_langchain",
    # "instrument_openai",
    # "instrument_langchain_openai",
    # Missing fixtures for Anthropic

]

def get_agent_data(anthropic_model, openai_deployment):
    question = "What are the common symptoms of diabetes?"
    return {
        "question": question,
        "expected_llm_spans": 2,
        "anthropic_model": anthropic_model,
        "openai_deployment": openai_deployment
    }

def run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path):
    instrument = request.getfixturevalue(instrument_fixture)
    short_anthropic = shorten_model_name(agent_data['anthropic_model'])
    short_openai = shorten_model_name(agent_data['openai_deployment'])
    cassette_name = f"{instrument_fixture}-{short_anthropic}-{short_openai}"
    
    with use_vcr_cassette(cassette_path, cassette_name, vcr_config):
        # Model 1: Anthropic answers the medical question
        model_1 = ChatAnthropic(
            model=agent_data["anthropic_model"],
            api_key=getenv("ANTHROPIC_API_KEY"),
            max_tokens=1024,
            temperature=0.1
        )
        prompt_1 = ChatPromptTemplate.from_messages([
            ("system", "You are a medical expert. Answer the following question concisely and accurately."),
            ("human", "{question}")
        ])
        chain_1 = prompt_1 | model_1
        answer = chain_1.invoke({"question": agent_data["question"]}).content

        time.sleep(1)

        # Model 2: OpenAI explains the answer
        model_2 = AzureChatOpenAI(
            azure_endpoint=getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=getenv("AZURE_OPENAI_API_KEY"),
            azure_deployment=agent_data["openai_deployment"],
            api_version="2024-02-15-preview"
        )
        prompt_2 = ChatPromptTemplate.from_messages([
            ("system", "You are a knowledgeable medical assistant. Explain the following answer in detail for a layperson."),
            ("human", "Question: {question}\nAnswer: {answer}")
        ])
        chain_2 = prompt_2 | model_2
        explanation = chain_2.invoke({"question": agent_data["question"], "answer": answer}).content

        assert answer is not None and len(answer) > 0, "Anthropic answer should be generated"
        assert explanation is not None and len(explanation) > 0, "OpenAI explanation should be generated"
        spans = span_exporter.get_finished_spans()
        assert spans, "No spans were created"
        llm_spans = get_llm_spans(spans)
        assert llm_spans, "No LLM spans were created"
        return llm_spans, agent_data


@pytest.mark.parametrize("anthropic_model", ANTHROPIC_MODELS)
@pytest.mark.parametrize("openai_deployment", OPENAI_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_required_attributes(request, instrument_fixture, openai_deployment, anthropic_model, span_exporter, vcr_config, cassette_path, subtests):
    agent_data = get_agent_data(anthropic_model, openai_deployment)
    llm_spans, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_required_attributes(span)


@pytest.mark.parametrize("anthropic_model", ANTHROPIC_MODELS)
@pytest.mark.parametrize("openai_deployment", OPENAI_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_system_value(request, instrument_fixture, openai_deployment, anthropic_model, span_exporter, vcr_config, cassette_path, subtests):
    agent_data = get_agent_data(anthropic_model, openai_deployment)
    llm_spans, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_system_value(span)


@pytest.mark.parametrize("anthropic_model", ANTHROPIC_MODELS)
@pytest.mark.parametrize("openai_deployment", OPENAI_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_model_attributes(request, instrument_fixture, openai_deployment, anthropic_model, span_exporter, vcr_config, cassette_path, subtests):
    agent_data = get_agent_data(anthropic_model, openai_deployment)
    llm_spans, agent_data = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for i, span in enumerate(llm_spans):
        expected_model = agent_data["anthropic_model"] if i == 0 else agent_data["openai_deployment"]
        check_model_attributes(span, expected_model)


@pytest.mark.parametrize("anthropic_model", ANTHROPIC_MODELS)
@pytest.mark.parametrize("openai_deployment", OPENAI_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_resource_validation(request, instrument_fixture, openai_deployment, anthropic_model, span_exporter, vcr_config, cassette_path, subtests):
    agent_data = get_agent_data(anthropic_model, openai_deployment)
    llm_spans, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_resource_validation(span)


@pytest.mark.parametrize("anthropic_model", ANTHROPIC_MODELS)
@pytest.mark.parametrize("openai_deployment", OPENAI_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_llm_span_count(request, instrument_fixture, openai_deployment, anthropic_model, span_exporter, vcr_config, cassette_path, subtests):
    agent_data = get_agent_data(anthropic_model, openai_deployment)
    llm_spans, agent_data = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    if instrument_fixture == "instrument_openai":
        expected_llm_spans = 1
    elif instrument_fixture == "instrument_anthropic":
        expected_llm_spans = 1
    else:
        expected_llm_spans = 2
    assert len(llm_spans) == expected_llm_spans, f"Expected {expected_llm_spans} LLM spans, got {len(llm_spans)}"
