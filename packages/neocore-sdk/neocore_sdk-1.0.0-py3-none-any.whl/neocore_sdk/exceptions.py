"""
Comprehensive exception hierarchy for NeoCore Security SDK.

This module provides industry-grade error handling with:
- HTTP status-specific exceptions
- Rich error context (request ID, response body, headers)
- Network-specific error handling
- Actionable error messages with suggestions
- Debug information for troubleshooting
"""

from typing import Any, Dict, Optional


class SecureSDKError(Exception):
    """
    Base exception for all NeoCore Security SDK errors.

    All SDK exceptions inherit from this class, allowing you to catch
    all SDK-specific errors with a single except clause.

    Attributes:
        message: Human-readable error description
        request_id: Unique request identifier for support/debugging (if available)

    Examples:
        >>> try:
        ...     client.get("/api/v1/users")
        ... except SecureSDKError as e:
        ...     print(f"SDK error: {e}")
    """

    def __init__(self, message: str, *, request_id: Optional[str] = None):
        self.message = message
        self.request_id = request_id
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format error message with request ID if available."""

        parts = [self.message]
        if self.request_id:
            parts.append(f"(request_id: {self.request_id})")
        return " ".join(parts)

    def __str__(self) -> str:
        return self._format_message()

# ============================================================================
# Key Loading Errors
# ============================================================================

class KeyLoadError(SecureSDKError):
    """
    Raised when private key cannot be loaded or is invalid.

    This error occurs when:
    - Key file doesn't exist
    - Key file is not readable (permissions issue)
    - Key file contains invalid PEM data
    - Key is not an Ed25519 key

    Attributes:
        key_path: Path to the key file that failed to load
        reason: Specific reason for the failure

    Examples:
        >>> try:
        ...     client = NeoCoreClient(key_id="...", private_key_path="/bad/path.pem")
        ... except KeyLoadError as e:
        ...     print(f"Key error: {e.message}")
        ...     print(f"Path: {e.key_path}")
    """

    def __init__(
        self,
        message: str,
        *,
        key_path: Optional[str] = None,
        reason: Optional[str] = None,
    ):
        self.key_path = key_path
        self.reason = reason
        super().__init__(message)

    def _format_message(self) -> str:
        parts = [self.message]
        if self.key_path:
            parts.append(f"\nKey path: {self.key_path}")
        if self.reason:
            parts.append(f"\nReason: {self.reason}")
        parts.append(
            "\n\nSuggested fix: Verify the key file exists and is readable."
            "\nGenerate new keys with: neocore-keygen"
        )
        return "".join(parts)


class KeyNotFoundError(KeyLoadError):
    """
    Raised when no private key found in default locations.

    This is a specialized KeyLoadError that occurs only when auto-discovery
    fails (i.e., no explicit key path was provided).

    Attributes:
        searched_paths: List of paths that were searched

    Examples:
        >>> try:
        ...     client = NeoCoreClient(key_id="...")  # No key_path provided
        ... except KeyNotFoundError as e:
        ...     print(f"Key not found. Searched: {e.searched_paths}")
    """

    def __init__(self, message: str, *, searched_paths: Optional[list] = None):
        self.searched_paths = searched_paths or []
        super().__init__(message)

    def _format_message(self) -> str:
        parts = [self.message]
        if self.searched_paths:
            paths_str = "\n  - ".join(str(p) for p in self.searched_paths)
            parts.append(f"\n\nSearched locations:\n  - {paths_str}")
        parts.append(
            "\n\nSuggested fix:"
            "\n1. Generate keys: neocore-keygen"
            "\n2. Or specify explicit path: NeoCoreClient(key_id='...', private_key_path='/path/to/key.pem')"
        )
        return "".join(parts)

# ============================================================================
# Signing Errors
# ============================================================================

class SigningError(SecureSDKError):
    """
    Raised when signature generation fails.

    This error occurs when the cryptographic signing process fails,
    typically due to:
    - Corrupted private key
    - Invalid payload data
    - Cryptography library errors

    Examples:
        >>> try:
        ...     response = client.post("/api/v1/data", data={"key": "value"})
        ... except SigningError as e:
        ...     print(f"Signing failed: {e}")
    """

    pass

# ============================================================================
# Canonicalization Errors
# ============================================================================

class CanonicalizationError(SecureSDKError):
    """
    Raised when request canonicalization fails.

    Canonicalization is the process of building a standardized string
    representation of the request for signing. This error is rare and
    typically indicates:
    - Invalid characters in request parameters
    - Encoding issues
    - Internal SDK bug

    Attributes:
        component: Which component failed (e.g., "query_params", "body")

    Examples:
        >>> try:
        ...     response = client.get("/api/v1/users")
        ... except CanonicalizationError as e:
        ...     print(f"Canonicalization failed: {e}")
    """

    def __init__(
        self, message: str, *, component: Optional[str] = None, request_id: Optional[str] = None
    ):
        self.component = component
        super().__init__(message, request_id=request_id)

    def _format_message(self) -> str:
        parts = [self.message]
        if self.component:
            parts.append(f"\nFailed component: {self.component}")
        if self.request_id:
            parts.append(f"\nRequest ID: {self.request_id}")
        parts.append(
            "\n\nThis is unusual. Please report this issue:"
            "\nhttps://github.com/NeoSapien-xyz/neocore-sdk/issues"
        )
        return "".join(parts)

# ============================================================================
# Input Validation Errors
# ============================================================================

class ValidationError(SecureSDKError):
    """
    Raised when input validation fails before making API request.

    This error prevents invalid requests from being sent to the server,
    saving time and API quota.

    Attributes:
        param: Parameter name that failed validation
        value: Invalid value provided
        expected: Description of expected format/value
        example: Example of valid value

    Examples:
        >>> try:
        ...     client.get("invalid_endpoint")  # Missing leading slash
        ... except ValidationError as e:
        ...     print(f"Invalid {e.param}: {e.value}")
        ...     print(f"Expected: {e.expected}")
        ...     print(f"Example: {e.example}")
    """

    def __init__(
        self,
        message: str,
        *,
        param: Optional[str] = None,
        value: Any = None,
        expected: Optional[str] = None,
        example: Optional[str] = None,
    ):
        self.param = param
        self.value = value
        self.expected = expected
        self.example = example
        super().__init__(message)

    def _format_message(self) -> str:
        parts = [self.message]
        if self.param:
            parts.append(f"\nParameter: {self.param}")
        if self.value is not None:
            # Truncate very long values
            value_str = str(self.value)
            if len(value_str) > 100:
                value_str = value_str[:97] + "..."
            parts.append(f"\nProvided value: {repr(value_str)}")
        if self.expected:
            parts.append(f"\nExpected: {self.expected}")
        if self.example:
            parts.append(f"\nExample: {self.example}")
        return "".join(parts)

# ============================================================================
# Network/Connection Errors
# ============================================================================

class APIConnectionError(SecureSDKError):
    """
    Base class for API connection errors.

    This is the parent class for all network-related errors. Catch this
    to handle any network issue generically.

    Attributes:
        url: The URL that failed to connect
        should_retry: Whether this error is transient and retryable

    Examples:
        >>> try:
        ...     response = client.get("/api/v1/users")
        ... except APIConnectionError as e:
        ...     if e.should_retry:
        ...         # Implement retry logic
        ...         pass
    """

    def __init__(
        self,
        message: str,
        *,
        url: Optional[str] = None,
        should_retry: bool = False,
        request_id: Optional[str] = None,
    ):
        self.url = url
        self.should_retry = should_retry
        super().__init__(message, request_id=request_id)

    def _format_message(self) -> str:
        parts = [self.message]
        if self.url:
            parts.append(f"\nURL: {self.url}")
        if self.should_retry:
            parts.append("\n\nThis is a transient error. Retry with exponential backoff.")
        else:
            parts.append(
                "\n\nSuggested fix: Check network connectivity and base_url configuration."
            )
        if self.request_id:
            parts.append(f"\nRequest ID: {self.request_id}")
        return "".join(parts)


class APITimeoutError(APIConnectionError):
    """
    Raised when request times out.

    This error occurs when:
    - Connection attempt takes too long (ConnectTimeout)
    - Server doesn't respond within timeout period (ReadTimeout)

    Attributes:
        timeout: Timeout value that was exceeded (seconds)
        timeout_type: "connect" or "read"

    Examples:
        >>> try:
        ...     client = NeoCoreClient(key_id="...", timeout=5)
        ...     response = client.get("/api/v1/slow-endpoint")
        ... except APITimeoutError as e:
        ...     print(f"Timeout after {e.timeout}s ({e.timeout_type})")
    """

    def __init__(
        self,
        message: str,
        *,
        url: Optional[str] = None,
        timeout: Optional[int] = None,
        timeout_type: str = "request",
        request_id: Optional[str] = None,
    ):
        self.timeout = timeout
        self.timeout_type = timeout_type
        super().__init__(message, url=url, should_retry=True, request_id=request_id)

    def _format_message(self) -> str:
        parts = [self.message]
        if self.timeout:
            parts.append(f"\nTimeout: {self.timeout}s ({self.timeout_type})")
        if self.url:
            parts.append(f"\nURL: {self.url}")
        parts.append(
            "\n\nSuggested fixes:"
            "\n1. Increase timeout: NeoCoreClient(key_id='...', timeout=60)"
            "\n2. Check server response time"
            "\n3. Retry the request"
        )
        if self.request_id:
            parts.append(f"\nRequest ID: {self.request_id}")
        return "".join(parts)


class DNSError(APIConnectionError):
    """
    Raised when DNS resolution fails.

    This error indicates that the hostname in base_url cannot be resolved to an IP address.

    Attributes:
        hostname: The hostname that failed to resolve

    Examples:
        >>> try:
        ...     client = NeoCoreClient(key_id="...", base_url="https://nonexistent.example.com")
        ...     response = client.get("/api/v1/users")
        ... except DNSError as e:
        ...     print(f"Cannot resolve: {e.hostname}")
    """

    def __init__(self, message: str, *, hostname: Optional[str] = None, url: Optional[str] = None):
        self.hostname = hostname
        super().__init__(message, url=url, should_retry=False)

    def _format_message(self) -> str:
        parts = [self.message]
        if self.hostname:
            parts.append(f"\nHostname: {self.hostname}")
        parts.append(
            "\n\nSuggested fixes:"
            "\n1. Verify base_url is correct"
            "\n2. Check DNS configuration"
            "\n3. Test with: ping {hostname}".format(hostname=self.hostname or "<hostname>")
        )
        return "".join(parts)


class ConnectionRefusedError(APIConnectionError):
    """
    Raised when connection is actively refused by the server.

    This typically means:
    - Server is not running
    - Firewall is blocking the connection
    - Wrong port number

    Examples:
        >>> try:
        ...     client = NeoCoreClient(key_id="...", base_url="https://localhost:9999")
        ...     response = client.get("/api/v1/users")
        ... except ConnectionRefusedError as e:
        ...     print(f"Server refused connection: {e}")
    """

    def __init__(self, message: str, *, url: Optional[str] = None):
        super().__init__(message, url=url, should_retry=False)

    def _format_message(self) -> str:
        parts = [self.message]
        if self.url:
            parts.append(f"\nURL: {self.url}")
        parts.append(
            "\n\nSuggested fixes:"
            "\n1. Verify the server is running"
            "\n2. Check base_url and port number"
            "\n3. Check firewall settings"
        )
        return "".join(parts)


class SSLError(APIConnectionError):
    """
    Raised when SSL/TLS verification fails.

    This error occurs when:
    - SSL certificate is invalid or expired
    - Hostname doesn't match certificate
    - Certificate chain is broken
    - Self-signed certificate without verification disabled

    Examples:
        >>> try:
        ...     response = client.get("/api/v1/users")
        ... except SSLError as e:
        ...     print(f"SSL error: {e}")
    """

    def __init__(self, message: str, *, url: Optional[str] = None):
        super().__init__(message, url=url, should_retry=False)

    def _format_message(self) -> str:
        parts = [self.message]
        if self.url:
            parts.append(f"\nURL: {self.url}")
        parts.append(
            "\n\nSuggested fixes:"
            "\n1. Verify server has valid SSL certificate"
            "\n2. Check system time is correct"
            "\n3. Update CA certificates: pip install --upgrade certifi"
        )
        return "".join(parts)


class ProxyError(APIConnectionError):
    """
    Raised when proxy connection fails.

    This error occurs when requests are configured to use a proxy but
    the proxy connection fails.

    Examples:
        >>> try:
        ...     response = client.get("/api/v1/users")
        ... except ProxyError as e:
        ...     print(f"Proxy error: {e}")
    """

    def __init__(self, message: str, *, url: Optional[str] = None):
        super().__init__(message, url=url, should_retry=False)

    def _format_message(self) -> str:
        parts = [self.message]
        if self.url:
            parts.append(f"\nURL: {self.url}")
        parts.append(
            "\n\nSuggested fixes:"
            "\n1. Verify proxy configuration"
            "\n2. Check HTTP_PROXY and HTTPS_PROXY environment variables"
            "\n3. Test proxy connectivity"
        )
        return "".join(parts)

# ============================================================================
# HTTP Status Code Errors
# ============================================================================

class APIStatusError(SecureSDKError):
    """
    Base class for HTTP status code errors.

    Raised when server returns 4xx or 5xx status codes.

    Attributes:
        status_code: HTTP status code (e.g., 400, 404, 500)
        response_body: Raw response body (string)
        response_json: Parsed JSON response (if available)
        headers: Response headers dict
        request_id: Server's request ID from X-Request-Id header

    Examples:
        >>> try:
        ...     response = client.get("/api/v1/users")
        ...     response.raise_for_status()  # Manual raising
        ... except APIStatusError as e:
        ...     print(f"HTTP {e.status_code}: {e.message}")
        ...     print(f"Response: {e.response_body}")
        ...     print(f"Request ID: {e.request_id}")
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        response_body: Optional[str] = None,
        response_json: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        request_id: Optional[str] = None,
    ):
        self.status_code = status_code
        self.response_body = response_body
        self.response_json = response_json or {}
        self.headers = headers or {}

        if not request_id and headers:
            request_id = headers.get("X-Request-Id") or headers.get("x-request-id")

        super().__init__(message, request_id=request_id)

    def _format_message(self) -> str:
        parts = [f"HTTP {self.status_code}: {self.message}"]

        if self.response_json:
            error_msg = self.response_json.get("error") or self.response_json.get("message")
            if error_msg:
                parts.append(f"\nServer message: {error_msg}")
        elif self.response_body:
            body = self.response_body
            if len(body) > 200:
                body = body[:197] + "..."
            parts.append(f"\nResponse: {body}")

        if self.request_id:
            parts.append(f"\nRequest ID: {self.request_id}")
            parts.append(
                "\n\nFor support, provide the request ID above." "\nContact: support@neosapien.xyz"
            )

        return "".join(parts)

