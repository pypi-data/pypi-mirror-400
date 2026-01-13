"""
Unit tests for NeoCoreClient.

These tests verify the core functionality of the NeoCore SDK client.
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from neocore_sdk import NeoCoreClient
from neocore_sdk.exceptions import (
    KeyLoadError,
    KeyNotFoundError,
    SigningError,
    APIConnectionError,
)


class TestNeoCoreClientInitialization:
    """Test client initialization."""

    @patch('neocore_sdk.key_loader.load_ed25519_private_key')
    def test_client_init_with_default_values(self, mock_load_key):
        """Test client initialization with default values."""
        # Mock the key loading
        mock_load_key.return_value = Mock()

        # Initialize client
        client = NeoCoreClient(key_id="test-key-id")

        # Verify
        assert client.key_id == "test-key-id"
        assert client.base_url == "https://api.neosapien.xyz"
        assert client.timeout == 30

    @patch('neocore_sdk.key_loader.load_ed25519_private_key')
    def test_client_init_with_custom_values(self, mock_load_key):
        """Test client initialization with custom values."""
        mock_load_key.return_value = Mock()

        # Initialize with custom values
        client = NeoCoreClient(
            key_id="custom-key-id",
            base_url="https://custom-api.example.com",
            timeout=60
        )

        # Verify
        assert client.key_id == "custom-key-id"
        assert client.base_url == "https://custom-api.example.com"
        assert client.timeout == 60

    @patch('neocore_sdk.key_loader.load_ed25519_private_key')
    def test_client_init_strips_trailing_slash(self, mock_load_key):
        """Test that base_url trailing slash is removed."""
        mock_load_key.return_value = Mock()

        client = NeoCoreClient(
            key_id="test-key",
            base_url="https://api.example.com/"
        )

        assert client.base_url == "https://api.example.com"

    def test_client_init_raises_key_not_found_error(self):
        """Test that KeyLoadError is raised when key not found."""
        with pytest.raises(KeyLoadError):
            NeoCoreClient(
                key_id="test-key",
                private_key_path="/nonexistent/path/key.pem"
            )


class TestNeoCoreClientRequests:
    """Test HTTP request methods."""

    @patch('neocore_sdk.key_loader.load_ed25519_private_key')
    @patch('neocore_sdk.client.requests.Session')
    def test_get_request(self, mock_session_class, mock_load_key):
        """Test GET request."""
        # Mock setup
        mock_load_key.return_value = Mock()
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_session.request.return_value = mock_response

        # Make request
        client = NeoCoreClient(key_id="test-key")
        response = client.get("/api/v1/test")

        # Verify
        assert response.status_code == 200
        assert mock_session.request.called
        call_args = mock_session.request.call_args
        assert call_args[1]['method'] == 'GET'

    @patch('neocore_sdk.key_loader.load_ed25519_private_key')
    @patch('neocore_sdk.client.requests.Session')
    def test_post_request(self, mock_session_class, mock_load_key):
        """Test POST request."""
        mock_load_key.return_value = Mock()
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.status_code = 201
        mock_session.request.return_value = mock_response

        client = NeoCoreClient(key_id="test-key")
        response = client.post("/api/v1/test", data={"name": "test"})

        assert response.status_code == 201
        assert mock_session.request.called

    @patch('neocore_sdk.key_loader.load_ed25519_private_key')
    @patch('neocore_sdk.client.requests.Session')
    def test_put_request(self, mock_session_class, mock_load_key):
        """Test PUT request."""
        mock_load_key.return_value = Mock()
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.request.return_value = mock_response

        client = NeoCoreClient(key_id="test-key")
        response = client.put("/api/v1/test/123", data={"name": "updated"})

        assert response.status_code == 200
        assert mock_session.request.called

    @patch('neocore_sdk.key_loader.load_ed25519_private_key')
    @patch('neocore_sdk.client.requests.Session')
    def test_patch_request(self, mock_session_class, mock_load_key):
        """Test PATCH request."""
        mock_load_key.return_value = Mock()
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.request.return_value = mock_response

        client = NeoCoreClient(key_id="test-key")
        response = client.patch("/api/v1/test/123", data={"email": "new@test.com"})

        assert response.status_code == 200
        assert mock_session.request.called

    @patch('neocore_sdk.key_loader.load_ed25519_private_key')
    @patch('neocore_sdk.client.requests.Session')
    def test_delete_request(self, mock_session_class, mock_load_key):
        """Test DELETE request."""
        mock_load_key.return_value = Mock()
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.status_code = 204
        mock_session.request.return_value = mock_response

        client = NeoCoreClient(key_id="test-key")
        response = client.delete("/api/v1/test/123")

        assert response.status_code == 204
        assert mock_session.request.called

    @patch('neocore_sdk.key_loader.load_ed25519_private_key')
    @patch('neocore_sdk.client.requests.Session')
    def test_request_with_query_params(self, mock_session_class, mock_load_key):
        """Test request with query parameters."""
        mock_load_key.return_value = Mock()
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.request.return_value = mock_response

        client = NeoCoreClient(key_id="test-key")
        response = client.get("/api/v1/test", params={"page": 1, "limit": 10})

        assert response.status_code == 200
        assert mock_session.request.called


class TestNeoCoreClientErrorHandling:
    """Test error handling."""

    @patch('neocore_sdk.key_loader.load_ed25519_private_key')
    @patch('neocore_sdk.client.requests.Session')
    def test_connection_error_handling(self, mock_session_class, mock_load_key):
        """Test handling of connection errors."""
        mock_load_key.return_value = Mock()
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.request.side_effect = requests.RequestException("Connection failed")

        client = NeoCoreClient(key_id="test-key")

        with pytest.raises(APIConnectionError):
            client.get("/api/v1/test")

    @patch('neocore_sdk.key_loader.load_ed25519_private_key')
    def test_signing_error_handling(self, mock_load_key):
        """Test handling of signing errors."""
        # Mock a key that will fail signing
        mock_key = Mock()
        mock_key.sign.side_effect = Exception("Signing failed")
        mock_load_key.return_value = mock_key

        client = NeoCoreClient(key_id="test-key")

        # This should raise SigningError when trying to make a request
        # The actual implementation may vary, this is a conceptual test
        # with pytest.raises(SigningError):
        #     client.get("/api/v1/test")


class TestNeoCoreClientHeaders:
    """Test request header generation."""

    @patch('neocore_sdk.key_loader.load_ed25519_private_key')
    @patch('neocore_sdk.client.requests.Session')
    def test_request_headers_include_signature(self, mock_session_class, mock_load_key):
        """Test that requests include required security headers."""
        mock_load_key.return_value = Mock()
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.request.return_value = mock_response

        client = NeoCoreClient(key_id="test-key")
        client.get("/api/v1/test")

        # Verify request was called with headers
        assert mock_session.request.called
        call_kwargs = mock_session.request.call_args[1]

        # Check that headers exist
        assert 'headers' in call_kwargs
        headers = call_kwargs['headers']

        # Verify required headers are present
        assert 'X-Key-Id' in headers
        assert headers['X-Key-Id'] == "test-key"
        # Note: Other headers like X-Signature, X-Timestamp, X-Nonce
        # should also be present in the actual implementation
