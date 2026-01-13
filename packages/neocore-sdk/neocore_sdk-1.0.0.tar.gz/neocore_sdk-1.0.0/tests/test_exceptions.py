"""
Unit tests for exception classes.

Tests the exception hierarchy and error handling.
"""

import pytest
from neocore_sdk.exceptions import (
    # Base exception
    SecureSDKError,
    # Key errors
    KeyLoadError,
    KeyNotFoundError,
    # Signing errors
    SigningError,
    CanonicalizationError,
    # Validation errors
    ValidationError,
    # Network errors
    APIConnectionError,
    APITimeoutError,
    DNSError,
    ConnectionRefusedError,
    SSLError,
    ProxyError,
    # HTTP status errors
    APIStatusError,
    BadRequestError,
    AuthenticationError,
    PermissionError,
    NotFoundError,
    ConflictError,
    UnprocessableEntityError,
    RateLimitError,
    InternalServerError,
    ServiceUnavailableError,
    GatewayTimeoutError,
    # Helper function
    get_exception_for_status_code,
)


class TestExceptionHierarchy:
    """Test exception hierarchy and inheritance."""

    def test_all_exceptions_inherit_from_base(self):
        """Test that all SDK exceptions inherit from SecureSDKError."""
        exceptions = [
            KeyLoadError,
            KeyNotFoundError,
            SigningError,
            CanonicalizationError,
            ValidationError,
            APIConnectionError,
            APIStatusError,
        ]

        for exc_class in exceptions:
            assert issubclass(exc_class, SecureSDKError)

    def test_key_not_found_inherits_from_key_load_error(self):
        """Test that KeyNotFoundError inherits from KeyLoadError."""
        assert issubclass(KeyNotFoundError, KeyLoadError)

    def test_network_errors_inherit_from_api_connection_error(self):
        """Test network errors inherit from APIConnectionError."""
        network_errors = [
            APITimeoutError,
            DNSError,
            ConnectionRefusedError,
            SSLError,
            ProxyError,
        ]

        for exc_class in network_errors:
            assert issubclass(exc_class, APIConnectionError)

    def test_http_errors_inherit_from_api_status_error(self):
        """Test HTTP errors inherit from APIStatusError."""
        http_errors = [
            BadRequestError,
            AuthenticationError,
            PermissionError,
            NotFoundError,
            ConflictError,
            UnprocessableEntityError,
            RateLimitError,
            InternalServerError,
            ServiceUnavailableError,
            GatewayTimeoutError,
        ]

        for exc_class in http_errors:
            assert issubclass(exc_class, APIStatusError)


class TestExceptionMessages:
    """Test exception message handling."""

    def test_base_exception_with_message(self):
        """Test base exception with custom message."""
        error = SecureSDKError("Test error message")
        assert str(error) == "Test error message"

    def test_key_load_error_with_message(self):
        """Test KeyLoadError with message."""
        error = KeyLoadError("Failed to load key")
        assert "Failed to load key" in str(error)

    def test_key_not_found_error_with_message(self):
        """Test KeyNotFoundError with message."""
        error = KeyNotFoundError("Key not found at path")
        assert "Key not found at path" in str(error)

    def test_api_connection_error_with_message(self):
        """Test APIConnectionError with message."""
        error = APIConnectionError("Connection failed")
        assert "Connection failed" in str(error)


class TestStatusCodeMapping:
    """Test HTTP status code to exception mapping."""

    def test_get_exception_for_400(self):
        """Test mapping for 400 Bad Request."""
        exc_class = get_exception_for_status_code(400)
        assert exc_class == BadRequestError

    def test_get_exception_for_401(self):
        """Test mapping for 401 Unauthorized."""
        exc_class = get_exception_for_status_code(401)
        assert exc_class == AuthenticationError

    def test_get_exception_for_403(self):
        """Test mapping for 403 Forbidden."""
        exc_class = get_exception_for_status_code(403)
        assert exc_class == PermissionError

    def test_get_exception_for_404(self):
        """Test mapping for 404 Not Found."""
        exc_class = get_exception_for_status_code(404)
        assert exc_class == NotFoundError

    def test_get_exception_for_409(self):
        """Test mapping for 409 Conflict."""
        exc_class = get_exception_for_status_code(409)
        assert exc_class == ConflictError

    def test_get_exception_for_422(self):
        """Test mapping for 422 Unprocessable Entity."""
        exc_class = get_exception_for_status_code(422)
        assert exc_class == UnprocessableEntityError

    def test_get_exception_for_429(self):
        """Test mapping for 429 Too Many Requests."""
        exc_class = get_exception_for_status_code(429)
        assert exc_class == RateLimitError

    def test_get_exception_for_500(self):
        """Test mapping for 500 Internal Server Error."""
        exc_class = get_exception_for_status_code(500)
        assert exc_class == InternalServerError

    def test_get_exception_for_503(self):
        """Test mapping for 503 Service Unavailable."""
        exc_class = get_exception_for_status_code(503)
        assert exc_class == ServiceUnavailableError

    def test_get_exception_for_504(self):
        """Test mapping for 504 Gateway Timeout."""
        exc_class = get_exception_for_status_code(504)
        assert exc_class == GatewayTimeoutError

    def test_get_exception_for_unknown_status(self):
        """Test mapping for unknown status code."""
        exc_class = get_exception_for_status_code(999)
        assert exc_class == APIStatusError


class TestExceptionRaising:
    """Test raising exceptions with proper context."""

    def test_raise_key_load_error(self):
        """Test raising KeyLoadError."""
        with pytest.raises(KeyLoadError) as exc_info:
            raise KeyLoadError("Test key load error")

        assert "Test key load error" in str(exc_info.value)

    def test_raise_key_not_found_error(self):
        """Test raising KeyNotFoundError."""
        with pytest.raises(KeyNotFoundError) as exc_info:
            raise KeyNotFoundError("Key not found")

        assert "Key not found" in str(exc_info.value)

    def test_catch_key_not_found_as_key_load_error(self):
        """Test that KeyNotFoundError can be caught as KeyLoadError."""
        with pytest.raises(KeyLoadError):
            raise KeyNotFoundError("Test")

    def test_raise_api_connection_error(self):
        """Test raising APIConnectionError."""
        with pytest.raises(APIConnectionError) as exc_info:
            raise APIConnectionError("Connection failed")

        assert "Connection failed" in str(exc_info.value)

    def test_raise_signing_error(self):
        """Test raising SigningError."""
        with pytest.raises(SigningError) as exc_info:
            raise SigningError("Signature generation failed")

        assert "Signature generation failed" in str(exc_info.value)

    def test_catch_all_as_secure_sdk_error(self):
        """Test that all SDK exceptions can be caught as SecureSDKError."""
        exceptions = [
            KeyLoadError("test"),
            KeyNotFoundError("test"),
            SigningError("test"),
            APIConnectionError("test"),
            BadRequestError("test"),
        ]

        for exc in exceptions:
            with pytest.raises(SecureSDKError):
                raise exc
