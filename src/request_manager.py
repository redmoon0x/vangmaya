import requests
import warnings
import logging
import random
import time
from typing import Optional, Dict, Any, List, Set
from collections import defaultdict
from .proxy_manager import get_proxy_list
from .user_agent_rotator import UserAgentRotator
from .headers_manager import HeadersManager
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
warnings.filterwarnings('ignore')
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)

class RequestManager:
    def __init__(self, timeout: int = 5):
        """Initialize RequestManager."""
        self.timeout = timeout
        self.user_agent_rotator = UserAgentRotator()
        self.headers_manager = HeadersManager()
        self.max_retries = 10
        
        # Get initial proxy list
        logger.info("Getting proxy list...")
        self.proxy_list = get_proxy_list()
        logger.info(f"Got {len(self.proxy_list)} working proxies")

        # Keep track of working proxies for each domain
        self.domain_proxies = defaultdict(dict)  # domain -> {proxy: last_success_time}
        self.working_proxies: Set[str] = set()

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        return urlparse(url).netloc

    def make_request(
        self,
        method: str,
        url: str,
        base_headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """Make request with proxy rotation and retries."""
        if base_headers is None:
            base_headers = {}

        headers = self.headers_manager.get_random_headers({
            **base_headers,
            'User-Agent': self.user_agent_rotator.get_random()
        })
        
        if method.upper() == 'POST':
            headers['Content-Type'] = 'application/json'

        request_timeout = kwargs.pop('timeout', self.timeout)
        domain = self._get_domain(url)

        # Prioritize proxies:
        # 1. Recently successful proxies for this domain
        # 2. Generally working proxies
        # 3. Random new proxies

        proxies_to_try = []
        
        # Add domain-specific working proxies
        if domain in self.domain_proxies:
            recent = sorted(
                self.domain_proxies[domain].items(),
                key=lambda x: x[1],
                reverse=True
            )
            proxies_to_try.extend([p[0] for p in recent])

        # Add other working proxies
        other_working = [p for p in self.working_proxies if p not in proxies_to_try]
        if other_working:
            proxies_to_try.extend(other_working)

        # Add some random proxies if needed
        if len(proxies_to_try) < self.max_retries:
            remaining = self.max_retries - len(proxies_to_try)
            available = [p for p in self.proxy_list if p not in proxies_to_try]
            if available:
                proxies_to_try.extend(random.sample(available, min(remaining, len(available))))

        errors = []
        for proxy in proxies_to_try:
            proxy_dict = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            
            try:
                logger.info(f"Trying proxy: {proxy}")
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    proxies=proxy_dict,
                    timeout=request_timeout,
                    verify=False,
                    **kwargs
                )
                response.raise_for_status()
                logger.info(f"Request successful with proxy {proxy}")
                
                # Update successful proxy records
                self.working_proxies.add(proxy)
                self.domain_proxies[domain][proxy] = time.time()
                return response

            except Exception as e:
                error = f"Proxy {proxy} failed: {str(e)}"
                logger.warning(error)
                errors.append(error)
                
                # Remove failed proxy
                self.working_proxies.discard(proxy)
                if domain in self.domain_proxies:
                    self.domain_proxies[domain].pop(proxy, None)

        # If we get here, all retries failed
        raise Exception(f"All proxies failed.\nLast {min(3, len(errors))} errors:\n" + 
                      "\n".join(errors[-3:]))

    def get(self, url: str, **kwargs) -> requests.Response:
        """Make GET request."""
        return self.make_request('GET', url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        """Make POST request."""
        return self.make_request('POST', url, **kwargs)