# 4xx Client Errors

class BadRequestError(APIStatusError):
    """
    Raised when server returns 400 Bad Request.

    Indicates malformed request or invalid parameters.

    Examples:
        >>> try:
        ...     response = client.post("/api/v1/users", data={"invalid": "data"})
        ... except BadRequestError as e:
        ...     print(f"Bad request: {e.response_json}")
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("status_code", 400)
        super().__init__(*args, **kwargs)


class AuthenticationError(APIStatusError):
    """
    Raised when server returns 401 Unauthorized.

    Indicates:
    - Invalid key_id
    - Invalid signature
    - Expired timestamp
    - Missing authentication headers

    Examples:
        >>> try:
        ...     response = client.get("/api/v1/users")
        ... except AuthenticationError as e:
        ...     print(f"Auth failed: {e}")
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("status_code", 401)
        super().__init__(*args, **kwargs)

    def _format_message(self) -> str:
        msg = super()._format_message()
        msg += (
            "\n\nSuggested fixes:"
            "\n1. Verify key_id is correct"
            "\n2. Ensure private key matches registered public key"
            "\n3. Check system time is synchronized (timestamp validation)"
        )
        return msg


class PermissionError(APIStatusError):
    """
    Raised when server returns 403 Forbidden.

    Indicates authenticated but not authorized for the requested resource.

    Examples:
        >>> try:
        ...     response = client.delete("/api/v1/admin/users")
        ... except PermissionError as e:
        ...     print(f"Forbidden: {e}")
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("status_code", 403)
        super().__init__(*args, **kwargs)


class NotFoundError(APIStatusError):
    """
    Raised when server returns 404 Not Found.

    Indicates the requested resource doesn't exist.

    Examples:
        >>> try:
        ...     response = client.get("/api/v1/users/99999")
        ... except NotFoundError as e:
        ...     print(f"Not found: {e}")
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("status_code", 404)
        super().__init__(*args, **kwargs)


