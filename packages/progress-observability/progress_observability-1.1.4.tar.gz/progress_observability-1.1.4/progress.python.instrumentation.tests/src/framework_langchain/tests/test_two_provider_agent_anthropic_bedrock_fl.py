"""
Tests for two-provider agent chain using Anthropic and Bedrock (LangChain framework).
Model 1 (Anthropic): Answers a question.
Model 2 (Bedrock): Explains the answer in detail.
"""
from dotenv import load_dotenv
load_dotenv() 

from os import getenv
import time
import pytest
from langchain_anthropic import ChatAnthropic
from langchain_aws import ChatBedrockConverse
from langchain_core.prompts import ChatPromptTemplate

from test_utils.llm_span_helpers import (
    get_llm_spans,
    check_required_attributes,
    check_system_value,
    check_model_attributes,
    check_resource_validation,
    use_vcr_cassette,
    shorten_model_name,
)

# Parametrize anthropic and bedrock models, check types, and instrument fixtures
ANTHROPIC_MODELS = ["claude-sonnet-4-20250514"]
BEDROCK_MODELS = [getenv("BEDROCK_MODEL", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")]

INSTRUMENT_FIXTURES = [
    "instrument_auto",
]

def get_agent_data(anthropic_model, bedrock_model):
    question = "What are the common symptoms of diabetes?"
    return {
        "question": question,
        "expected_llm_spans": 2,
        "anthropic_model": anthropic_model,
        "bedrock_model": bedrock_model,
    }


def run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path):
    instrument = request.getfixturevalue(instrument_fixture)
    # Shorten model names for cassette filename
    short_anthropic = shorten_model_name(agent_data['anthropic_model'])
    short_bedrock = shorten_model_name(agent_data['bedrock_model'])
    cassette_name = f"{instrument_fixture}-{short_anthropic}-{short_bedrock}"

    with use_vcr_cassette(cassette_path, cassette_name, vcr_config):
        # Model 1: Anthropic answers the question
        model_1 = ChatAnthropic(
            model=agent_data["anthropic_model"],
            api_key=getenv("ANTHROPIC_API_KEY"),
            max_tokens=1024,
            temperature=0.1,
        )
        prompt_1 = ChatPromptTemplate.from_messages([
            ("system", "You are an expert assistant. Answer the following question concisely and accurately."),
            ("human", "{question}"),
        ])
        chain_1 = prompt_1 | model_1
        answer = chain_1.invoke({"question": agent_data["question"]}).content

        time.sleep(1)

        # Model 2: Bedrock explains the answer
        model_2 = ChatBedrockConverse(
            model=agent_data["bedrock_model"],
            temperature=0.0,
            max_tokens=None,
        )
        prompt_2 = ChatPromptTemplate.from_messages([
            ("system", "You are a knowledgeable assistant. Explain the following answer in detail for a layperson."),
            ("human", "Question: {question}\nAnswer: {answer}"),
        ])
        chain_2 = prompt_2 | model_2
        explanation = chain_2.invoke({"question": agent_data["question"], "answer": answer}).content

        assert answer is not None and len(answer) > 0, "Anthropic answer should be generated"
        assert explanation is not None and len(explanation) > 0, "Bedrock explanation should be generated"

        spans = span_exporter.get_finished_spans()
        assert spans, "No spans were created"
        llm_spans = get_llm_spans(spans)
        assert llm_spans, "No LLM spans were created"
        return llm_spans, agent_data


@pytest.mark.parametrize("anthropic_model", ANTHROPIC_MODELS)
@pytest.mark.parametrize("bedrock_model", BEDROCK_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_required_attributes(request, instrument_fixture, bedrock_model, anthropic_model, span_exporter, vcr_config, cassette_path, subtests):
    agent_data = get_agent_data(anthropic_model, bedrock_model)
    llm_spans, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_required_attributes(span)


@pytest.mark.parametrize("anthropic_model", ANTHROPIC_MODELS)
@pytest.mark.parametrize("bedrock_model", BEDROCK_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_system_value(request, instrument_fixture, bedrock_model, anthropic_model, span_exporter, vcr_config, cassette_path, subtests):
    agent_data = get_agent_data(anthropic_model, bedrock_model)
    llm_spans, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_system_value(span)


@pytest.mark.parametrize("anthropic_model", ANTHROPIC_MODELS)
@pytest.mark.parametrize("bedrock_model", BEDROCK_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_model_attributes(request, instrument_fixture, bedrock_model, anthropic_model, span_exporter, vcr_config, cassette_path, subtests):
    agent_data = get_agent_data(anthropic_model, bedrock_model)
    llm_spans, agent_data = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for i, span in enumerate(llm_spans):
        expected_model = agent_data["anthropic_model"] if i == 0 else agent_data["bedrock_model"]
        check_model_attributes(span, expected_model)


@pytest.mark.parametrize("anthropic_model", ANTHROPIC_MODELS)
@pytest.mark.parametrize("bedrock_model", BEDROCK_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_resource_validation(request, instrument_fixture, bedrock_model, anthropic_model, span_exporter, vcr_config, cassette_path, subtests):
    agent_data = get_agent_data(anthropic_model, bedrock_model)
    llm_spans, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_resource_validation(span)


@pytest.mark.parametrize("anthropic_model", ANTHROPIC_MODELS)
@pytest.mark.parametrize("bedrock_model", BEDROCK_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_two_provider_agent_llm_span_count(request, instrument_fixture, bedrock_model, anthropic_model, span_exporter, vcr_config, cassette_path, subtests):
    agent_data = get_agent_data(anthropic_model, bedrock_model)
    llm_spans, agent_data = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    if instrument_fixture == "instrument_anthropic":
        expected_llm_spans = 1
    elif instrument_fixture == "instrument_bedrock":
        expected_llm_spans = 1
    else:
        expected_llm_spans = 2
    assert len(llm_spans) == expected_llm_spans, f"Expected {expected_llm_spans} LLM spans, got {len(llm_spans)}"
