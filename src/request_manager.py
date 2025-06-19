from typing import Optional, Dict, Any
import requests
from .proxy_manager import ProxyManager, get_fast_proxies
from .user_agent_rotator import UserAgentRotator
from .headers_manager import HeadersManager
import random
import logging

logger = logging.getLogger(__name__)

class RequestManager:
    def __init__(self, num_proxies: int = 5, timeout: int = 10):
        """
        Initialize RequestManager with components for rotating proxies, user agents, and headers.
        
        Args:
            num_proxies: Number of fast proxies to maintain in the pool
            timeout: Timeout for requests in seconds
        """
        self.timeout = timeout
        self.proxies_pool = get_fast_proxies(limit=num_proxies)
        self.user_agent_rotator = UserAgentRotator()
        self.headers_manager = HeadersManager()
        self._current_proxy: Optional[Dict[str, Any]] = None

    def _get_random_proxy(self) -> Dict[str, str]:
        """Get a random proxy from the pool."""
        if not self.proxies_pool:
            # If proxy pool is empty, refresh it
            self.proxies_pool = get_fast_proxies(limit=5)
            if not self.proxies_pool:
                raise Exception("No working proxies available")

        proxy_info = random.choice(self.proxies_pool)
        proxy_url = f"http://{proxy_info['proxy']}"
        self._current_proxy = proxy_info
        
        return {
            'http': proxy_url,
            'https': proxy_url
        }

    def make_request(
        self,
        method: str,
        url: str,
        base_headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make an HTTP request with rotating proxies, user agents, and headers.
        
        Args:
            method: HTTP method ('GET', 'POST', etc.)
            url: Target URL
            base_headers: Base headers to include (optional)
            **kwargs: Additional arguments to pass to requests
        
        Returns:
            requests.Response object
        
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        # Get random components
        proxy = self._get_random_proxy()
        user_agent = self.user_agent_rotator.get_random()
        
        # Prepare headers
        if base_headers is None:
            base_headers = {}
        base_headers['User-Agent'] = user_agent
        
        headers = self.headers_manager.get_random_headers(base_headers)
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                proxies=proxy,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            logger.debug(f"Request successful using proxy: {self._current_proxy['proxy']}")
            return response
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed with proxy {self._current_proxy['proxy']}: {str(e)}")
            
            # Remove failed proxy from pool
            if self._current_proxy in self.proxies_pool:
                self.proxies_pool.remove(self._current_proxy)
            
            # Retry with remaining proxies if available
            if len(self.proxies_pool) > 0:
                logger.info("Retrying with different proxy...")
                return self.make_request(method, url, base_headers, **kwargs)
            else:
                # If no proxies left, refresh the pool and try one last time
                self.proxies_pool = get_fast_proxies(limit=5)
                if self.proxies_pool:
                    return self.make_request(method, url, base_headers, **kwargs)
                raise

    def get(self, url: str, **kwargs) -> requests.Response:
        """Make a GET request."""
        return self.make_request('GET', url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        """Make a POST request."""
        return self.make_request('POST', url, **kwargs)

    def get_current_proxy(self) -> Optional[Dict[str, Any]]:
        """Get the currently used proxy."""
        return self._current_proxy

    def refresh_proxy_pool(self, num_proxies: int = 5) -> None:
        """Refresh the proxy pool with new fast proxies."""
        self.proxies_pool = get_fast_proxies(limit=num_proxies)
