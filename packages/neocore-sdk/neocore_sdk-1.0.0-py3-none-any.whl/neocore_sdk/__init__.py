# src/neocore_sdk/__init__.py

"""
NeoCore Security SDK - Official Python client for NeoCore API authentication.

This SDK provides secure request signing using Ed25519 digital signatures.
All requests are automatically signed with your private key, and the server
verifies signatures using your registered public key.

Basic usage:
    >>> from neocore_sdk import NeoCoreClient
    >>> client = NeoCoreClient(key_id="your-key-id")
    >>> response = client.get("/api/v1/users")
"""

from .client import NeoCoreClient
from .exceptions import (
    # Base exceptions
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

__version__ = "1.0.0"

__all__ = [
    # Main client
    "NeoCoreClient",
    # Base exceptions
    "SecureSDKError",
    # Key errors
    "KeyLoadError",
    "KeyNotFoundError",
    # Signing errors
    "SigningError",
    "CanonicalizationError",
    # Validation errors
    "ValidationError",
    # Network errors
    "APIConnectionError",
    "APITimeoutError",
    "DNSError",
    "ConnectionRefusedError",
    "SSLError",
    "ProxyError",
    # HTTP status errors
    "APIStatusError",
    "BadRequestError",
    "AuthenticationError",
    "PermissionError",
    "NotFoundError",
    "ConflictError",
    "UnprocessableEntityError",
    "RateLimitError",
    "InternalServerError",
    "ServiceUnavailableError",
    "GatewayTimeoutError",
    # Helper function
    "get_exception_for_status_code",
    # Version
    "__version__",
]
