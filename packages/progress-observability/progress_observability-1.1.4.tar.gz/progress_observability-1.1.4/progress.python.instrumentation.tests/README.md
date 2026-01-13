
# Progress Observability Python Test Suite

Comprehensive unit and integration tests for the Progress Observability Python instrumentation library.
Supports multiple frameworks (LangChain, LlamaIndex, Haystack, direct provider calls) and uses OpenTelemetry for tracing.

---

## Table of Contents
- [Setup Instructions](#setup-instructions)
- [Info](#info)
  - [Test Categories](#test-categories)
  - [Test Patterns](#test-patterns)
  - [Tested Models and Providers](#tested-models-and-providers)
  - [Fixtures & Helpers](#fixtures--helpers)
  - [Span Validation Helpers](#span-validation-helpers)
  - [VCR Cassette Management](#vcr-cassette-management)
  - [Cassette Recordings](#cassette-recordings)
  
---

## Setup Instructions 

### 1. Generate the instrumentation wheel
Go to the `progress.observability.instrumentation` folder:
```zsh
cd ../progress.observability.instrumentation
uv venv
source .venv/bin/activate
uv build
```
This will create a new `dist/` folder containing `progress_observability-0.1.0-py3-none-any.whl`. Copy this file into the test root folder.

### 2. Create a .env file in the project root for the OPENAI/Azure providers/Anthropic/Bedrock
Dummy/example values
```zsh
AZURE_OPENAI_API_KEY=dummy-api-key
AZURE_OPENAI_ENDPOINT=https://test-azure-endpoint.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
DISABLE_HTTP_MOCKS=0

ANTHROPIC_API_KEY=dummy-anthropic-key

AWS_BEARER_TOKEN_BEDROCK=dummy-aws-bearer-token
AWS_DEFAULT_REGION=us-east-1
```
For live cassette recording, replace dummy values with your real credentials and set DISABLE_HTTP_MOCKS=1

### 3. Install dependencies

```zsh
uv venv
source .venv/bin/activate
uv sync
uv pip install --force-reinstall progress_observability-0.1.0-py3-none-any.whl
```
Key dependencies managed in [`pyproject.toml`](pyproject.toml)

### 4. Running tests
```zsh
#r un all test
python -m pytest -v 
# run all tests in the folder
python -m pytest src/framework_langchain/tests/ -v
# run a single test
python -m pytest src/framework_langchain/tests/test_simple_agents_ollama_fl.py -v
```
---

## Info

### Test Categories
- **General tests** (`src/general_tests/`): Core  functionality
- **Framework tests**: `src/framework_langchain/`, `src/framework_llama_index/`, `src/framework_haystack/`
- **Direct provider calls**: `src/direct_provider_calls/` (bypass frameworks and call provider APIs directly)

**Note**: `test_block_instruments.py` and `test_edge_cases.py`/`TestGracefulHandling` should be run in isolation due to Progress Observability  being a singleton. Use `src/general_tests/test_isolated.py` for isolated runs.

### Test Patterns
- Simple agents: Single model, single request
- Multi-model agents: Chaining models
- Two-provider agents: Ollama + OpenAI in one workflow

### Tested Models and Providers
- OpenAI/Azure OpenAI: `gpt-4o`, `gpt-4o-mini`, `gpt-4.1-nano`
- Ollama: `gemma2:2b`, `qwen2.5:3b`

### Fixtures & Helpers
All test frameworks use a centralized fixture system defined in [`src/test_utils/conftest_shared.py`]:

**Core Fixtures:**
- `setup_observability`: Initializes Progress Observability  instrumentation with OpenTelemetry
- `fixture_span_exporter`: In-memory span exporter for capturing telemetry data
- `vcr_config`: Centralized VCR configuration with API key filtering
- `cassette_path`: Dynamic cassette path generation based on test file location

**Instrumentation Fixtures:**
- `instrument_auto`: Auto-instrumentation (default, recommended)

### Span Validation Helpers
The [`src/llm_span_helpers.py`] module provides comprehensive span validation:

**Core Functions:**
- `get_llm_spans(spans)`: Filters spans to find LLM-related telemetry
- `use_vcr_cassette()`: Standardized VCR cassette wrapper with security filtering
- `shorten_model_name(model_name)`: Shortens long model names for cassette filenames
- `check_required_attributes(span)`: Validates required OpenTelemetry attributes (supports both new and legacy attribute names)
- `check_system_value(span)`: Validates `gen_ai.provider.name` (or `gen_ai.system` for backwards compatibility)
- `check_model_attributes(span)`: Validates model consistency between request/response
- `check_resource_validation(span)`: Validates span metadata and timing

**Model Name Shortening:**
To keep cassette filenames manageable, long model names are automatically shortened using predefined aliases:
- `claude-sonnet-4-20250514` → `cs4-0514`
- `us.anthropic.claude-sonnet-4-5-20250929-v1:0` → `cs45-bedrock`
- `claude-3-5-sonnet-20241022` → `cs35-1022`
- `gpt-4o` → `gpt4o`

New model aliases can be added to `CASSETTE_MODEL_ALIASES` in `llm_span_helpers.py`.

### VCR Cassette Management
The test suite implements comprehensive security measures for API key protection:

**Automatic API Key Filtering:**
- `authorization`: OAuth and bearer tokens
- `x-api-key`: Generic API keys
- `api-key`: Alternative API key header format

### Cassette Recordings
To update cassettes, delete the old file and rerun the test. For OPENAI/Azure you need to set your real credentials in the `.env` file.

