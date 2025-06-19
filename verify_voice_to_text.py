from voice_to_text import VoiceToTextConverter
import time
import random

def test_voice_to_text_with_load():
    converter = VoiceToTextConverter()
    
    # Test audio files
    test_files = [
        "Record (online-voice-recorder.com) (1).mp3"  # Test audio file
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
    
    print("Starting rapid voice-to-text test with proxy rotation...")
    print("Making 20 consecutive requests to test rate limit bypass...")
    print("-" * 50)
    
    start_total = time.time()
    
    for i in range(20):  # Make 20 rapid requests
        audio_file = test_files[0]  # Use first test file for now
        target = random.choice(target_langs)
        
        print(f"\nRequest {i + 1}/20 to {converter.SUPPORTED_LANGUAGES[target]}")
        
        # Show proxy pool status
        working_count = len([p for p in converter.request_manager.proxies_pool if p['proxy'] not in converter.request_manager.failed_proxies])
        failed_count = len(converter.request_manager.failed_proxies)
        print(f"Proxy Pool Status: {working_count} working, {failed_count} blacklisted")
        
        try:
            start_time = time.time()
            result = converter.transcribe(audio_file, target)
            duration = time.time() - start_time
            
            # Extract text from nested response
            if 'output' in result and len(result['output']) > 0:
                text = result['output'][0].get('source', '')
                if text:  # Only count as success if we got text
                    total_time += duration
                    fastest_time = min(fastest_time, duration)
                    slowest_time = max(slowest_time, duration)
                    successful_requests += 1
                    
                    proxy_info = converter.request_manager.get_current_proxy()
                    if proxy_info:
                        proxy = proxy_info['proxy']
                        used_proxies[proxy] = used_proxies.get(proxy, 0) + 1
                    
                    print(f"✓ {duration:.2f}s | {text}")
                    if proxy_info:
                        proxy = proxy_info['proxy']
                        successes = converter.request_manager.proxy_success_counts[proxy]
                        failures = converter.request_manager.proxy_failure_counts[proxy]
                        total = successes + failures
                        success_rate = (successes / total * 100) if total > 0 else 0
                        
                        print(f"  └─ Proxy: {proxy}")
                        print(f"     Speed: {proxy_info['speed']:.2f}s")
                        print(f"     Success/Fail: {successes}/{failures}")
                        print(f"     Success Rate: {success_rate:.1f}%")
                else:
                    raise Exception("No text in response")
            else:
                raise Exception("Invalid response format")
            
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
            converter.request_manager.proxy_success_counts[proxy] /
            (converter.request_manager.proxy_success_counts[proxy] + 
             converter.request_manager.proxy_failure_counts[proxy]) * 100
            if converter.request_manager.proxy_success_counts[proxy] > 0 else 0
        )
        print(f"Proxy {proxy}:")
        print(f"  Requests: {count}")
        print(f"  Success Rate: {success_rate:.1f}%")
    print("-" * 50)

if __name__ == "__main__":
    test_voice_to_text_with_load()
