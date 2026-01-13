import os
import pytest
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry import trace
import json
from dotenv import load_dotenv
from pathlib import Path
import logging
from unittest.mock import patch, MagicMock
from progress.observability import Observability, ObservabilityInstruments

os.environ["OTEL_METRICS_EXPORTER"] = "none"
os.environ["OTEL_EXPORTER_OTLP_METRICS_ENDPOINT"] = ""
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = ""
logging.getLogger("opentelemetry.sdk.trace.export").setLevel(logging.CRITICAL)
logging.getLogger("opentelemetry.exporter.otlp").setLevel(logging.CRITICAL)
logging.getLogger("opentelemetry.sdk.metrics").setLevel(logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

# Load .env from the project root directory
project_root = Path(__file__).resolve().parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

# Mock the HTTP requests to prevent connection errors
@pytest.fixture(scope="session", autouse=True)
def mock_http_requests():
    """Mock HTTP requests to prevent telemetry exporters from making actual network calls.
    Set DISABLE_HTTP_MOCKS=1 to disable this and allow real HTTP requests (for VCR.py recording).
    
    Note: We do NOT mock urllib3.connectionpool.HTTPConnectionPool.urlopen because:
    1. It interferes with VCR.py cassette recording/playback
    2. It breaks boto3's AWS API calls (used by Bedrock tests)
    3. OpenTelemetry exporters use requests, which we already mock
    """
    import os
    if os.environ.get("DISABLE_HTTP_MOCKS", "0") == "1":
        yield
        return
    with patch('requests.Session.post') as mock_post, \
         patch('requests.post') as mock_post_direct, \
         patch('opentelemetry.exporter.otlp.proto.http.metric_exporter.OTLPMetricExporter.export') as mock_export:
        # Make all HTTP posts return a successful mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"success": true}'
        mock_response.json.return_value = {"success": True}
        
        mock_post.return_value = mock_response
        mock_post_direct.return_value = mock_response
        mock_export.return_value = None  # Suppress metric exports entirely
        yield

@pytest.fixture(scope="function", name="span_exporter")
def fixture_span_exporter():
    exporter = InMemorySpanExporter()
    yield exporter
    exporter.clear()

@pytest.fixture
def setup_observability(span_exporter):
    def _setup(app_name, instruments=None, block_instruments=None):
        span_exporter.clear()
        Observability.instrument(
            app_name=app_name,
            instruments=instruments,
            block_instruments=block_instruments,
            endpoint="http://127.0.0.1:1",
            api_key="api-key-123456789",
        )
        provider = trace.get_tracer_provider()
        provider.add_span_processor(SimpleSpanProcessor(span_exporter))
        return provider
    
    yield _setup
    
    # Cleanup after test
    try:
        Observability.shutdown()
    except Exception:
        pass
    trace.set_tracer_provider(None)

@pytest.fixture
def cassette_path(request):
    """Centralized cassette path management - creates path based on test file location"""
    test_file_path = Path(request.fspath)
    test_dir_name = test_file_path.stem  # e.g., "test_block_instruments"
    cassettes_dir = test_file_path.parent / "cassettes" / test_dir_name
    cassettes_dir.mkdir(parents=True, exist_ok=True)
    return cassettes_dir

# VCR.py configuration for filtering sensitive data from cassettes
@pytest.fixture(scope="module")
def vcr_config():
    def before_record_request(request):
        # Filter out AWS EC2 metadata service requests (used by boto3 for credential discovery)
        # These should not be recorded in cassettes as they're environment-specific
        if hasattr(request, 'uri') and '169.254.169.254' in request.uri:
            return None
        
        if hasattr(request, "body") and request.body:
            try:
                if isinstance(request.body, (str, bytes)):
                    body_str = (
                        request.body.decode("utf-8")
                        if isinstance(request.body, bytes)
                        else request.body
                    )
                    body_data = json.loads(body_str)
                    if "api_key" in body_data:
                        body_data["api_key"] = "FILTERED"
                        request.body = json.dumps(body_data)
            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                pass
        return request

    def before_record_response(response):
        return response

    return {
        "filter_headers": ["authorization", "x-api-key", "api-key"],
        "filter_query_parameters": [],
        "filter_post_data_parameters": [],
        "match_on": ["method", "scheme", "port", "path", "query"],  # Removed "host" from matching
        "before_record_request": before_record_request,
        "before_record_response": before_record_response,
        "ignore_hosts": ["169.254.169.254"],  # Ignore AWS metadata service
    }


# ALL COMBINATIONS OF AGENT CLARITY INSTRUMENTS

# AUTO - All instruments enabled
@pytest.fixture(scope="function")
def instrument_auto(setup_observability):
    setup_observability(app_name="test")
    yield

# OpenAI only
@pytest.fixture(scope="function")
def instrument_openai(setup_observability):
    setup_observability(
        app_name="test",
        instruments=[ObservabilityInstruments.OPENAI],
    )
    yield

# OLLAMA only
@pytest.fixture(scope="function")
def instrument_ollama(setup_observability):
    setup_observability(
        app_name="test",
        instruments=[ObservabilityInstruments.OLLAMA],
    )
    yield

# OLLAMA + OpenAI
@pytest.fixture(scope="function")
def instrument_ollama_openai(setup_observability):
    setup_observability(
        app_name="test",
        instruments=[ObservabilityInstruments.OLLAMA, ObservabilityInstruments.OPENAI],
    )
    yield

# Haystack only
@pytest.fixture(scope="function")
def instrument_haystack(setup_observability):
    setup_observability(
        app_name="test",
        instruments=[ObservabilityInstruments.HAYSTACK],
    )
    yield

# Haystack + OLLAMA
@pytest.fixture(scope="function")
def instrument_haystack_ollama(setup_observability):
    setup_observability(
        app_name="test",
        instruments=[ObservabilityInstruments.HAYSTACK, ObservabilityInstruments.OLLAMA],
    )
    yield


# Haystack + OPENAI
@pytest.fixture(scope="function")
def instrument_haystack_openai(setup_observability):
    setup_observability(
        app_name="test",
        instruments=[ObservabilityInstruments.HAYSTACK, ObservabilityInstruments.OPENAI],
    )
    yield

# Haystack + OLLAMA + OPENAI
@pytest.fixture(scope="function")
def instrument_haystack_ollama_openai(setup_observability):
    setup_observability(
        app_name="test",
        instruments=[ObservabilityInstruments.HAYSTACK, ObservabilityInstruments.OLLAMA, ObservabilityInstruments.OPENAI],
    )
    yield

# LangChain only
@pytest.fixture(scope="function")
def instrument_langchain(setup_observability):
    setup_observability(
        app_name="test",
        instruments=[ObservabilityInstruments.LANGCHAIN],
    )
    yield

# LangChain + OLLAMA
@pytest.fixture(scope="function")
def instrument_langchain_ollama(setup_observability):
    setup_observability(
        app_name="test",
        instruments=[ObservabilityInstruments.LANGCHAIN, ObservabilityInstruments.OLLAMA],
    )
    yield

# LangChain + OPENAI
@pytest.fixture(scope="function")
def instrument_langchain_openai(setup_observability):
    setup_observability(
        app_name="test",
        instruments=[ObservabilityInstruments.LANGCHAIN, ObservabilityInstruments.OPENAI],
    )
    yield

# LangChain + OLLAMA + OPENAI
@pytest.fixture(scope="function")
def instrument_langchain_ollama_openai(setup_observability):
    setup_observability(
        app_name="test",
        instruments=[ObservabilityInstruments.LANGCHAIN, ObservabilityInstruments.OLLAMA, ObservabilityInstruments.OPENAI],
    )
    yield

# LLamaIndex only
@pytest.fixture(scope="function")
def instrument_llama_index(setup_observability):
    setup_observability(
        app_name="test",
        instruments=[ObservabilityInstruments.LLAMA_INDEX],
    )
    yield

# LLamaIndex + OLLAMA
@pytest.fixture(scope="function")
def instrument_ollama_llama_index(setup_observability):
    setup_observability(
        app_name="test",
        instruments=[ObservabilityInstruments.LLAMA_INDEX, ObservabilityInstruments.OLLAMA],
    )
    yield

# LLamaIndex + OPENAI
@pytest.fixture(scope="function")
def instrument_llama_index_openai(setup_observability):
    setup_observability(
        app_name="test",
        instruments=[ObservabilityInstruments.LLAMA_INDEX, ObservabilityInstruments.OPENAI],
    )
    yield

# LLamaIndex + OLLAMA + OPENAI
@pytest.fixture(scope="function")
def instrument_ollama_openai_llama_index(setup_observability):
    setup_observability(
        app_name="test",
        instruments=[ObservabilityInstruments.LLAMA_INDEX, ObservabilityInstruments.OLLAMA, ObservabilityInstruments.OPENAI],
    )
    yield

# LLamaIndex + Anthropic + OPENAI
@pytest.fixture(scope="function")
def instrument_anthropic_openai_llama_index(setup_observability):
    setup_observability(
        app_name="test",
        instruments=[ObservabilityInstruments.LLAMA_INDEX, ObservabilityInstruments.ANTHROPIC, ObservabilityInstruments.OPENAI],
    )
    yield

# OpenAI Agents only
@pytest.fixture(scope="function")
def instrument_openai_agents(setup_observability):
    setup_observability(
        app_name="test",
        instruments=[ObservabilityInstruments.OPENAI_AGENTS],
    )
    yield  

# OpenAI Agents + OPENAI
@pytest.fixture(scope="function")
def instrument_openai_agents_openai(setup_observability):
    setup_observability(
        app_name="test",
        instruments=[ObservabilityInstruments.OPENAI_AGENTS, ObservabilityInstruments.OPENAI],
    )
    yield

# OpenAI Agents + OLLAMA
@pytest.fixture(scope="function")
def instrument_openai_agents_ollama(setup_observability):
    setup_observability(
        app_name="test",
        instruments=[ObservabilityInstruments.OPENAI_AGENTS, ObservabilityInstruments.OLLAMA],
    )
    yield

# OpenAI Agents + OLLAMA + OPENAI
@pytest.fixture(scope="function")
def instrument_openai_agents_ollama_openai(setup_observability): 
    setup_observability(
        app_name="test",
        instruments=[ObservabilityInstruments.OPENAI_AGENTS, ObservabilityInstruments.OLLAMA, ObservabilityInstruments.OPENAI],
    )
    yield