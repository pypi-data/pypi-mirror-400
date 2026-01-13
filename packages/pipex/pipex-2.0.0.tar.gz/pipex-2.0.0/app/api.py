"""
HTTP API client module for PipeX ETL tool.

This module provides a robust APIClient class with:
- HTTP request methods (GET, POST, PUT, DELETE)
- Automatic retry logic with exponential backoff
- Request/response caching with TTL
- Authentication support (Bearer token, API key, Basic auth)
- Comprehensive error handling and logging
- Timeout management
- Custom headers support
"""

import hashlib
import json
import logging
import time
from typing import Any, Dict, Optional, Union

import requests
from cachetools import TTLCache, cached
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class APIClient:
    """
    A robust HTTP API client with retry logic, caching, and authentication support.
    """

    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        cache_enabled: bool = True,
        cache_ttl: int = 300,
        cache_maxsize: int = 100,
        timeout: int = 30,
        retries: int = 3,
        backoff_factor: float = 0.3,
    ):
        """
        Initialize the API client.

        Args:
            base_url: Base URL for all API requests
            headers: Default headers to include in all requests
            cache_enabled: Whether to enable response caching
            cache_ttl: Cache time-to-live in seconds
            cache_maxsize: Maximum number of cached responses
            timeout: Default timeout for requests in seconds
            retries: Number of retry attempts for failed requests
            backoff_factor: Backoff factor for retry delays
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.cache_enabled = cache_enabled

        # Setup session with retry strategy
        self.session = requests.Session()
        self.session.headers.update(headers or {})

        retry_strategy = Retry(
            total=retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],  # Updated parameter name
            backoff_factor=backoff_factor,
            raise_on_redirect=False,
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Setup cache
        if cache_enabled:
            self.cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)

        logger.info(f"APIClient initialized for base URL: {base_url}")

    def _make_cache_key(self, method: str, url: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> str:
        """Generate a cache key for the request."""
        key_data = {"method": method, "url": url, "params": params, "data": data}
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get response from cache if available."""
        if not self.cache_enabled:
            return None
        return self.cache.get(cache_key)

    def _set_cache(self, cache_key: str, response_data: Any) -> None:
        """Store response in cache."""
        if self.cache_enabled:
            self.cache[cache_key] = response_data

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        use_cache: bool = True,
    ) -> requests.Response:
        """
        Make HTTP request with error handling and optional caching.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (will be appended to base_url)
            params: Query parameters
            data: Form data
            json_data: JSON data
            headers: Additional headers for this request
            timeout: Request timeout (uses default if not specified)
            use_cache: Whether to use cache for this request

        Returns:
            requests.Response: HTTP response object

        Raises:
            requests.exceptions.RequestException: For various HTTP errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        timeout = timeout or self.timeout

        # Check cache for GET requests
        if method.upper() == "GET" and use_cache and self.cache_enabled:
            cache_key = self._make_cache_key(method, url, params, data)
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                logger.info(f"Cache hit for {method} {url}")
                return cached_response

        # Prepare request headers
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)

        logger.info(f"Making {method} request to {url}")
        start_time = time.time()

        try:
            response = self.session.request(
                method=method, url=url, params=params, data=data, json=json_data, headers=request_headers, timeout=timeout
            )

            duration = time.time() - start_time
            logger.info(f"Request completed in {duration:.2f}s with status {response.status_code}")

            # Raise exception for HTTP errors
            response.raise_for_status()

            # Cache successful GET responses
            if method.upper() == "GET" and use_cache and self.cache_enabled:
                cache_key = self._make_cache_key(method, url, params, data)
                self._set_cache(cache_key, response)

            return response

        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout after {timeout}s: {url}")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error for {url}: {str(e)}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {response.status_code} for {url}: {str(e)}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {str(e)}")
            raise

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Make GET request and return JSON response.

        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout
            use_cache: Whether to use cache

        Returns:
            Dict[str, Any]: JSON response data
        """
        response = self._make_request("GET", endpoint, params=params, headers=headers, timeout=timeout, use_cache=use_cache)
        return response.json()

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Make POST request and return JSON response.

        Args:
            endpoint: API endpoint
            data: Form data
            json_data: JSON data
            headers: Additional headers
            timeout: Request timeout

        Returns:
            Dict[str, Any]: JSON response data
        """
        response = self._make_request(
            "POST", endpoint, data=data, json_data=json_data, headers=headers, timeout=timeout, use_cache=False
        )
        return response.json()

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Make PUT request and return JSON response.

        Args:
            endpoint: API endpoint
            data: Form data
            json_data: JSON data
            headers: Additional headers
            timeout: Request timeout

        Returns:
            Dict[str, Any]: JSON response data
        """
        response = self._make_request(
            "PUT", endpoint, data=data, json_data=json_data, headers=headers, timeout=timeout, use_cache=False
        )
        return response.json()

    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Make DELETE request and return JSON response.

        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout

        Returns:
            Dict[str, Any]: JSON response data
        """
        response = self._make_request("DELETE", endpoint, params=params, headers=headers, timeout=timeout, use_cache=False)
        return response.json()

    def get_with_bearer_auth(
        self,
        endpoint: str,
        token: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Make GET request with Bearer token authentication.

        Args:
            endpoint: API endpoint
            token: Bearer token
            params: Query parameters
            timeout: Request timeout
            use_cache: Whether to use cache

        Returns:
            Dict[str, Any]: JSON response data
        """
        headers = {"Authorization": f"Bearer {token}"}
        return self.get(endpoint, params=params, headers=headers, timeout=timeout, use_cache=use_cache)

    def get_with_api_key(
        self,
        endpoint: str,
        api_key: str,
        key_header: str = "X-API-Key",
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Make GET request with API key authentication.

        Args:
            endpoint: API endpoint
            api_key: API key
            key_header: Header name for API key
            params: Query parameters
            timeout: Request timeout
            use_cache: Whether to use cache

        Returns:
            Dict[str, Any]: JSON response data
        """
        headers = {key_header: api_key}
        return self.get(endpoint, params=params, headers=headers, timeout=timeout, use_cache=use_cache)

    def set_basic_auth(self, username: str, password: str) -> None:
        """
        Set basic authentication for all requests.

        Args:
            username: Username for basic auth
            password: Password for basic auth
        """
        self.session.auth = (username, password)
        logger.info("Basic authentication configured")

    def clear_cache(self) -> None:
        """Clear the response cache."""
        if self.cache_enabled:
            self.cache.clear()
            logger.info("Response cache cleared")

    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict[str, Any]: Cache statistics
        """
        if not self.cache_enabled:
            return {"cache_enabled": False}

        return {
            "cache_enabled": True,
            "cache_size": len(self.cache),
            "cache_maxsize": self.cache.maxsize,
            "cache_ttl": self.cache.ttl,
        }
