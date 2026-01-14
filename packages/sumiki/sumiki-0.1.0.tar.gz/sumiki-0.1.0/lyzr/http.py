"""
HTTP client for Lyzr Agent API
"""

import os
from typing import Dict, Any, Optional
import httpx
from lyzr.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    APIError,
    TimeoutError,
    ValidationError,
)


class HTTPClient:
    """HTTP client with authentication and error handling"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://agent-prod.studio.lyzr.ai",
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize HTTP client

        Args:
            api_key: Lyzr API key (reads from LYZR_API_KEY env var if not provided)
            base_url: Base URL for API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.api_key = api_key or os.getenv("LYZR_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Provide it via api_key parameter or LYZR_API_KEY environment variable."
            )

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        # Create httpx client
        self._client = httpx.Client(
            timeout=httpx.Timeout(timeout),
            headers=self._get_headers(),
        )

    def _get_headers(self) -> Dict[str, str]:
        """Get default headers"""
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _build_url(self, path: str) -> str:
        """Build full URL from path"""
        path = path.lstrip("/")
        return f"{self.base_url}/{path}"

    def _handle_error(self, response: httpx.Response):
        """Handle HTTP errors"""
        status_code = response.status_code

        try:
            error_data = response.json()
            message = error_data.get("detail", response.text)
        except Exception:
            message = response.text

        if status_code == 401:
            raise AuthenticationError(
                f"Authentication failed: {message}",
                status_code=status_code,
                response=error_data if 'error_data' in locals() else None
            )
        elif status_code == 404:
            raise NotFoundError(
                f"Resource not found: {message}",
                status_code=status_code,
                response=error_data if 'error_data' in locals() else None
            )
        elif status_code == 422:
            raise ValidationError(
                f"Validation error: {message}",
                status_code=status_code,
                response=error_data if 'error_data' in locals() else None
            )
        elif status_code == 429:
            raise RateLimitError(
                f"Rate limit exceeded: {message}",
                status_code=status_code,
                response=error_data if 'error_data' in locals() else None
            )
        else:
            raise APIError(
                f"API error ({status_code}): {message}",
                status_code=status_code,
                response=error_data if 'error_data' in locals() else None
            )

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make GET request

        Args:
            path: API endpoint path
            params: Query parameters

        Returns:
            Response JSON as dictionary
        """
        try:
            url = self._build_url(path)
            response = self._client.get(url, params=params)

            if response.status_code >= 400:
                self._handle_error(response)

            return response.json()

        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {str(e)}")
        except httpx.HTTPError as e:
            raise APIError(f"HTTP error occurred: {str(e)}")

    def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make POST request

        Args:
            path: API endpoint path
            json: JSON body
            params: Query parameters

        Returns:
            Response JSON as dictionary
        """
        try:
            url = self._build_url(path)
            response = self._client.post(url, json=json, params=params)

            if response.status_code >= 400:
                self._handle_error(response)

            return response.json()

        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {str(e)}")
        except httpx.HTTPError as e:
            raise APIError(f"HTTP error occurred: {str(e)}")

    def put(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make PUT request

        Args:
            path: API endpoint path
            json: JSON body
            params: Query parameters

        Returns:
            Response JSON as dictionary
        """
        try:
            url = self._build_url(path)
            response = self._client.put(url, json=json, params=params)

            if response.status_code >= 400:
                self._handle_error(response)

            return response.json()

        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {str(e)}")
        except httpx.HTTPError as e:
            raise APIError(f"HTTP error occurred: {str(e)}")

    def delete(self, path: str, params: Optional[Dict[str, Any]] = None, json_body: Optional[Dict[str, Any]] = None) -> bool:
        """
        Make DELETE request

        Args:
            path: API endpoint path
            params: Query parameters
            json_body: JSON body (for deletes that require body)

        Returns:
            True if successful
        """
        try:
            url = self._build_url(path)

            # httpx requires json bodies to be passed via content parameter for DELETE
            if json_body:
                import json as json_lib
                response = self._client.delete(
                    url,
                    params=params,
                    content=json_lib.dumps(json_body),
                    headers={**self._get_headers(), "Content-Type": "application/json"}
                )
            else:
                response = self._client.delete(url, params=params)

            if response.status_code >= 400:
                self._handle_error(response)

            return True

        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {str(e)}")
        except httpx.HTTPError as e:
            raise APIError(f"HTTP error occurred: {str(e)}")

    def post_file(
        self,
        path: str,
        file_path: str,
        file_field: str = "file",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload file with multipart/form-data

        Args:
            path: API endpoint path
            file_path: Path to file to upload
            file_field: Form field name for file (default: "file")
            data: Additional form data
            params: Query parameters

        Returns:
            Response JSON as dictionary

        Raises:
            FileNotFoundError: If file doesn't exist
            APIError: If upload fails

        Example:
            >>> response = http.post_file(
            ...     path="/v3/train/pdf/",
            ...     file_path="manual.pdf",
            ...     params={"rag_id": "kb_123"}
            ... )
        """
        try:
            import os
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            url = self._build_url(path)

            with open(file_path, 'rb') as f:
                files = {file_field: (os.path.basename(file_path), f)}

                # Remove Content-Type from headers for multipart
                headers = self._get_headers()
                headers.pop("Content-Type", None)

                response = self._client.post(
                    url,
                    files=files,
                    data=data,
                    params=params,
                    headers=headers
                )

                if response.status_code >= 400:
                    self._handle_error(response)

                return response.json()

        except FileNotFoundError:
            raise
        except httpx.TimeoutException as e:
            raise TimeoutError(f"File upload timed out: {str(e)}")
        except httpx.HTTPError as e:
            raise APIError(f"HTTP error during file upload: {str(e)}")

    def close(self):
        """Close the HTTP client"""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
