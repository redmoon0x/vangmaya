import logging
from src.proxy_manager import get_fast_proxies

logging.basicConfig(level=logging.INFO)

def main():
    print("Fetching and testing proxies...")
    proxies = get_fast_proxies(limit=5)
    
    if not proxies:
        print("No working proxies found.")
        return
        
    print("\nFastest working proxies:")
    print("-" * 50)
    for idx, proxy in enumerate(proxies, 1):
        print(f"{idx}. Proxy: {proxy['proxy']}")
        print(f"   Speed: {proxy['speed']:.2f} seconds")
        print("-" * 50)

if __name__ == "__main__":
    main()
