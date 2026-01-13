"""
Test module for API Key Authentication

Test Categories:
1. Header injection - X-API-Key header added correctly
2. Auth flow - httpx.Auth generator pattern
3. Helper methods - get_headers()
"""


# TODO: Import from tradepose_client.auth.api_key
# from tradepose_client.auth.api_key import APIKeyAuth


class TestAPIKeyAuth:
    """Test suite for APIKeyAuth."""

    def test_init_with_api_key(self):
        """Test APIKeyAuth initialization."""
        # TODO: Act - auth = APIKeyAuth("sk_test_123")
        # TODO: Assert - auth.api_key == "sk_test_123"
        pass

    def test_get_headers_returns_x_api_key(self):
        """Test get_headers() returns X-API-Key header."""
        # TODO: Arrange - auth = APIKeyAuth("sk_test_123")
        # TODO: Act - headers = auth.get_headers()
        # TODO: Assert - headers["X-API-Key"] == "sk_test_123"
        pass

    def test_auth_flow_adds_header(self):
        """Test httpx.Auth flow adds header to request."""
        # TODO: Arrange - auth = APIKeyAuth("sk_test_123")
        # TODO: Arrange - Mock request object
        # TODO: Act - Call auth_flow and get modified request
        # TODO: Assert - Request has X-API-Key header
        pass

    def test_auth_flow_generator_pattern(self):
        """Test auth_flow follows generator pattern."""
        # TODO: Arrange - auth = APIKeyAuth("sk_test_123")
        # TODO: Act - flow = auth.auth_flow(mock_request)
        # TODO: Assert - next(flow) yields request with header
        pass
