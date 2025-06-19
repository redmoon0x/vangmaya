from translator import TextTranslator
import time
import random

def test_translator_with_load():
    translator = TextTranslator()
    
    # Test phrases to translate
    test_phrases = [
        "Hello how are you?",
        "What are you doing?",
        "This is a test message",
        "Learning new languages is fun",
        "Tell me more about yourself",
        "The weather is nice today",
        "I love learning languages",
        "Can you help me please",
        "What time is it now",
        "Let's meet tomorrow"
    ]
    
    # Target languages to test
    target_langs = ["hi", "ta", "kn", "te", "ml"]
    
    # Track performance metrics
    total_time = 0
    fastest_time = float('inf')
    slowest_time = 0
    successful_requests = 0
    failed_requests = 0
    used_proxies = {}  # Track requests per proxy
    
    print("Starting rapid translation test with proxy rotation...")
    print("Making 50 consecutive requests to test rate limit bypass...")
    print("-" * 50)
    
    start_total = time.time()
    
    for i in range(50):  # Make 50 rapid requests
        phrase = random.choice(test_phrases)
        target = random.choice(target_langs)
        
        print(f"\nRequest {i + 1}/50 to {translator.SUPPORTED_LANGUAGES[target]}")
        
        # Show proxy pool status
        working_count = len([p for p in translator.request_manager.proxies_pool if p['proxy'] not in translator.request_manager.failed_proxies])
        failed_count = len(translator.request_manager.failed_proxies)
        print(f"Proxy Pool Status: {working_count} working, {failed_count} blacklisted")
        
        try:
            start_time = time.time()
            result = translator.translate(phrase, target_lang=target)
            duration = time.time() - start_time
            
            # Update metrics
            total_time += duration
            fastest_time = min(fastest_time, duration)
            slowest_time = max(slowest_time, duration)
            successful_requests += 1
            
            proxy_info = translator.request_manager.get_current_proxy()
            if proxy_info:
                proxy = proxy_info['proxy']
                used_proxies[proxy] = used_proxies.get(proxy, 0) + 1
            
            print(f"✓ {duration:.2f}s | {result}")
            if proxy_info:
                proxy = proxy_info['proxy']
                successes = translator.request_manager.proxy_success_counts[proxy]
                failures = translator.request_manager.proxy_failure_counts[proxy]
                total = successes + failures
                success_rate = (successes / total * 100) if total > 0 else 0
                
                print(f"  └─ Proxy: {proxy}")
                print(f"     Speed: {proxy_info['speed']:.2f}s")
                print(f"     Success/Fail: {successes}/{failures}")
                print(f"     Success Rate: {success_rate:.1f}%")
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            failed_requests += 1
            
    # Calculate and display final stats
    total_duration = time.time() - start_total
    avg_time = total_time / successful_requests if successful_requests > 0 else 0
    
    print("\n" + "="*50)
    print("FINAL STATISTICS")
    print("="*50)
    print(f"Total Duration: {total_duration:.2f} seconds")
    print(f"Successful Requests: {successful_requests}")
    print(f"Failed Requests: {failed_requests}")
    print(f"Average Time per Request: {avg_time:.2f} seconds")
    print(f"Fastest Request: {fastest_time:.2f} seconds")
    print(f"Slowest Request: {slowest_time:.2f} seconds")
    
    print("\nProxy Usage Details:")
    print("-" * 50)
    for proxy, count in used_proxies.items():
        success_rate = (
            translator.request_manager.proxy_success_counts[proxy] /
            (translator.request_manager.proxy_success_counts[proxy] + 
             translator.request_manager.proxy_failure_counts[proxy]) * 100
            if translator.request_manager.proxy_success_counts[proxy] > 0 else 0
        )
        print(f"Proxy {proxy}:")
        print(f"  Requests: {count}")
        print(f"  Success Rate: {success_rate:.1f}%")
    print("-" * 50)

if __name__ == "__main__":
    test_translator_with_load()
