import requests
import warnings
import logging
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from .user_agent_rotator import UserAgentRotator
from .headers_manager import HeadersManager
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
warnings.filterwarnings('ignore')
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class RequestManager:
    def __init__(self, timeout: int = 70):  # Recommended 70s timeout by ScraperAPI
        """Initialize RequestManager."""
        self.timeout = timeout
        self.user_agent_rotator = UserAgentRotator()
        self.headers_manager = HeadersManager()
        self.max_retries = 3
        self.api_key = os.getenv('SCRAPER_API_KEY')
        
        if not self.api_key:
            raise ValueError("SCRAPER_API_KEY not found in environment variables")
        
        # Using proxy port approach for better session handling and IP rate limiting bypass
        self.proxy = f"http://scraperapi:{self.api_key}@proxy-server.scraperapi.com:8001"

    def make_request(
        self,
        method: str,
        url: str,
        base_headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """Make request using Scraper API proxy port."""
        if base_headers is None:
            base_headers = {}

        headers = self.headers_manager.get_random_headers({
            **base_headers,
            'User-Agent': self.user_agent_rotator.get_random()
        })
        
        if method.upper() == 'POST':
            headers['Content-Type'] = 'application/json'

        request_timeout = kwargs.pop('timeout', self.timeout)
        
        # Setup proxy configuration
        proxies = {
            'http': self.proxy,
            'https': self.proxy
        }

        errors = []
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Making request attempt {attempt + 1} of {self.max_retries}")
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    proxies=proxies,
                    timeout=request_timeout,
                    verify=False,  # Required for proxy usage
                    **kwargs
                )
                response.raise_for_status()
                logger.info("Request successful")
                return response

            except Exception as e:
                error = f"Request failed on attempt {attempt + 1}: {str(e)}"
                logger.warning(error)
                errors.append(error)
                
                if attempt == self.max_retries - 1:
                    raise Exception(f"All retries failed.\nLast {min(3, len(errors))} errors:\n" + 
                                 "\n".join(errors[-3:]))

    def get(self, url: str, **kwargs) -> requests.Response:
        """Make GET request."""
        return self.make_request('GET', url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        """Make POST request."""
        return self.make_request('POST', url, **kwargs)