class ConflictError(APIStatusError):
    """
    Raised when server returns 409 Conflict.

    Indicates resource conflict (e.g., duplicate key, version mismatch).

    Examples:
        >>> try:
        ...     response = client.post("/api/v1/users", data={"email": "existing@example.com"})
        ... except ConflictError as e:
        ...     print(f"Conflict: {e}")
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("status_code", 409)
        super().__init__(*args, **kwargs)


class UnprocessableEntityError(APIStatusError):
    """
    Raised when server returns 422 Unprocessable Entity.

    Indicates request syntax is valid but semantically invalid.

    Examples:
        >>> try:
        ...     response = client.post("/api/v1/users", data={"email": "invalid-email"})
        ... except UnprocessableEntityError as e:
        ...     print(f"Validation error: {e.response_json}")
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("status_code", 422)
        super().__init__(*args, **kwargs)


class RateLimitError(APIStatusError):
    """
    Raised when server returns 429 Too Many Requests.

    Indicates rate limit has been exceeded.

    Attributes:
        retry_after: Seconds to wait before retrying (from Retry-After header)

    Examples:
        >>> try:
        ...     response = client.get("/api/v1/users")
        ... except RateLimitError as e:
        ...     print(f"Rate limited. Retry after {e.retry_after}s")
        ...     time.sleep(e.retry_after)
    """

    def __init__(self, *args, retry_after: Optional[int] = None, **kwargs):
        self.retry_after = retry_after
        kwargs.setdefault("status_code", 429)
        super().__init__(*args, **kwargs)

    def _format_message(self) -> str:
        msg = super()._format_message()
        if self.retry_after:
            msg += f"\n\nRetry after: {self.retry_after} seconds"
        else:
            msg += "\n\nRetry with exponential backoff (e.g., 1s, 2s, 4s, 8s...)"
        return msg

