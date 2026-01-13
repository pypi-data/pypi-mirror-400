"""
Tests for simple Haystack agents using Ollama.
Example: Using Haystack with OllamaChatGenerator.
"""
import pytest
from haystack_integrations.components.generators.ollama import OllamaChatGenerator
from haystack.dataclasses import ChatMessage
import vcr
from pathlib import Path

# Haystack framework instrument fixtures
INSTRUMENT_FIXTURES = [
    "instrument_auto",
    # "instrument_haystack",
    # "instrument_ollama",
    # "instrument_haystack_ollama",
]

from test_utils.llm_span_helpers import (
    check_required_attributes,
    check_system_value,
    check_model_attributes,
    check_resource_validation,
    get_llm_spans,
    use_vcr_cassette
)

# Test different Ollama models
OLLAMA_MODELS = ["gemma2:2b", "qwen2.5:3b"]

def get_agent_data(model):
    return {
        "model": model,
        "expected_total_spans": 3,
        "expected_llm_spans": 1,
        "system_prompt": "You are a helpful AI assistant. Provide clear, accurate, and concise answers to user questions.",
        "question": "What is the capital of France?"
    }


def _run_simple_agent(agent_data):
    """Run the simple agent and return response and model name"""
    model = agent_data["model"]
    system_prompt = agent_data["system_prompt"]
    question = agent_data["question"]

    # Create Ollama Chat Generator
    generator = OllamaChatGenerator(
        url="http://localhost:11434",  # Remove /v1 for OllamaChatGenerator
        model=model,
        timeout=120,   
        generation_kwargs={"temperature": 0.1}
    )

    # Create messages
    messages = [
        ChatMessage.from_system(system_prompt),
        ChatMessage.from_user(question)
    ]

    # Generate response
    result = generator.run(messages=messages)
    answer = result["replies"][0].text

    return answer, model


def run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path):
    instrument = request.getfixturevalue(instrument_fixture)
    cassette_name = f"simple_agent_{agent_data['model'].replace(':', '-')}"
    
    with use_vcr_cassette(cassette_path, cassette_name, vcr_config):
        answer, model_name = _run_simple_agent(agent_data)
        assert answer
        spans = span_exporter.get_finished_spans()
        assert spans, "No spans were created"
        llm_spans = get_llm_spans(spans)
        assert llm_spans, "No LLM spans were created"
        return llm_spans, model_name, agent_data


@pytest.mark.parametrize("model", OLLAMA_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_required_attributes(request, instrument_fixture, model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(model)
    llm_spans, _, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_required_attributes(span)


@pytest.mark.parametrize("model", OLLAMA_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_system_value(request, instrument_fixture, model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(model)
    llm_spans, _, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_system_value(span)


@pytest.mark.parametrize("model", OLLAMA_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_model_attributes(request, instrument_fixture, model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(model)
    llm_spans, model_name, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_model_attributes(span, model_name)


@pytest.mark.parametrize("model", OLLAMA_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_resource_validation(request, instrument_fixture, model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(model)
    llm_spans, _, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_resource_validation(span)


@pytest.mark.parametrize("model", OLLAMA_MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_llm_span_count(request, instrument_fixture, model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(model)
    llm_spans, _, agent_data = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    assert len(llm_spans) == agent_data["expected_llm_spans"], f"Expected {agent_data['expected_llm_spans']} LLM spans, got {len(llm_spans)}"
