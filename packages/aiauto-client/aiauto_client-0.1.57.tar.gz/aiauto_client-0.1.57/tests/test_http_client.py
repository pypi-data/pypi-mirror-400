"""Tests for HTTP client module."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from aiauto.http_client import ConnectRPCClient, ConnectRPCError, map_http_error


class TestConnectRPCError:
    """Test ConnectRPCError exception class."""

    def test_init(self):
        """Test error initialization."""
        error = ConnectRPCError("not_found", "Resource not found")
        assert error.code == "not_found"
        assert error.message == "Resource not found"
        assert str(error) == "[not_found] Resource not found"

    def test_is_retryable_unavailable(self):
        """Test unavailable error is retryable."""
        error = ConnectRPCError("unavailable", "Service unavailable")
        assert error.is_retryable() is True

    def test_is_retryable_failed_precondition(self):
        """Test failed_precondition error is NOT retryable (영구 실패)."""
        error = ConnectRPCError("failed_precondition", "Precondition failed")
        assert error.is_retryable() is False

    def test_is_retryable_not_found(self):
        """Test not_found error is not retryable."""
        error = ConnectRPCError("not_found", "Not found")
        assert error.is_retryable() is False

    def test_is_retryable_invalid_argument(self):
        """Test invalid_argument error is not retryable."""
        error = ConnectRPCError("invalid_argument", "Invalid argument")
        assert error.is_retryable() is False

    def test_is_retryable_unknown(self):
        """Test unknown error is not retryable."""
        error = ConnectRPCError("unknown", "Unknown error")
        assert error.is_retryable() is False


class TestConnectRPCClient:
    """Test ConnectRPCClient class."""

    def test_init_with_custom_base_url(self):
        """Test client initialization with custom base URL."""
        client = ConnectRPCClient("test-token", base_url="https://custom.example.com")
        assert client.token == "test-token"
        assert client.base_url == "https://custom.example.com"
        assert client.headers["Authorization"] == "Bearer test-token"
        assert client.headers["Content-Type"] == "application/json"
        assert client.headers["Connect-Protocol-Version"] == "1"

    def test_init_with_default_base_url(self):
        """Test client initialization with default base URL from config."""
        with patch("aiauto.http_client.AIAUTO_API_TARGET", "api.example.com:443"):
            client = ConnectRPCClient("test-token")
            assert client.base_url == "https://api.example.com"

    @patch("aiauto.http_client.requests.post")
    def test_call_rpc_success(self, mock_post):
        """Test successful RPC call."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "success"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = ConnectRPCClient("test-token", base_url="https://api.example.com")
        result = client.call_rpc("TestMethod", {"param": "value"})

        assert result == {"result": "success"}
        mock_post.assert_called_once_with(
            "https://api.example.com/api/aiauto.v1.AIAutoService/TestMethod",
            json={"param": "value"},
            headers=client.headers,
        )

    @patch("aiauto.http_client.requests.post")
    def test_call_rpc_http_error_with_connect_rpc_error(self, mock_post):
        """Test RPC call with HTTP error containing Connect RPC error format."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"code": "not_found", "message": "Study not found"}
        mock_response.text = '{"code": "not_found", "message": "Study not found"}'

        http_error = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        client = ConnectRPCClient("test-token", base_url="https://api.example.com")

        with pytest.raises(ConnectRPCError) as exc_info:
            client.call_rpc("TestMethod", {})

        assert exc_info.value.code == "not_found"
        assert exc_info.value.message == "Study not found"

    @patch("aiauto.http_client.requests.post")
    def test_call_rpc_http_error_with_non_json_response(self, mock_post):
        """Test RPC call with HTTP error containing non-JSON response."""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("No JSON")
        mock_response.text = "Internal Server Error"
        mock_response.status_code = 500

        http_error = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        client = ConnectRPCClient("test-token", base_url="https://api.example.com")

        with pytest.raises(RuntimeError, match="HTTP 500 error"):
            client.call_rpc("TestMethod", {})

    @patch("aiauto.http_client.requests.post")
    def test_call_rpc_http_error_without_response(self, mock_post):
        """Test RPC call with HTTP error without response object."""
        http_error = requests.exceptions.HTTPError()
        http_error.response = None
        mock_post.return_value.raise_for_status.side_effect = http_error

        client = ConnectRPCClient("test-token", base_url="https://api.example.com")

        with pytest.raises(RuntimeError, match="HTTP error"):
            client.call_rpc("TestMethod", {})

    @patch("aiauto.http_client.requests.post")
    def test_call_rpc_request_exception(self, mock_post):
        """Test RPC call with request exception (network error)."""
        mock_post.side_effect = requests.exceptions.RequestException("Connection failed")

        client = ConnectRPCClient("test-token", base_url="https://api.example.com")

        with pytest.raises(RuntimeError, match="Request failed"):
            client.call_rpc("TestMethod", {})

    @patch("aiauto.http_client.requests.post")
    def test_call_rpc_http_error_with_json_unknown_code(self, mock_post):
        """Test RPC call with JSON error response with unknown code."""
        mock_response = MagicMock()
        # When no code/message, defaults to code="unknown", message=""
        mock_response.json.return_value = {"error": "some other format"}
        mock_response.text = '{"error": "some other format"}'

        http_error = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        client = ConnectRPCClient("test-token", base_url="https://api.example.com")

        # code defaults to "unknown" which is truthy, so ConnectRPCError is raised
        with pytest.raises(ConnectRPCError) as exc_info:
            client.call_rpc("TestMethod", {})

        assert exc_info.value.code == "unknown"

    @patch("aiauto.http_client.requests.post")
    def test_call_rpc_http_error_fallback_to_error_data(self, mock_post):
        """Test RPC call falls back to error_data when code and message are empty."""
        mock_response = MagicMock()
        # Both code and message are empty strings (falsy)
        mock_response.json.return_value = {"code": "", "message": "", "details": "extra info"}
        mock_response.text = '{"code": "", "message": "", "details": "extra info"}'

        http_error = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        client = ConnectRPCClient("test-token", base_url="https://api.example.com")

        with pytest.raises(RuntimeError, match="Server error"):
            client.call_rpc("TestMethod", {})


class TestWebhookErrorPropagation:
    """Test webhook error message propagation from server to client."""

    @patch("aiauto.http_client.requests.post")
    def test_webhook_denial_error_is_propagated(self, mock_post):
        """Test that webhook denial error message is properly received by client.

        When OptunaWorkspace creation is blocked by webhook (PVCs from previous
        workspace still exist), the error message should reach the client.
        """
        mock_response = MagicMock()
        # This is the format the front server sends for webhook denial
        mock_response.json.return_value = {
            "code": "failed_precondition",
            "message": 'admission webhook "voptunaworkspace-v1.kb.io" denied the request: PVCs from previous workspace still exist',
        }
        mock_response.text = '{"code": "failed_precondition", "message": "admission webhook \\"voptunaworkspace-v1.kb.io\\" denied the request: PVCs from previous workspace still exist"}'

        http_error = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        client = ConnectRPCClient("test-token", base_url="https://api.example.com")

        with pytest.raises(ConnectRPCError) as exc_info:
            client.call_rpc("EnsureWorkspace", {})

        assert exc_info.value.code == "failed_precondition"
        assert "PVCs from previous workspace still exist" in exc_info.value.message

    @patch("aiauto.http_client.requests.post")
    def test_webhook_denial_error_str_representation(self, mock_post):
        """Test that webhook denial error has readable string representation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "failed_precondition",
            "message": "PVCs from previous workspace still exist",
        }

        http_error = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        client = ConnectRPCClient("test-token", base_url="https://api.example.com")

        with pytest.raises(ConnectRPCError) as exc_info:
            client.call_rpc("EnsureWorkspace", {})

        error_str = str(exc_info.value)
        assert "[failed_precondition]" in error_str
        assert "PVCs from previous workspace still exist" in error_str

    def test_failed_precondition_is_not_retryable(self):
        """Test that failed_precondition errors are NOT retryable.

        Webhook denial (e.g., PVC still deleting) is a permanent failure
        that won't resolve with automatic retries.
        User should wait and manually retry.
        """
        error = ConnectRPCError(
            "failed_precondition",
            "PVCs from previous workspace still exist",
        )
        # failed_precondition is NOT retryable - permanent failure
        assert error.is_retryable() is False


class TestMapHttpError:
    """Test map_http_error function."""

    def test_passthrough(self):
        """Test that exceptions pass through unchanged."""
        original = ValueError("test error")
        result = map_http_error(original)
        assert result is original

    def test_connect_rpc_error_passthrough(self):
        """Test ConnectRPCError passes through unchanged."""
        original = ConnectRPCError("not_found", "Not found")
        result = map_http_error(original)
        assert result is original

    def test_runtime_error_passthrough(self):
        """Test RuntimeError passes through unchanged."""
        original = RuntimeError("Request failed")
        result = map_http_error(original)
        assert result is original
