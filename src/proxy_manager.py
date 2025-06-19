import requests
import concurrent.futures
import time
import asyncio
from typing import List, Dict, Optional
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class ProxyManager:
    def __init__(self):
        self.proxy_urls = [
            'http://207.180.209.185:5000/ips.txt',
            'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'
        ]
        self.test_url = 'http://httpbin.org/get'  # URL to test proxies
        self.timeout = 5  # Reduced timeout for faster testing
        self.max_workers = 20  # Maximum number of concurrent workers

    async def fetch_url(self, url: str) -> List[str]:
        """Fetch proxies from a single URL."""
        try:
            async with concurrent.futures.ThreadPoolExecutor() as executor:
                response = await asyncio.get_event_loop().run_in_executor(
                    executor,
                    lambda: requests.get(url, timeout=self.timeout)
                )
                if response.status_code == 200:
                    new_proxies = response.text.strip().split('\n')
                    new_proxies = [p.strip() for p in new_proxies if p.strip()]
                    logger.debug(f"Fetched {len(new_proxies)} proxies from {url}")
                    return new_proxies
        except Exception as e:
            logger.error(f"Error fetching proxies from {url}: {str(e)}")
        return []

    def fetch_proxies(self) -> List[str]:
        """Fetch proxies from all sources concurrently."""
        proxies = set()
        
        # Create event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Gather tasks
        tasks = [self.fetch_url(url) for url in self.proxy_urls]
        results = loop.run_until_complete(asyncio.gather(*tasks))
        
        # Close loop
        loop.close()
        
        # Combine results
        for proxy_list in results:
            proxies.update(proxy_list)
        
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
                timeout=self.timeout,
                verify=False
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

    def get_working_proxies(self, max_workers: Optional[int] = None) -> List[Dict]:
        """
        Fetch and test proxies concurrently, return working ones sorted by speed.
        
        Args:
            max_workers (int, optional): Maximum number of concurrent workers for testing proxies.
                                       If not provided, uses self.max_workers
            
        Returns:
            List[Dict]: List of working proxies with their speeds, sorted fastest first
        """
        if max_workers is None:
            max_workers = self.max_workers

        # Fetch proxies concurrently
        proxies = self.fetch_proxies()
        logger.info(f"Testing {len(proxies)} proxies with {max_workers} workers...")
        working_proxies = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all proxy tests
            future_to_proxy = {
                executor.submit(self.test_proxy, proxy): proxy 
                for proxy in proxies
            }
            
            # Process results as they complete
            for i, future in enumerate(as_completed(future_to_proxy), 1):
                result = future.result()
                if result:
                    working_proxies.append(result)
                    logger.info(f"Progress: {i}/{len(proxies)} - Found working proxy: {result['proxy']} (Speed: {result['speed']:.2f}s)")
                else:
                    logger.debug(f"Progress: {i}/{len(proxies)} - Proxy failed")

        # Sort proxies by speed
        working_proxies.sort(key=lambda x: x['speed'])
        
        logger.info(f"Found {len(working_proxies)} working proxies")
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
