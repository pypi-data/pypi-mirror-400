"""
HTTP request canonicalization for signature generation.

This module implements the canonical request format that MUST match
the server-side implementation exactly, or signatures will fail.
"""

import hashlib
from typing import Union
from urllib.parse import parse_qsl, urlencode

from .exceptions import CanonicalizationError


def build_canonical_string(
    method: str,
    path: str,
    query: Union[str, dict, None],
    body_bytes: bytes,
    timestamp: str,
    nonce: str,
) -> bytes:
    """
    Build canonical string for signature generation.

    The canonical format is:
        METHOD
        PATH
        QUERY_PARAMS (sorted alphabetically)
        SHA256(BODY)
        TIMESTAMP
        NONCE

    This format MUST match the server implementation exactly.

    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        path: Request path (e.g., "/api/v1/endpoint")
        query: Query parameters as dict or string (e.g., {"page": 1} or "page=1")
        body_bytes: Raw request body as bytes (use b"" for GET requests)
        timestamp: Unix timestamp as string (e.g., "1234567890")
        nonce: Unique nonce, typically UUID (e.g., "550e8400-e29b-41d4-a716-446655440000")

    Returns:
        Canonical string as UTF-8 encoded bytes

    Raises:
        CanonicalizationError: If canonicalization fails

    Examples:
        >>> canonical = build_canonical_string(
        ...     method="GET",
        ...     path="/api/v1/users",
        ...     query={"page": 1, "limit": 10},
        ...     body_bytes=b"",
        ...     timestamp="1234567890",
        ...     nonce="550e8400-e29b-41d4-a716-446655440000"
        ... )
        >>> print(canonical.decode())
        GET
        /api/v1/users
        limit=10&page=1
        e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
        1234567890
        550e8400-e29b-41d4-a716-446655440000
    """
    try:
        method = method.upper().strip()
        path = path.strip()
        if not path.startswith("/"):
            path = "/" + path

        if query:
            if isinstance(query, str):
                params = parse_qsl(query, keep_blank_values=True)
            elif isinstance(query, dict):
                params = list(query.items())
            else:
                params = []

            params.sort(key=lambda x: (x[0], x[1]))
            normalized_query = urlencode(params)
        else:
            normalized_query = ""

        if body_bytes is None:
            body_bytes = b""

        if isinstance(body_bytes, str):
            body_bytes = body_bytes.encode("utf-8")

        body_hash = hashlib.sha256(body_bytes).hexdigest()
        canonical_str = (
            f"{method}\n"
            f"{path}\n"
            f"{normalized_query}\n"
            f"{body_hash}\n"
            f"{timestamp}\n"
            f"{nonce}"
        )
        return canonical_str.encode("utf-8")

    except Exception as e:
        raise CanonicalizationError(f"Failed to build canonical string: {str(e)}")
