import pytest
from progress.observability import Observability, ObservabilityInstruments
from progress.observability.exceptions import EndpointValidationError


@pytest.fixture(autouse=True)
def reset_state():
    """Reset any SDK state between tests"""
    if hasattr(Observability, '_initialized'):
        Observability._initialized = False
    yield
    

class TestGracefulHandling:
    """Tests for graceful handling of edge cases"""
    
    def test_none_as_instruments(self):
        """Passing None as instruments should not break."""
        try:
            Observability.instrument(instruments=None)
        except Exception as e:
            pytest.fail(f"Should handle None gracefully, got: {e}")

    def test_empty_set_as_instruments(self):
        """Passing empty set as instruments should not break."""
        try:
            Observability.instrument(instruments=set())
        except Exception as e:
            pytest.fail(f"Should handle empty set gracefully, got: {e}")

    def test_block_without_instrument(self):
        """Blocking an instrument that is not enabled should not break."""
        try:
            Observability.instrument(block_instruments={ObservabilityInstruments.OPENAI})
        except Exception as e:
            pytest.fail(f"Should handle blocking without instrument gracefully, got: {e}")

class TestInstrumentsInputValidation:

    """Tests for input validation and error raising"""
    
    def test_unknown_instrument_name(self):
        """Passing an unknown instrument should raise an error."""
        with pytest.raises((ValueError, AttributeError, TypeError)):
            Observability.instrument(instruments={"NOT_A_REAL_INSTRUMENT"})

    def test_unknown_block_instrument(self):
        """Passing an unknown block instrument should raise an error."""
        with pytest.raises((ValueError, AttributeError, TypeError)):
            Observability.instrument(block_instruments={"NOT_A_REAL_INSTRUMENT"})

    @pytest.mark.parametrize("invalid_input", [
        123,  # int
        True,  # bool  
        "OPENAI",  # string
        {"OPENAI": True},  # dict
    ])
    def test_non_iterable_instruments_raise(self, invalid_input):
        """Non-iterable inputs should raise an error."""
        with pytest.raises((TypeError, ValueError, AttributeError)):
            Observability.instrument(instruments=invalid_input)

    @pytest.mark.parametrize("invalid_input", [
        123,  # int
        True,  # bool  
        "OPENAI",  # string
        {"OPENAI": True},  # dict
    ])
    def test_non_iterable_block_instruments_raise(self, invalid_input):
        """Non-iterable block_instruments should raise an error."""
        with pytest.raises((TypeError, ValueError, AttributeError)):
            Observability.instrument(block_instruments=invalid_input)

    def test_invalid_elements_in_instruments(self):
        """Invalid elements in instruments should raise an error."""
        # Test individual cases that would cause errors
        
        # Mixed invalid types
        with pytest.raises((TypeError, ValueError, AttributeError)):
            Observability.instrument(instruments={None, 42, object()})
        
        # Empty string
        with pytest.raises((TypeError, ValueError, AttributeError)):
            Observability.instrument(instruments={""})
        
        # Whitespace string
        with pytest.raises((TypeError, ValueError, AttributeError)):
            Observability.instrument(instruments={"   "})
        
        # Mixed valid/invalid
        with pytest.raises((TypeError, ValueError, AttributeError)):
            Observability.instrument(instruments={ObservabilityInstruments.OPENAI, "NOT_A_REAL_INSTRUMENT"})

    def test_single_enum_instead_of_set(self):
        """Passing a single enum instead of a set should raise an error."""
        with pytest.raises((TypeError, ValueError)):
            Observability.instrument(instruments=ObservabilityInstruments.OPENAI)

    def test_generator_with_invalid_types(self):
        """Generator yielding invalid types should raise an error."""
        with pytest.raises((TypeError, ValueError, AttributeError)):
            Observability.instrument(instruments=(x for x in [None, "bad", ObservabilityInstruments.OPENAI]))


class TestEndpointValidation:
   
    @pytest.mark.parametrize("endpoint,should_raise", [
        ("http://127.0.0.1:1", False),
        ("http://localhost:4318", False),
        ("http://127.0.0.1:9999", False),
        ("http://localhost:9999   ", True),
        ("http://127.0.0.1:99999", True),      # Invalid port
        ("http://127.0.0.1:-1", True),         # Negative port
        ("http://:4318", True),                # Missing host
        ("http://localhost:", True),           # Missing port
        ("http://localhost:port", True),       # Non-numeric port
        ("ftp://localhost:4318", True),        # Unsupported scheme
        ("http://local host:4318", True),      # Space in host
        ("", False),                            # Empty string
        (None, False),                          # None value
        ("https://localhost:4318", False),     # HTTPS
        # ("http://例子.测试:4318", False),        # Internationalized domain
    ])
    def test_endpoint_validation(self, endpoint, should_raise):
        if should_raise:
            with pytest.raises(EndpointValidationError):
                Observability.instrument(
                    app_name="test",
                    endpoint=endpoint,
                    api_key="api-key-123456789"
                )
        else:
            Observability.instrument(
                app_name="test",
                endpoint=endpoint,
                api_key="api-key-123456789"
            )

