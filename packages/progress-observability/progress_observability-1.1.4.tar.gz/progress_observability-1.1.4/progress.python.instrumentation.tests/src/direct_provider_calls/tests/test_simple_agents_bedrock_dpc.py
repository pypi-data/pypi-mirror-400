"""
Tests for simple Bedrock agents using Amazon Bedrock models.
Example: Simple question-answering using different Bedrock model directly via boto3.
"""
import os
import json
from dotenv import load_dotenv
import pytest
import boto3

load_dotenv()

# Bedrock framework instrument fixtures
INSTRUMENT_FIXTURES = [
    "instrument_auto",
    # "instrument_bedrock",
    # "instrument_boto3",
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

# Test different Bedrock models
MODELS = [
    "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
]

def get_agent_data(model):
    question = "What is the capital of France and why is it important?"
    return {
        "question": question,
        "model": model,
        "expected_llm_spans": 1,
    }


def _run_simple_agent(agent_data):
    """Run the simple agent and return response"""
    question = agent_data["question"]
    model_name = agent_data["model"]

    # Get bearer token from environment
    bearer_token = os.getenv('AWS_BEARER_TOKEN_BEDROCK')
    
    # Create Bedrock client with bearer token authentication
    if bearer_token:
        # Create a custom config to add the bearer token as an Authorization header
        def add_auth_header(request, **kwargs):
            request.headers['Authorization'] = f'Bearer {bearer_token}'
        
        # Create the client and add event handler for the authorization header
        client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_DEFAULT_REGION')
        )
        
        # Add the event handler to inject the bearer token
        client.meta.events.register('before-sign.bedrock-runtime.*', add_auth_header)
    else:
        # Fallback to default credentials
        client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_DEFAULT_REGION')
        )

    # Prepare the request body for Claude models
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 150,
        "temperature": 0.1,
        "messages": [
            {
                "role": "user",
                "content": f"System: You are a helpful assistant.\n\nHuman: {question}"
            }
        ]
    }

    # Get response
    response = client.invoke_model(
        modelId=model_name,
        body=json.dumps(body),
        contentType='application/json'
    )
    
    response_body = json.loads(response['body'].read())
    content = response_body['content'][0]['text']
    
    return content, model_name


def run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path):
    instrument = request.getfixturevalue(instrument_fixture)
    short_model = shorten_model_name(agent_data['model'])
    cassette_name = f"simple_agent_{short_model}"
    
    with use_vcr_cassette(cassette_path, cassette_name, vcr_config):
        response, model_name = _run_simple_agent(agent_data)
        assert response
        spans = span_exporter.get_finished_spans()
        assert spans, "No spans were created"
        llm_spans = get_llm_spans(spans)
        assert llm_spans, "No LLM spans were created"
        return llm_spans, model_name, agent_data


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_required_attributes(request, instrument_fixture, model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(model)
    llm_spans, _, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_required_attributes(span)


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_system_value(request, instrument_fixture, model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(model)
    llm_spans, _, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_system_value(span)


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_model_attributes(request, instrument_fixture, model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(model)
    llm_spans, model_name, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_model_attributes(span, model_name)


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_resource_validation(request, instrument_fixture, model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(model)
    llm_spans, _, _ = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    for span in llm_spans:
        check_resource_validation(span)


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("instrument_fixture", INSTRUMENT_FIXTURES)
def test_simple_agent_llm_span_count(request, instrument_fixture, model, span_exporter, vcr_config, cassette_path):
    agent_data = get_agent_data(model)
    llm_spans, _, agent_data = run_and_get_llm_spans(request, instrument_fixture, agent_data, span_exporter, vcr_config, cassette_path)
    assert len(llm_spans) == agent_data["expected_llm_spans"], f"Expected {agent_data['expected_llm_spans']} LLM spans, got {len(llm_spans)}"