from typing import Optional, Dict, Any, Set
import requests
import warnings
import random
import logging
from .proxy_manager import ProxyManager, get_fast_proxies
from .user_agent_rotator import UserAgentRotator
from .headers_manager import HeadersManager
from urllib3.exceptions import InsecureRequestWarning
from collections import defaultdict

# Disable all warnings
warnings.filterwarnings('ignore')
# Specifically disable SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)

class RequestManager:
    def __init__(self, num_proxies: int = 3, timeout: int = 5, max_requests_per_proxy: int = 25):
        """Initialize RequestManager with proxy tracking."""
        self.timeout = timeout
        self.user_agent_rotator = UserAgentRotator()
        self.headers_manager = HeadersManager()
        self._current_proxy: Optional[Dict[str, Any]] = None
        
        # Proxy management
        self.max_requests_per_proxy = max_requests_per_proxy
        self.proxies_pool = []
        self.working_proxies = defaultdict(list)  # url -> list of working proxies
        self.failed_proxies: Set[str] = set()
        self.proxy_success_counts = defaultdict(int)
        self.proxy_failure_counts = defaultdict(int)
        self.proxy_request_counts = defaultdict(int)  # Track total requests per proxy
        
        # Build initial proxy pool asynchronously
        logger.info("Building initial proxy pool asynchronously...")
        self._initialize_proxy_pool(num_proxies)

    def _initialize_proxy_pool(self, num_proxies: int) -> None:
        """Initialize proxy pool asynchronously."""
        import threading
        self.initialization_thread = threading.Thread(
            target=self._build_proxy_pool,
            args=(num_proxies,),
            daemon=True
        )
        self.initialization_thread.start()

    def _build_proxy_pool(self, num_proxies: int) -> None:
        """Build a pool of fast proxies."""
        try:
            new_proxies = get_fast_proxies(limit=num_proxies * 2)
            if new_proxies:
                # Sort by speed
                new_proxies.sort(key=lambda x: x['speed'])
                # Take fastest proxies
                self.proxies_pool = [p for p in new_proxies if p['proxy'] not in self.failed_proxies][:num_proxies]
                logger.info(f"Found {len(self.proxies_pool)} working proxies")
            else:
                logger.warning("No working proxies found in initial pool")
        except Exception as e:
            logger.error(f"Error building proxy pool: {str(e)}")

    def _update_proxy_stats(self, proxy: str, success: bool, url: str) -> None:
        """Update proxy success/failure statistics."""
        if success:
            self.proxy_success_counts[proxy] += 1
            if proxy not in self.working_proxies[url]:
                self.working_proxies[url].append(proxy)
        else:
            self.proxy_failure_counts[proxy] += 1
            if proxy in self.working_proxies[url]:
                self.working_proxies[url].remove(proxy)
            
        # Check failure rate
        total = self.proxy_success_counts[proxy] + self.proxy_failure_counts[proxy]
        if total >= 5:  # Need minimum attempts to judge
            failure_rate = self.proxy_failure_counts[proxy] / total
            if failure_rate > 0.5:  # More than 50% failures
                self.failed_proxies.add(proxy)
                logger.info(f"Proxy {proxy} blacklisted due to high failure rate")

    def _ensure_proxy_pool(self) -> None:
        """Ensure proxy pool is initialized."""
        if hasattr(self, 'initialization_thread') and self.initialization_thread.is_alive():
            logger.info("Waiting for proxy pool initialization...")
            self.initialization_thread.join(timeout=10)  # Wait up to 10 seconds
            
        if not self.proxies_pool:
            logger.warning("No proxies in pool, initializing backup proxy...")
            # Use a default proxy as backup
            self.proxies_pool = [{
                'proxy': '207.180.209.185:5000',  # Example backup proxy
                'speed': 1.0,
                'status': 'working'
            }]

    def _get_best_proxy(self, url: str) -> Dict[str, str]:
        """Get the best proxy for a specific URL."""
        # Ensure proxy pool is initialized
        self._ensure_proxy_pool()
        # Try previously successful proxies first
        if url in self.working_proxies and self.working_proxies[url]:
            proxy_info = next(
                (p for p in self.proxies_pool if p['proxy'] == self.working_proxies[url][0]), 
                None
            )
            if proxy_info:
                return self._format_proxy(proxy_info)

        # If no working proxies or max requests reached, get new one
        available_proxies = [
            p for p in self.proxies_pool 
            if p['proxy'] not in self.failed_proxies
        ]
        
        if not available_proxies:
            logger.info("No available proxies, refreshing pool...")
            self._build_proxy_pool(max(3, len(self.proxies_pool)))
            available_proxies = self.proxies_pool

        proxy_info = min(available_proxies, key=lambda x: x['speed'])
        return self._format_proxy(proxy_info)

    def _format_proxy(self, proxy_info: Dict[str, Any]) -> Dict[str, str]:
        """Format proxy info for requests."""
        self._current_proxy = proxy_info
        self.proxy_request_counts[proxy_info['proxy']] = self.proxy_request_counts[proxy_info['proxy']] + 1
        proxy_url = f"http://{proxy_info['proxy']}"
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
        """Make request with automatic proxy management."""
        if base_headers is None:
            base_headers = {}
        
        # Add random user agent
        base_headers['User-Agent'] = self.user_agent_rotator.get_random()
        
        # Get random headers
        headers = self.headers_manager.get_random_headers(base_headers)
        
        # Force content-type for POST
        if method.upper() == 'POST':
            headers['Content-Type'] = 'application/json'

        while True:
            proxy = self._get_best_proxy(url)
            
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    response = requests.request(
                        method=method,
                        url=url,
                        headers=headers,
                        proxies=proxy,
                        timeout=self.timeout,
                        verify=False,
                        **kwargs
                    )
                response.raise_for_status()
                
                # Update success stats
                self._update_proxy_stats(self._current_proxy['proxy'], True, url)
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed with proxy {self._current_proxy['proxy']}: {str(e)}")
                
                # Update failure stats
                self._update_proxy_stats(self._current_proxy['proxy'], False, url)
                
                # Remove failed proxy from pool
                if self._current_proxy in self.proxies_pool:
                    self.proxies_pool.remove(self._current_proxy)
                
                # Stop if we've tried all proxies
                if not self.proxies_pool:
                    raise

    def get(self, url: str, **kwargs) -> requests.Response:
        """Make GET request."""
        return self.make_request('GET', url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        """Make POST request."""
        return self.make_request('POST', url, **kwargs)

    def get_current_proxy(self) -> Optional[Dict[str, Any]]:
        """Get current proxy info."""
        return self._current_proxy
