"""
Secure HTTP client for NeoCore API with automatic request signing.
"""

import json
import time
import uuid
from typing import Optional

import requests

from .canonicalization import build_canonical_string
from .crypto import sign_payload
from .exceptions import (
    APIConnectionError,
    APITimeoutError,
    ConnectionRefusedError,
    DNSError,
    SSLError,
    get_exception_for_status_code,
)
from .key_loader import load_ed25519_private_key


class NeoCoreClient:
    """
    Secure HTTP client for NeoCore API.

    Automatically signs all requests with Ed25519 signatures using your private key.
    The server verifies signatures using your registered public key.

    Examples:
        Basic usage (uses default NeoCore API URL):
        >>> client = NeoCoreClient(key_id="your-key-id")
        >>> response = client.get("/api/v1/users")

        Custom base URL:
        >>> client = NeoCoreClient(
        ...     key_id="your-key-id",
        ...     base_url="https://custom-api.example.com"
        ... )

        Custom key path:
        >>> client = NeoCoreClient(
        ...     key_id="your-key-id",
        ...     private_key_path="/secure/vault/key.pem"
        ... )
    """

    def __init__(
        self,
        key_id: str,
        base_url: str = "https://api.neosapien.xyz",
        private_key_path: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize secure client.

        Args:
            key_id: Your registered developer key ID
            base_url: API base URL (default: "https://api.neosapien.xyz")
                     Trailing slash is automatically removed.
                     Override for custom deployments or different environments.
            private_key_path: Path to Ed25519 private key PEM file.
                            If None, searches default OS-specific locations.
            timeout: Request timeout in seconds (default: 30)

        Raises:
            KeyLoadError: If private key cannot be loaded
            KeyNotFoundError: If no key found in default locations (when path=None)
        """
        self.base_url = base_url.rstrip("/")
        self.key_id = key_id
        self.timeout = timeout
        self.session = requests.Session()
        self.private_key = load_ed25519_private_key(private_key_path)

    def _execute_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
    ) -> requests.Response:
        """
        Execute signed HTTP request.

        This method:
        1. Prepares request body
        2. Generates timestamp and nonce
        3. Builds canonical string
        4. Signs with private key
        5. Adds signature headers
        6. Sends HTTP request
        7. Checks response status and raises detailed exceptions for errors

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint path (e.g., "/api/v1/users")
            params: Query parameters dict (optional)
            json_data: JSON body data dict (optional)

        Returns:
            requests.Response object (only for successful 2xx/3xx responses)

        Raises:
            SigningError: If signature generation fails
            CanonicalizationError: If request canonicalization fails

            Network errors:
            APITimeoutError: If request times out
            DNSError: If DNS resolution fails
            ConnectionRefusedError: If server refuses connection
            SSLError: If SSL/TLS verification fails
            APIConnectionError: If connection fails (generic)

            HTTP status errors (4xx/5xx):
            BadRequestError: HTTP 400 - Malformed request
            AuthenticationError: HTTP 401 - Invalid authentication
            PermissionError: HTTP 403 - Insufficient permissions
            NotFoundError: HTTP 404 - Resource not found
            ConflictError: HTTP 409 - Resource conflict
            UnprocessableEntityError: HTTP 422 - Validation error
            RateLimitError: HTTP 429 - Rate limit exceeded
            InternalServerError: HTTP 500 - Server error
            ServiceUnavailableError: HTTP 503 - Service unavailable
            GatewayTimeoutError: HTTP 504 - Gateway timeout
            APIStatusError: Other HTTP errors
        """
        endpoint = endpoint.strip()

        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint

        endpoint = endpoint.rstrip("/")

        if not endpoint:
            endpoint = "/"

        url = f"{self.base_url}{endpoint}"
        body_bytes = b""

        if json_data is not None:
            body_bytes = json.dumps(json_data, separators=(",", ":")).encode("utf-8")

        timestamp = str(int(time.time()))
        nonce = str(uuid.uuid4())
        canonical_data = build_canonical_string(
            method=method,
            path=endpoint,
            query=params,
            body_bytes=body_bytes,
            timestamp=timestamp,
            nonce=nonce,
        )
        signature = sign_payload(self.private_key, canonical_data)
        headers = {
            "Content-Type": "application/json",
            "X-Key-Id": self.key_id,
            "X-Timestamp": timestamp,
            "X-Nonce": nonce,
            "X-Signature": signature,
        }
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=body_bytes,
                headers=headers,
                timeout=self.timeout,
            )

            if response.status_code >= 400:
                response_body = response.text
                response_json = None
                try:
                    response_json = response.json()
                except Exception:
                    pass  # Response not JSON

                exc_class = get_exception_for_status_code(response.status_code)

                request_id = response.headers.get("X-Request-Id") or response.headers.get(
                    "x-request-id"
                )

                message = response.reason
                if response_json:
                    message = (
                        response_json.get("message")
                        or response_json.get("error")
                        or response_json.get("detail")
                        or response.reason
                    )

                raise exc_class(
                    message,
                    status_code=response.status_code,
                    response_body=response_body,
                    response_json=response_json,
                    headers=dict(response.headers),
                    request_id=request_id,
                )

            return response

        except requests.Timeout as e:
            timeout_type = "connect" if "connect" in str(e).lower() else "read"
            raise APITimeoutError(
                "Request timed out",
                url=url,
                timeout=self.timeout,
                timeout_type=timeout_type,
            ) from e

        except requests.exceptions.SSLError as e:
            raise SSLError(
                "SSL/TLS verification failed",
                url=url,
                should_retry=False,
            ) from e

        except requests.exceptions.ConnectionError as e:
            error_str = str(e).lower()

            if "name or service not known" in error_str or "nodename nor servname" in error_str or "getaddrinfo failed" in error_str:
                from urllib.parse import urlparse
                hostname = urlparse(url).hostname or url
                raise DNSError(
                    "DNS resolution failed",
                    hostname=hostname,
                    url=url,
                ) from e

            elif "connection refused" in error_str:
                raise ConnectionRefusedError(
                    "Connection refused by server",
                    url=url,
                    should_retry=False,
                ) from e

            else:
                raise APIConnectionError(
                    f"Connection failed: {str(e)}",
                    url=url,
                    should_retry=True,
                ) from e

        except requests.RequestException as e:
            raise APIConnectionError(
                f"Request failed: {str(e)}",
                url=url,
                should_retry=False,
            ) from e

    def get(self, endpoint: str, params: Optional[dict] = None) -> requests.Response:
        """
        Send signed GET request.

        Args:
            endpoint: API endpoint (e.g., "/api/v1/users")
            params: Query parameters (e.g., {"page": 1, "limit": 10})

        Returns:
            Response object

        Examples:
            >>> response = client.get("/api/v1/users")
            >>> response = client.get("/api/v1/users", params={"page": 2})
        """
        return self._execute_request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[dict] = None) -> requests.Response:
        """
        Send signed POST request.

        Args:
            endpoint: API endpoint (e.g., "/api/v1/users")
            data: JSON body data (e.g., {"name": "John", "email": "john@example.com"})

        Returns:
            Response object

        Examples:
            >>> response = client.post("/api/v1/users", data={"name": "John"})
        """
        return self._execute_request("POST", endpoint, json_data=data)

    def put(self, endpoint: str, data: Optional[dict] = None) -> requests.Response:
        """
        Send signed PUT request.

        Args:
            endpoint: API endpoint (e.g., "/api/v1/users/123")
            data: JSON body data

        Returns:
            Response object

        Examples:
            >>> response = client.put("/api/v1/users/123", data={"name": "John Doe"})
        """
        return self._execute_request("PUT", endpoint, json_data=data)

    def patch(self, endpoint: str, data: Optional[dict] = None) -> requests.Response:
        """
        Send signed PATCH request.

        Args:
            endpoint: API endpoint (e.g., "/api/v1/users/123")
            data: JSON body data

        Returns:
            Response object

        Examples:
            >>> response = client.patch("/api/v1/users/123", data={"email": "new@example.com"})
        """
        return self._execute_request("PATCH", endpoint, json_data=data)

    def delete(self, endpoint: str, params: Optional[dict] = None) -> requests.Response:
        """
        Send signed DELETE request.

        Args:
            endpoint: API endpoint (e.g., "/api/v1/users/123")
            params: Query parameters (optional)

        Returns:
            Response object

        Examples:
            >>> response = client.delete("/api/v1/users/123")
        """
        return self._execute_request("DELETE", endpoint, params=params)
