import subprocess
import sys
import pytest

def run_isolated_test(test_file, test_function_name, config_params=None):
    """Run a specific test function with given parameters in subprocess"""
    if config_params:
        test_identifier = f"{test_file}::{test_function_name}[{config_params}]"
    else:
        test_identifier = f"{test_file}::{test_function_name}"
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_identifier, "-v", "--tb=short"],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        print(f"\n--- FAILED: {test_function_name} ---")
        if config_params:
            print(f"Config: {config_params}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
    
    assert result.returncode == 0, (
        f"Test {test_function_name} failed in subprocess.\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )

# Test file paths
TEST_FILE_EDGE_CASES = "src/general_tests/test_edge_cases.py"
TEST_FILE_BLOCK_INSTRUMENTS = "src/general_tests/block_instruments.py"

# TestGracefulHandling tests
GRACEFUL_HANDLING_TESTS = [
    "test_none_as_instruments",
    "test_empty_set_as_instruments", 
    "test_block_without_instrument"
]

@pytest.mark.parametrize("test_name", GRACEFUL_HANDLING_TESTS)
def test_graceful_handling_isolated(test_name):
    """Run TestGracefulHandling tests in subprocess isolation"""
    test_function_name = f"TestGracefulHandling::{test_name}"
    run_isolated_test(TEST_FILE_EDGE_CASES, test_function_name)

# TestBlockingInstrumentation tests
BLOCKING_INSTRUMENTATION_TESTS = [
    "test_conflicts_should_raise_error",
    "test_reinitialize_should_raise_error",
    "test_normal_instrumentation_creates_spans",
    "test_blocking_prevents_spans",
    "test_blocking_multiple_instruments", 
]

@pytest.mark.parametrize("test_name", BLOCKING_INSTRUMENTATION_TESTS)
def test_blocking_instrumentation_isolated(test_name):
    """Run TestBlockingInstrumentation tests in subprocess isolation"""
    test_function_name = f"TestBlockingInstrumentation::{test_name}"
    run_isolated_test(TEST_FILE_BLOCK_INSTRUMENTS, test_function_name)

# Parametrized blocking test with block providers
BLOCK_PROVIDERS = [
    ("ollama", "openai", "ollama"),
    ("openai", "ollama", "openai")
]


@pytest.mark.parametrize("block_provider,expected_present,expected_blocked", BLOCK_PROVIDERS)
def test_blocked_vs_unblocked_provider_isolated(block_provider, expected_present, expected_blocked):
    """Run parametrized blocking provider tests in subprocess isolation"""
    test_function_name = "TestBlockingInstrumentation::test_blocked_vs_unblocked_provider_span"
    config_params = f"{block_provider}-{expected_present}-{expected_blocked}"
    run_isolated_test(TEST_FILE_BLOCK_INSTRUMENTS, test_function_name, config_params)



