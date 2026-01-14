"""Base HTTP client for Mielto API."""

import json
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import httpx

from mielto.client.exceptions import (
    AuthenticationError,
    ConnectionError,
    CreditLimitExceededError,
    MieltoError,
    NotFoundError,
    OverageLimitExceededError,
    PaymentRequiredError,
    PermissionError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
)


class BaseClient:
    """Base HTTP client for making API requests."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.mielto.com/api/v1",
        timeout: float = 30.0,
        max_retries: int = 2,
    ):
        """Initialize the base client.

        Args:
            api_key: Mielto API key for authentication
            base_url: Base URL for the Mielto API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        self._client = httpx.Client(
            timeout=timeout,
            headers=self._get_headers(),
            transport=httpx.HTTPTransport(retries=max_retries),
        )

    def _get_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        return urljoin(self.base_url + "/", endpoint.lstrip("/"))

    def _handle_response_error(self, response: httpx.Response) -> None:
        """Handle HTTP error responses."""
        try:
            # For streaming responses, we need to read the content first
            if hasattr(response, "is_stream_consumed") and not response.is_stream_consumed:
                try:
                    response.read()
                except Exception:
                    # If reading fails, use status code as message
                    message = f"HTTP {response.status_code}"
                    raise MieltoError(message, response.status_code, None)

            error_data = response.json()
            message = error_data.get("detail", response.text)
            error_code = error_data.get("error_code") if isinstance(error_data, dict) else None
        except (json.JSONDecodeError, AttributeError):
            message = response.text or f"HTTP {response.status_code}"
            error_code = None

        error_dict = error_data if "error_data" in locals() else None

        # Check for specific error codes first
        if error_code == "CREDIT_LIMIT_EXCEEDED":
            raise CreditLimitExceededError(message, response.status_code, error_dict)
        elif error_code == "OVERAGE_LIMIT_EXCEEDED":
            raise OverageLimitExceededError(message, response.status_code, error_dict)

        # Handle HTTP status codes
        if response.status_code == 401:
            raise AuthenticationError(message, response.status_code, error_dict)
        elif response.status_code == 402:
            raise PaymentRequiredError(message, response.status_code, error_dict)
        elif response.status_code == 403:
            raise PermissionError(message, response.status_code, error_dict)
        elif response.status_code == 404:
            raise NotFoundError(message, response.status_code, error_dict)
        elif response.status_code == 422:
            raise ValidationError(message, response.status_code, error_dict)
        elif response.status_code == 429:
            raise RateLimitError(message, response.status_code, error_dict)
        elif response.status_code >= 500:
            raise ServerError(message, response.status_code, error_dict)
        else:
            raise MieltoError(message, response.status_code, error_dict)

    def request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            json_data: JSON data to send in request body
            params: Query parameters
            files: Files to upload (multipart/form-data)
            data: Form data to send
            headers: Additional headers to include in the request

        Returns:
            Response data (parsed JSON)

        Raises:
            MieltoError: On API errors
            TimeoutError: On request timeout
            ConnectionError: On connection errors
        """
        url = self._build_url(endpoint)

        try:
            # Merge custom headers with default headers
            request_headers = self._get_headers()
            if headers:
                request_headers.update(headers)

            # Handle multipart form data
            if files or data:
                # For multipart, only include Authorization header
                request_headers = {"Authorization": f"Bearer {self.api_key}"}
                if headers:
                    request_headers.update(headers)
                response = self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    files=files,
                    headers=request_headers,
                )
            else:
                response = self._client.request(
                    method=method,
                    url=url,
                    json=json_data,
                    params=params,
                    headers=request_headers,
                )

            if not response.is_success:
                self._handle_response_error(response)

            # Handle empty responses (e.g., 204 No Content)
            if response.status_code == 204 or not response.content:
                return None

            return response.json()

        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {str(e)}")
        except httpx.ConnectError as e:
            raise ConnectionError(f"Connection error: {str(e)}")
        except (AuthenticationError, PermissionError, NotFoundError, ValidationError, RateLimitError, ServerError):
            raise
        except Exception as e:
            raise MieltoError(f"Unexpected error: {str(e)}")

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """Make a GET request."""
        return self.request("GET", endpoint, params=params, headers=headers)

    def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a POST request."""
        return self.request("POST", endpoint, json_data=json_data, files=files, data=data)

    def put(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Any:
        """Make a PUT request."""
        return self.request("PUT", endpoint, json_data=json_data)

    def delete(self, endpoint: str) -> Any:
        """Make a DELETE request."""
        return self.request("DELETE", endpoint)

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class AsyncBaseClient:
    """Async base HTTP client for making API requests."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.mielto.com/api/v1",
        timeout: float = 30.0,
        max_retries: int = 2,
    ):
        """Initialize the async base client.

        Args:
            api_key: Mielto API key for authentication
            base_url: Base URL for the Mielto API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers=self._get_headers(),
            transport=httpx.AsyncHTTPTransport(retries=max_retries),
        )

    def _get_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        return urljoin(self.base_url + "/", endpoint.lstrip("/"))

    def _handle_response_error(self, response: httpx.Response) -> None:
        """Handle HTTP error responses."""
        try:
            # For streaming responses, we need to read the content first
            if hasattr(response, "is_stream_consumed") and not response.is_stream_consumed:
                try:
                    response.read()
                except Exception:
                    # If reading fails, use status code as message
                    message = f"HTTP {response.status_code}"
                    raise MieltoError(message, response.status_code, None)

            error_data = response.json()
            message = error_data.get("detail", response.text)
            error_code = error_data.get("error_code") if isinstance(error_data, dict) else None
        except (json.JSONDecodeError, AttributeError):
            message = response.text or f"HTTP {response.status_code}"
            error_code = None

        error_dict = error_data if "error_data" in locals() else None

        # Check for specific error codes first
        if error_code == "CREDIT_LIMIT_EXCEEDED":
            raise CreditLimitExceededError(message, response.status_code, error_dict)
        elif error_code == "OVERAGE_LIMIT_EXCEEDED":
            raise OverageLimitExceededError(message, response.status_code, error_dict)

        # Handle HTTP status codes
        if response.status_code == 401:
            raise AuthenticationError(message, response.status_code, error_dict)
        elif response.status_code == 402:
            raise PaymentRequiredError(message, response.status_code, error_dict)
        elif response.status_code == 403:
            raise PermissionError(message, response.status_code, error_dict)
        elif response.status_code == 404:
            raise NotFoundError(message, response.status_code, error_dict)
        elif response.status_code == 422:
            raise ValidationError(message, response.status_code, error_dict)
        elif response.status_code == 429:
            raise RateLimitError(message, response.status_code, error_dict)
        elif response.status_code >= 500:
            raise ServerError(message, response.status_code, error_dict)
        else:
            raise MieltoError(message, response.status_code, error_dict)

    async def request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Make an async HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            json_data: JSON data to send in request body
            params: Query parameters
            files: Files to upload (multipart/form-data)
            data: Form data to send
            headers: Additional headers to include in the request

        Returns:
            Response data (parsed JSON)

        Raises:
            MieltoError: On API errors
            TimeoutError: On request timeout
            ConnectionError: On connection errors
        """
        url = self._build_url(endpoint)

        try:
            # Merge custom headers with default headers
            request_headers = self._get_headers()
            if headers:
                request_headers.update(headers)

            # Handle multipart form data
            if files or data:
                # For multipart, only include Authorization header
                request_headers = {"Authorization": f"Bearer {self.api_key}"}
                if headers:
                    request_headers.update(headers)
                response = await self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    files=files,
                    headers=request_headers,
                )
            else:
                response = await self._client.request(
                    method=method,
                    url=url,
                    json=json_data,
                    params=params,
                    headers=request_headers,
                )

            if not response.is_success:
                self._handle_response_error(response)

            # Handle empty responses (e.g., 204 No Content)
            if response.status_code == 204 or not response.content:
                return None

            return response.json()

        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {str(e)}")
        except httpx.ConnectError as e:
            raise ConnectionError(f"Connection error: {str(e)}")
        except (AuthenticationError, PermissionError, NotFoundError, ValidationError, RateLimitError, ServerError):
            raise
        except Exception as e:
            raise MieltoError(f"Unexpected error: {str(e)}")

    async def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """Make an async GET request."""
        return await self.request("GET", endpoint, params=params, headers=headers)

    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make an async POST request."""
        return await self.request("POST", endpoint, json_data=json_data, files=files, data=data)

    async def put(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Any:
        """Make an async PUT request."""
        return await self.request("PUT", endpoint, json_data=json_data)

    async def delete(self, endpoint: str) -> Any:
        """Make an async DELETE request."""
        return await self.request("DELETE", endpoint)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
