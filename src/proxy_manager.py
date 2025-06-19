import requests
import logging
import concurrent.futures
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class ProxyManager:
    def __init__(self):
        self.proxy_urls = [
            'http://207.180.209.185:5000/ips.txt',
            'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'
        ]
        self.test_url = 'http://httpbin.org/get'
        self.timeout = 1  # Super short timeout for filtering
        self.batch_size = 200  # Test more proxies at once

    def fetch_proxies(self) -> List[str]:
        """Fetch proxies from all sources."""
        proxies = set()
        
        for url in self.proxy_urls:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    new_proxies = response.text.strip().split('\n')
                    new_proxies = [p.strip() for p in new_proxies if p.strip() and ':' in p]
                    proxies.update(new_proxies)
                    logger.info(f"Fetched {len(new_proxies)} proxies from {url}")
            except Exception as e:
                logger.error(f"Error fetching proxies from {url}: {str(e)}")
        
        return list(proxies)

    def test_proxy(self, proxy: str) -> Dict:
        """Quick test proxy against httpbin."""
        proxy_dict = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        
        try:
            response = requests.get(
                self.test_url,
                proxies=proxy_dict,
                timeout=self.timeout,
                verify=False
            )
            if response.status_code == 200 and response.elapsed.total_seconds() < 1:
                # Only accept proxies that respond within 1 second
                logger.info(f"Found fast proxy: {proxy} ({response.elapsed.total_seconds():.2f}s)")
                return {
                    'proxy': proxy,
                    'working': True
                }
        except:
            pass
        
        return {
            'proxy': proxy,
            'working': False
        }

    def get_proxies(self) -> List[str]:
        """Get list of fast working proxies."""
        all_proxies = self.fetch_proxies()
        logger.info(f"Quick testing {len(all_proxies)} proxies...")
        working_proxies = []

        with ThreadPoolExecutor(max_workers=self.batch_size) as executor:
            futures = []
            for batch_start in range(0, len(all_proxies), self.batch_size):
                batch = all_proxies[batch_start:batch_start + self.batch_size]
                futures.extend([
                    executor.submit(self.test_proxy, proxy)
                    for proxy in batch
                ])

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if result['working']:
                        working_proxies.append(result['proxy'])
                except:
                    continue
                
                # Stop if we have enough proxies
                if len(working_proxies) >= 20:
                    logger.info("Found enough working proxies")
                    break

        logger.info(f"Found {len(working_proxies)} fast proxies")
        return working_proxies

def get_proxy_list() -> List[str]:
    """Get list of pre-tested working proxies."""
    manager = ProxyManager()
    return manager.get_proxies()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    proxies = get_proxy_list()
    print(f"\nFound {len(proxies)} fast proxies")
