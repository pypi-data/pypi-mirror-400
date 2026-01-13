"""
HTTP client with automatic retries and error handling
"""

import time
import logging
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    ServerError,
    NetworkError,
    PictographError
)

logger = logging.getLogger(__name__)


class HTTPClient:
    """
    HTTP client with automatic retries for transient failures.

    Handles authentication, rate limiting, and error responses.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://pictograph.dev",
        timeout: int = 30,
        max_retries: int = 3
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        # Create session with connection pooling
        self.session = requests.Session()

        # Configure retries for specific HTTP status codes
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,  # 1, 2, 4, 8 seconds
            status_forcelist=[500, 502, 503, 504],  # Retry on server errors
            allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
            raise_on_status=False
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        self.session.headers.update({
            "X-API-Key": api_key,
            "User-Agent": "pictograph-python-sdk/0.1.0",
            "Accept": "application/json"
        })

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle HTTP response and raise appropriate exceptions.
        """
        try:
            response_data = response.json()
        except ValueError:
            response_data = {"detail": response.text}

        # Success
        if 200 <= response.status_code < 300:
            return response_data

        # Client errors
        if response.status_code == 401:
            raise AuthenticationError(
                response_data.get("detail", "Authentication failed"),
                status_code=401,
                response=response_data
            )

        if response.status_code == 404:
            raise NotFoundError(
                response_data.get("detail", "Resource not found"),
                status_code=404,
                response=response_data
            )

        if response.status_code == 400:
            raise ValidationError(
                response_data.get("detail", "Validation error"),
                status_code=400,
                response=response_data
            )

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(
                response_data.get("detail", "Rate limit exceeded"),
                retry_after=retry_after,
                status_code=429,
                response=response_data
            )

        # Server errors
        if 500 <= response.status_code < 600:
            raise ServerError(
                response_data.get("detail", "Server error"),
                status_code=response.status_code,
                response=response_data
            )

        # Other errors
        raise PictographError(
            response_data.get("detail", f"HTTP {response.status_code}"),
            status_code=response.status_code,
            response=response_data
        )

    def _handle_rate_limit_retry(self, func, *args, **kwargs):
        """
        Wrapper to handle rate limit with automatic retry after waiting.
        """
        try:
            return func(*args, **kwargs)
        except RateLimitError as e:
            if e.retry_after and e.retry_after < 120:  # Only auto-retry if wait < 2 minutes
                logger.warning(f"Rate limit exceeded. Waiting {e.retry_after} seconds...")
                time.sleep(e.retry_after)
                return func(*args, **kwargs)  # Retry once
            raise

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a GET request.
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self._handle_rate_limit_retry(
                self.session.get,
                url,
                params=params,
                timeout=self.timeout
            )
            return self._handle_response(response)

        except requests.exceptions.Timeout:
            raise NetworkError(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {str(e)}")
        except (RateLimitError, AuthenticationError, NotFoundError, ValidationError, ServerError):
            raise
        except Exception as e:
            raise PictographError(f"Unexpected error: {str(e)}")

    def post(
        self,
        endpoint: str,
        json: Optional[Dict] = None,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make a POST request.
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self._handle_rate_limit_retry(
                self.session.post,
                url,
                json=json,
                data=data,
                files=files,
                timeout=self.timeout
            )
            return self._handle_response(response)

        except requests.exceptions.Timeout:
            raise NetworkError(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {str(e)}")
        except (RateLimitError, AuthenticationError, NotFoundError, ValidationError, ServerError):
            raise
        except Exception as e:
            raise PictographError(f"Unexpected error: {str(e)}")

    def patch(self, endpoint: str, json: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a PATCH request.
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self._handle_rate_limit_retry(
                self.session.patch,
                url,
                json=json,
                timeout=self.timeout
            )
            return self._handle_response(response)

        except requests.exceptions.Timeout:
            raise NetworkError(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {str(e)}")
        except (RateLimitError, AuthenticationError, NotFoundError, ValidationError, ServerError):
            raise
        except Exception as e:
            raise PictographError(f"Unexpected error: {str(e)}")

    def delete(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a DELETE request.
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self._handle_rate_limit_retry(
                self.session.delete,
                url,
                params=params,
                timeout=self.timeout
            )
            return self._handle_response(response)

        except requests.exceptions.Timeout:
            raise NetworkError(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {str(e)}")
        except (RateLimitError, AuthenticationError, NotFoundError, ValidationError, ServerError):
            raise
        except Exception as e:
            raise PictographError(f"Unexpected error: {str(e)}")

    def close(self):
        """Close the session"""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
