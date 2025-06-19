import logging
from src.proxy_manager import ProxyManager
from src.request_manager import RequestManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_proxies():
    print("Testing proxy manager...")
    pm = ProxyManager()
    proxies = pm.get_working_proxies()
    print(f"\nFound {len(proxies)} working proxies:")
    for p in proxies:
        print(f"Proxy: {p['proxy']}, Speed: {p['speed']:.2f}s")
        
    print("\nTesting request manager with proxies...")
    rm = RequestManager()
    try:
        response = rm.get('https://admin.models.ai4bharat.org/health')
        print(f"API connection successful with proxy: {rm.get_current_proxy()['proxy']}")
    except Exception as e:
        print(f"API test failed: {str(e)}")

if __name__ == "__main__":
    test_proxies()
