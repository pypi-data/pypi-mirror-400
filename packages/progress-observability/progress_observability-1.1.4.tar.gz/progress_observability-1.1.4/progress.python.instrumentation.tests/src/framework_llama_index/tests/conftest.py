import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from test_utils.conftest_shared import (
    mock_http_requests,
    fixture_span_exporter,
    setup_observability,
    vcr_config,
    cassette_path,
    instrument_auto,
    instrument_llama_index,
    instrument_openai, 
    instrument_llama_index_openai, 
    instrument_ollama, 
    instrument_ollama_llama_index,
    instrument_ollama_openai,
    instrument_ollama_openai_llama_index,
    instrument_anthropic_openai_llama_index
)
