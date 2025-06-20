import logging
from src.request_manager import RequestManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_scraper_api():
    print("Testing Scraper API integration...")
    rm = RequestManager()
    
    test_urls = [
        # Basic test
        'https://admin.models.ai4bharat.org/health',
        # Test with a site that often has rate limiting
        'https://api.github.com/users/microsoft',
        # Test with a site that requires JS rendering
        'https://www.amazon.com/dp/B08L5R1CCC'
    ]
    
    for url in test_urls:
        try:
            print(f"\nTesting URL: {url}")
            response = rm.get(url)
            print(f"✓ Basic request successful! Status code: {response.status_code}")
            
            # The proxy port automatically handles features like:
            # - Session persistence
            # - IP rotation when needed
            # - Automatic retries
            # - Geotargeting (uses optimal location for each site)
            # - JavaScript rendering when needed
            
        except Exception as e:
            print(f"✗ Request failed: {str(e)}")
            continue
            
    print("\nScraperAPI proxy port integration test complete!")

if __name__ == "__main__":
    test_scraper_api()
