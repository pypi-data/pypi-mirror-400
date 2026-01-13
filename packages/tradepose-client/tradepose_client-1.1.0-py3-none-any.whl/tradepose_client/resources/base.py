"""Base resource class for TradePose Client.

This module provides the abstract base class for all API resources,
handling common HTTP operations and error handling.
"""

import logging
from typing import TYPE_CHECKING

import httpx
from pydantic import BaseModel

from ..exceptions import (
    AuthenticationError,
    AuthorizationError,
    NetworkError,
    RateLimitError,
    ResourceNotFoundError,
    ServerError,
    TradePoseAPIError,
    ValidationError,
)
from ..types import Headers, JSONData, QueryParams, ResponseData

if TYPE_CHECKING:
    from ..client import TradePoseClient


logger = logging.getLogger(__name__)


class BaseResource:
    """Base class for all API resources.

    This class provides common HTTP methods and error handling for all resources.
    All resource classes (APIKeysResource, BillingResource, etc.) should inherit from this.

    Attributes:
        client: Parent TradePoseClient instance
        _http_client: httpx.AsyncClient for making requests
    """

    def __init__(self, client: "TradePoseClient") -> None:
        """Initialize base resource.

        Args:
            client: Parent TradePoseClient instance
        """
        self.client = client
        self._http_client = client._http_client

    def _build_url(self, path: str) -> str:
        """Build full URL from path.

        Args:
            path: API path (e.g., '/api/v1/tasks/123')

        Returns:
            Full URL (e.g., 'https://api.tradepose.com/api/v1/tasks/123')
        """
        path = path.lstrip("/")
        return f"{self.client.config.server_url}/{path}"

    def _get_headers(self, additional_headers: Headers | None = None) -> Headers:
        """Get request headers with authentication.

        Args:
            additional_headers: Additional headers to include

        Returns:
            Complete headers dictionary
        """
        headers: Headers = {
            "User-Agent": f"tradepose-client-python/{self.client.version}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if additional_headers:
            headers.update(additional_headers)

        return headers

    async def _handle_response(
        self,
        response: httpx.Response,
        expect_json: bool = True,
    ) -> ResponseData:
        """Handle HTTP response and raise appropriate exceptions.

        Args:
            response: HTTP response from httpx
            expect_json: Whether to parse response as JSON

        Returns:
            Response data (dict, list, or bytes)

        Raises:
            TradePoseAPIError: For various API error conditions
        """
        # Extract request ID if available
        request_id = response.headers.get("X-Request-ID")

        # Handle success responses
        if 200 <= response.status_code < 300:
            if response.status_code == 204:
                return {}

            if expect_json:
                try:
                    return response.json()
                except Exception as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    raise TradePoseAPIError(
                        f"Invalid JSON response: {e}",
                        status_code=response.status_code,
                        request_id=request_id,
                    )
            else:
                return response.content

        # Handle error responses
        error_data = None
        try:
            error_data = response.json()
        except Exception:
            error_data = {"error": response.text}

        error_message = error_data.get("error", "Unknown error")

        # Authentication error (401)
        if response.status_code == 401:
            raise AuthenticationError(
                message=error_message,
                response=error_data,
                request_id=request_id,
            )

        # Authorization error (403)
        if response.status_code == 403:
            raise AuthorizationError(
                message=error_message,
                response=error_data,
                request_id=request_id,
            )

        # Not found error (404)
        if response.status_code == 404:
            # Extract resource info from URL if possible
            url_parts = response.url.path.split("/")
            resource_type = url_parts[-2] if len(url_parts) >= 2 else "resource"
            resource_id = url_parts[-1] if url_parts else "unknown"

            raise ResourceNotFoundError(
                resource_type=resource_type,
                resource_id=resource_id,
                response=error_data,
                request_id=request_id,
            )

        # Validation error (422)
        if response.status_code == 422:
            errors = error_data.get("details", [])
            raise ValidationError(
                message=error_message,
                errors=errors,
                response=error_data,
                request_id=request_id,
            )

        # Rate limit error (429)
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_after_seconds = float(retry_after) if retry_after else None

            raise RateLimitError(
                message=error_message,
                retry_after=retry_after_seconds,
                response=error_data,
                request_id=request_id,
            )

        # Server error (5xx)
        if response.status_code >= 500:
            raise ServerError(
                message=error_message,
                status_code=response.status_code,
                response=error_data,
                request_id=request_id,
            )

        # Generic API error
        raise TradePoseAPIError(
            message=error_message,
            status_code=response.status_code,
            response=error_data,
            request_id=request_id,
        )

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: QueryParams | None = None,
        json: JSONData | BaseModel | None = None,
        headers: Headers | None = None,
        expect_json: bool = True,
        timeout: float | None = None,
    ) -> ResponseData:
        """Make HTTP request to API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            path: API path
            params: Query parameters
            json: JSON request body (dict or Pydantic model)
            headers: Additional headers
            expect_json: Whether to parse response as JSON
            timeout: Request timeout (uses config default if not specified)

        Returns:
            Response data

        Raises:
            NetworkError: For network-related errors
            TradePoseAPIError: For API errors
        """
        url = self._build_url(path)
        request_headers = self._get_headers(headers)
        request_timeout = timeout or self.client.config.timeout

        # Convert Pydantic model to dict if needed
        json_data = None
        if json is not None:
            if isinstance(json, BaseModel):
                json_data = json.model_dump(mode="json", exclude_none=True)
            else:
                json_data = json

        try:
            logger.debug(f"{method} {url} (params={params}, timeout={request_timeout}s)")

            response = await self._http_client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=request_headers,
                timeout=request_timeout,
            )

            return await self._handle_response(response, expect_json=expect_json)

        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {e}")
            raise NetworkError(f"Request timed out after {request_timeout}s: {e}")
        except httpx.NetworkError as e:
            logger.error(f"Network error: {e}")
            raise NetworkError(f"Network error: {e}")
        except (
            AuthenticationError,
            AuthorizationError,
            ResourceNotFoundError,
            ValidationError,
            RateLimitError,
            ServerError,
            TradePoseAPIError,
        ):
            # Re-raise TradePose API errors as-is
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during request: {e}")
            raise TradePoseAPIError(f"Unexpected error: {e}")

    async def _get(
        self,
        path: str,
        *,
        params: QueryParams | None = None,
        headers: Headers | None = None,
        expect_json: bool = True,
        timeout: float | None = None,
    ) -> ResponseData:
        """Make GET request.

        Args:
            path: API path
            params: Query parameters
            headers: Additional headers
            expect_json: Whether to parse response as JSON
            timeout: Request timeout

        Returns:
            Response data
        """
        return await self._request(
            "GET",
            path,
            params=params,
            headers=headers,
            expect_json=expect_json,
            timeout=timeout,
        )

    async def _post(
        self,
        path: str,
        *,
        json: JSONData | BaseModel | None = None,
        params: QueryParams | None = None,
        headers: Headers | None = None,
        timeout: float | None = None,
    ) -> ResponseData:
        """Make POST request.

        Args:
            path: API path
            json: JSON request body
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout

        Returns:
            Response data
        """
        return await self._request(
            "POST",
            path,
            json=json,
            params=params,
            headers=headers,
            timeout=timeout,
        )

    async def _put(
        self,
        path: str,
        *,
        json: JSONData | BaseModel | None = None,
        params: QueryParams | None = None,
        headers: Headers | None = None,
        timeout: float | None = None,
    ) -> ResponseData:
        """Make PUT request.

        Args:
            path: API path
            json: JSON request body
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout

        Returns:
            Response data
        """
        return await self._request(
            "PUT",
            path,
            json=json,
            params=params,
            headers=headers,
            timeout=timeout,
        )

    async def _delete(
        self,
        path: str,
        *,
        params: QueryParams | None = None,
        headers: Headers | None = None,
        timeout: float | None = None,
    ) -> ResponseData:
        """Make DELETE request.

        Args:
            path: API path
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout

        Returns:
            Response data
        """
        return await self._request(
            "DELETE",
            path,
            params=params,
            headers=headers,
            timeout=timeout,
        )