# 5xx Server Errors

class InternalServerError(APIStatusError):
    """
    Raised when server returns 500 Internal Server Error.

    Indicates server-side error. Safe to retry.

    Examples:
        >>> try:
        ...     response = client.get("/api/v1/users")
        ... except InternalServerError as e:
        ...     print(f"Server error: {e.request_id}")
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("status_code", 500)
        super().__init__(*args, **kwargs)

    def _format_message(self) -> str:
        msg = super()._format_message()
        msg += "\n\nThis is a server-side error. Safe to retry with exponential backoff."
        return msg


class ServiceUnavailableError(APIStatusError):
    """
    Raised when server returns 503 Service Unavailable.

    Indicates temporary server overload or maintenance.

    Examples:
        >>> try:
        ...     response = client.get("/api/v1/users")
        ... except ServiceUnavailableError as e:
        ...     print(f"Service unavailable: {e}")
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("status_code", 503)
        super().__init__(*args, **kwargs)

    def _format_message(self) -> str:
        msg = super()._format_message()
        msg += (
            "\n\nService temporarily unavailable. Retry with exponential backoff."
            "\nIf issue persists, check status at: https://status.neosapien.xyz"
        )
        return msg


class GatewayTimeoutError(APIStatusError):
    """
    Raised when server returns 504 Gateway Timeout.

    Indicates upstream server timeout.

    Examples:
        >>> try:
        ...     response = client.get("/api/v1/users")
        ... except GatewayTimeoutError as e:
        ...     print(f"Gateway timeout: {e}")
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("status_code", 504)
        super().__init__(*args, **kwargs)

    def _format_message(self) -> str:
        msg = super()._format_message()
        msg += "\n\nGateway timeout. Safe to retry."
        return msg

# ============================================================================
# Exception Mapping
# ============================================================================

STATUS_CODE_TO_EXCEPTION = {
    400: BadRequestError,
    401: AuthenticationError,
    403: PermissionError,
    404: NotFoundError,
    409: ConflictError,
    422: UnprocessableEntityError,
    429: RateLimitError,
    500: InternalServerError,
    503: ServiceUnavailableError,
    504: GatewayTimeoutError,
}


def get_exception_for_status_code(status_code: int) -> type:
    """
    Get the appropriate exception class for an HTTP status code.

    Args:
        status_code: HTTP status code

    Returns:
        Exception class (APIStatusError or more specific subclass)

    Examples:
        >>> exc_class = get_exception_for_status_code(404)
        >>> isinstance(exc_class(), NotFoundError)
        True
        >>> exc_class = get_exception_for_status_code(599)
        >>> isinstance(exc_class(), APIStatusError)
        True
    """
    return STATUS_CODE_TO_EXCEPTION.get(status_code, APIStatusError)
