import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from test_utils.conftest_shared import (
    mock_http_requests,
    fixture_span_exporter,
    setup_observability, 
    vcr_config,
    cassette_path,
    instrument_auto,
    instrument_langchain, 
    instrument_ollama, 
    instrument_langchain_ollama, 
    instrument_openai,
    instrument_langchain_openai, 
    instrument_ollama_openai,
    instrument_langchain_ollama_openai
)