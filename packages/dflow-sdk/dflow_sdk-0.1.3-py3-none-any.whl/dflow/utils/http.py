"""HTTP client for DFlow API requests."""

from typing import Any

import httpx


class DFlowApiError(Exception):
    """Custom error class for DFlow API errors.

    Thrown when the API returns a non-2xx status code.
    Contains the HTTP status code and response body for debugging.

    Example:
        >>> try:
        ...     market = dflow.markets.get_market("invalid-ticker")
        ... except DFlowApiError as e:
        ...     print(f"API Error {e.status_code}: {e}")
        ...     print(f"Response: {e.response}")
    """

    def __init__(self, message: str, status_code: int, response: Any = None):
        """Create a new API error.

        Args:
            message: Error message
            status_code: HTTP status code from the response
            response: Parsed response body (if available)
        """
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class HttpClient:
    """Internal HTTP client for making API requests.

    Handles request construction, authentication headers, and response parsing.
    Used internally by all API classes.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 30.0,
    ):
        """Create a new HTTP client.

        Args:
            base_url: Base URL for API requests
            api_key: Optional API key for authenticated requests
            headers: Optional additional headers to include in all requests
            timeout: Request timeout in seconds (default: 30.0)
        """
        # Ensure base_url ends with /
        self.base_url = base_url.rstrip("/") + "/"
        self.api_key = api_key
        self._default_headers = headers or {}
        self._client = httpx.Client(
            base_url=self.base_url,
            headers=self._build_headers(),
            timeout=timeout,
        )

    def _build_headers(self) -> dict[str, str]:
        """Build request headers including auth if available."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **self._default_headers,
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Make a GET request.

        Args:
            path: API endpoint path
            params: Optional query parameters

        Returns:
            Parsed JSON response

        Raises:
            DFlowApiError: If the request fails
        """
        # Clean path and filter None params
        clean_path = path.lstrip("/")
        clean_params = (
            {k: v for k, v in params.items() if v is not None} if params else None
        )

        response = self._client.get(clean_path, params=clean_params)
        return self._handle_response(response)

    def post(self, path: str, json: Any = None) -> Any:
        """Make a POST request.

        Args:
            path: API endpoint path
            json: Optional request body (will be JSON serialized)

        Returns:
            Parsed JSON response

        Raises:
            DFlowApiError: If the request fails
        """
        clean_path = path.lstrip("/")
        response = self._client.post(clean_path, json=json)
        return self._handle_response(response)

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle API response, raising errors for non-2xx status codes."""
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text

            raise DFlowApiError(
                f"HTTP {response.status_code}: {response.reason_phrase}",
                response.status_code,
                error_body,
            )

        try:
            return response.json()
        except Exception:
            raise DFlowApiError(
                "Failed to parse response as JSON",
                response.status_code,
                response.text,
            )

    def set_api_key(self, api_key: str) -> None:
        """Update the API key for subsequent requests.

        Args:
            api_key: New API key to use
        """
        self.api_key = api_key
        # Rebuild client with new headers
        self._client = httpx.Client(
            base_url=self.base_url,
            headers=self._build_headers(),
            timeout=self._client.timeout,
        )

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
