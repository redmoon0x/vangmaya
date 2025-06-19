import requests
import concurrent.futures
import time
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ProxyManager:
    def __init__(self):
        self.proxy_urls = [
            'http://207.180.209.185:5000/ips.txt',
            'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'
        ]
        self.test_url = 'http://httpbin.org/get'  # URL to test proxies
        self.timeout = 10  # Timeout in seconds for proxy tests

    def fetch_proxies(self) -> List[str]:
        """Fetch proxies from all sources and return as a list."""
        proxies = set()
        
        for url in self.proxy_urls:
            try:
                response = requests.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    # Split text into lines and clean up
                    new_proxies = response.text.strip().split('\n')
                    new_proxies = [p.strip() for p in new_proxies if p.strip()]
                    proxies.update(new_proxies)
                    logger.debug(f"Fetched {len(new_proxies)} proxies from {url}")
            except Exception as e:
                logger.error(f"Error fetching proxies from {url}: {str(e)}")
        
        return list(proxies)

    def test_proxy(self, proxy: str) -> Optional[Dict]:
        """Test a single proxy and return its details if working."""
        proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        
        try:
            start_time = time.time()
            response = requests.get(
                self.test_url,
                proxies=proxies,
                timeout=self.timeout
            )
            speed = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    'proxy': proxy,
                    'speed': speed,
                    'status': 'working'
                }
        except Exception as e:
            logger.debug(f"Proxy {proxy} failed: {str(e)}")
        
        return None

    def get_working_proxies(self, max_workers: int = 50) -> List[Dict]:
        """
        Fetch and test proxies, return working ones sorted by speed.
        
        Args:
            max_workers (int): Maximum number of concurrent workers for testing proxies
            
        Returns:
            List[Dict]: List of working proxies with their speeds, sorted fastest first
        """
        proxies = self.fetch_proxies()
        logger.debug(f"Testing {len(proxies)} proxies...")
        working_proxies = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {
                executor.submit(self.test_proxy, proxy): proxy 
                for proxy in proxies
            }
            
            for future in concurrent.futures.as_completed(future_to_proxy):
                result = future.result()
                if result:
                    working_proxies.append(result)
                    logger.debug(f"Found working proxy: {result['proxy']} (Speed: {result['speed']:.2f}s)")

        # Sort proxies by speed
        working_proxies.sort(key=lambda x: x['speed'])
        
        logger.debug(f"Found {len(working_proxies)} working proxies")
        return working_proxies

def get_fast_proxies(limit: int = 10) -> List[Dict]:
    """
    Convenience function to get the fastest working proxies.
    
    Args:
        limit (int): Maximum number of proxies to return
        
    Returns:
        List[Dict]: List of the fastest working proxies
    """
    manager = ProxyManager()
    proxies = manager.get_working_proxies()
    return proxies[:limit]

if __name__ == '__main__':
    # Example usage
    fast_proxies = get_fast_proxies(limit=5)
    print("\nFastest working proxies:")
    for proxy in fast_proxies:
        print(f"Proxy: {proxy['proxy']}, Speed: {proxy['speed']:.2f}s")
