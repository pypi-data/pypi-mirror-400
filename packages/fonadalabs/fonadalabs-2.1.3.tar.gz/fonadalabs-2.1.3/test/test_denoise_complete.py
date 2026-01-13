#!/usr/bin/env python3
"""
Complete Denoise SDK Test Suite
Tests all available endpoints and functionality of the Denoise SDK

Note: Some SDK methods (denoise_base64, denoise_numpy, denoise_stream) are not
tested because they rely on non-existent API endpoints.
"""

import os
import sys
import time
import base64
import numpy as np

# Add SDK to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fonadalabs import DenoiseHttpClient, DenoiseStreamingClient

# Configuration
API_KEY = os.getenv("FONADALABS_API_KEY", "sk_ae283a1d3f602b7c96a3068260b42dc8a71a89624569fdf3")
os.environ["FONADALABS_DENOISE_URL"] = os.getenv("FONADALABS_DENOISE_URL", "http://localhost:9559")

# Test audio file - use absolute path based on script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_AUDIO = os.path.join(SCRIPT_DIR, "../../backend/denoise/test/test_audio/Technical_noisy.wav")
TEST_AUDIO = os.path.normpath(TEST_AUDIO)  # Normalize the path

print("=" * 80)
print("COMPLETE DENOISE SDK TEST SUITE")
print("=" * 80)
print(f"API URL: {os.environ['FONADALABS_DENOISE_URL']}")
print(f"API Key: {API_KEY[:20]}...")
print(f"Test Audio: {TEST_AUDIO}")
print("=" * 80)

# Test Results Tracking
tests_passed = 0
tests_failed = 0
test_results = []

def log_test(test_name, passed, message="", duration=0):
    """Log test result"""
    global tests_passed, tests_failed
    status = "✅ PASS" if passed else "❌ FAIL"
    if passed:
        tests_passed += 1
    else:
        tests_failed += 1
    
    result = f"{status} | {test_name}"
    if duration > 0:
        result += f" ({duration:.2f}s)"
    if message:
        result += f" - {message}"
    
    print(result)
    test_results.append((test_name, passed, message, duration))

# ============================================================================
# TEST 1: Health Check
# ============================================================================
print("\n" + "=" * 80)
print("TEST 1: Health Check Endpoint")
print("=" * 80)

try:
    client = DenoiseHttpClient(api_key=API_KEY)
    start = time.time()
    health = client.health_check()
    duration = time.time() - start
    
    if health and "status" in health:
        log_test("Health Check", True, f"Status: {health.get('status')}", duration)
        print(f"   Engine Loaded: {health.get('engine_loaded')}")
        print(f"   Active Requests: {health.get('active_requests')}")
        print(f"   Available Slots: {health.get('available_slots')}")
    else:
        log_test("Health Check", False, "Invalid response format", duration)
except Exception as e:
    log_test("Health Check", False, str(e))

# ============================================================================
# TEST 2: Full Audio Denoising (denoise_file)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: Full Audio Denoising (denoise_file)")
print("=" * 80)

try:
    client = DenoiseHttpClient(api_key=API_KEY, timeout=300)
    
    if not os.path.exists(TEST_AUDIO):
        log_test("Full Audio Denoise", False, f"Test audio file not found: {TEST_AUDIO}")
    else:
        start = time.time()
        output_file = "test_output_full_denoise.wav"
        denoised = client.denoise_file(TEST_AUDIO, output_file)
        duration = time.time() - start
        
        if denoised and len(denoised) > 0:
            log_test("Full Audio Denoise", True, f"Output: {len(denoised)/1024:.2f} KB", duration)
            print(f"   Saved to: {output_file}")
            print(f"   File size: {os.path.getsize(output_file)/1024:.2f} KB")
        else:
            log_test("Full Audio Denoise", False, "Empty output", duration)
except FileNotFoundError as e:
    log_test("Full Audio Denoise", False, f"File not found: {e}")
except Exception as e:
    log_test("Full Audio Denoise", False, str(e))

# ============================================================================
# TEST 3: Full Audio Denoising without output file
# ============================================================================
print("\n" + "=" * 80)
print("TEST 3: Full Audio Denoising (return bytes only)")
print("=" * 80)

try:
    client = DenoiseHttpClient(api_key=API_KEY, timeout=300)
    
    if not os.path.exists(TEST_AUDIO):
        log_test("Denoise Return Bytes", False, f"Test audio file not found: {TEST_AUDIO}")
    else:
        start = time.time()
        denoised = client.denoise_file(TEST_AUDIO)
        duration = time.time() - start
        
        if denoised and len(denoised) > 0:
            log_test("Denoise Return Bytes", True, f"Output: {len(denoised)/1024:.2f} KB", duration)
            
            # Save manually
            manual_output = "test_output_manual.wav"
            client.save_audio(denoised, manual_output)
            print(f"   Manually saved to: {manual_output}")
        else:
            log_test("Denoise Return Bytes", False, "Empty output", duration)
except Exception as e:
    log_test("Denoise Return Bytes", False, str(e))

# ============================================================================
# TEST 4: Base64 Audio Denoising
# ============================================================================
print("\n" + "=" * 80)
print("TEST 4: Base64 Audio Denoising (denoise_base64)")
print("=" * 80)

try:
    client = DenoiseHttpClient(api_key=API_KEY, timeout=300)
    
    if not os.path.exists(TEST_AUDIO):
        log_test("Base64 Denoise", False, f"Test audio file not found: {TEST_AUDIO}")
    else:
        # Encode audio to base64
        with open(TEST_AUDIO, "rb") as f:
            audio_bytes = f.read()
        audio_b64 = base64.b64encode(audio_bytes).decode()
        
        start = time.time()
        denoised = client.denoise_base64(audio_b64, filename="test_audio.wav")
        duration = time.time() - start
        
        if denoised and len(denoised) > 0:
            # Save result
            output_file = "test_output_base64.wav"
            with open(output_file, "wb") as f:
                f.write(denoised)
            
            log_test("Base64 Denoise", True, f"Output: {len(denoised)/1024:.2f} KB", duration)
            print(f"   Saved to: {output_file}")
        else:
            log_test("Base64 Denoise", False, "Empty output", duration)
except Exception as e:
    log_test("Base64 Denoise", False, str(e))

# ============================================================================
# TEST 5: Numpy Array Denoising
# ============================================================================
print("\n" + "=" * 80)
print("TEST 5: Numpy Array Denoising (denoise_numpy)")
print("=" * 80)

try:
    import soundfile as sf
    
    client = DenoiseHttpClient(api_key=API_KEY, timeout=300)
    
    if not os.path.exists(TEST_AUDIO):
        log_test("Numpy Denoise", False, f"Test audio file not found: {TEST_AUDIO}")
    else:
        # Load audio as numpy array
        audio_array, sr = sf.read(TEST_AUDIO)
        
        start = time.time()
        denoised_array = client.denoise_numpy(audio_array, sample_rate=sr)
        duration = time.time() - start
        
        if denoised_array is not None and len(denoised_array) > 0:
            # Save as WAV
            output_file = "test_output_numpy.wav"
            sf.write(output_file, denoised_array, 16000)
            
            log_test("Numpy Denoise", True, f"Array shape: {denoised_array.shape}", duration)
            print(f"   Saved to: {output_file}")
            print(f"   Sample rate: 16000 Hz")
        else:
            log_test("Numpy Denoise", False, "Empty output", duration)
except ImportError:
    log_test("Numpy Denoise", False, "soundfile not installed (pip install soundfile)")
except Exception as e:
    log_test("Numpy Denoise", False, str(e))

# ============================================================================
# TEST 6: Streaming Client Server Status
# ============================================================================
print("\n" + "=" * 80)
print("TEST 6: Streaming Client Server Status")
print("=" * 80)

try:
    streaming_client = DenoiseStreamingClient(api_key=API_KEY)
    
    start = time.time()
    status = streaming_client.get_batch_status()
    duration = time.time() - start
    
    if status and "server" in status:
        log_test("Server Status", True, f"Server: {status.get('server')}", duration)
        print(f"   Version: {status.get('version')}")
        print(f"   Model: {status.get('model')}")
    else:
        log_test("Server Status", False, "Invalid response format", duration)
except Exception as e:
    log_test("Server Status", False, str(e))

# ============================================================================
# TEST 7: Streaming Client - Chunk Denoising
# ============================================================================
print("\n" + "=" * 80)
print("TEST 7: Streaming Client - Chunk Denoising (denoise_chunk)")
print("=" * 80)

try:
    import soundfile as sf
    
    streaming_client = DenoiseStreamingClient(api_key=API_KEY, timeout=60)
    
    if not os.path.exists(TEST_AUDIO):
        log_test("Chunk Denoise", False, f"Test audio file not found: {TEST_AUDIO}")
    else:
        # Load audio and get one chunk
        audio, sr = sf.read(TEST_AUDIO)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        
        # Get first chunk (10240 samples = 640ms at 16kHz)
        chunk = audio[:10240].astype('float32')
        
        start = time.time()
        denoised_chunk = streaming_client.denoise_chunk(chunk)
        duration = time.time() - start
        
        if denoised_chunk is not None and len(denoised_chunk) > 0:
            log_test("Chunk Denoise", True, f"Chunk shape: {denoised_chunk.shape}", duration)
        else:
            log_test("Chunk Denoise", False, "Empty output", duration)
except ImportError:
    log_test("Chunk Denoise", False, "soundfile not installed")
except Exception as e:
    log_test("Chunk Denoise", False, str(e))

# ============================================================================
# TEST 8: Streaming Client - File Denoising via Chunks
# ============================================================================
print("\n" + "=" * 80)
print("TEST 8: Streaming Client - File Denoising via Chunks (denoise_file)")
print("=" * 80)

try:
    streaming_client = DenoiseStreamingClient(api_key=API_KEY, timeout=120)
    
    if not os.path.exists(TEST_AUDIO):
        log_test("Streaming File Denoise", False, f"Test audio file not found: {TEST_AUDIO}")
    else:
        output_file = "test_output_streaming_chunks.wav"
        
        start = time.time()
        denoised = streaming_client.denoise_file(
            TEST_AUDIO,
            output_path=output_file,
            progress_callback=lambda cur, total: None  # Silent progress
        )
        duration = time.time() - start
        
        if denoised is not None and len(denoised) > 0:
            log_test("Streaming File Denoise", True, f"Output shape: {denoised.shape}", duration)
            print(f"   Saved to: {output_file}")
        else:
            log_test("Streaming File Denoise", False, "Empty output", duration)
except Exception as e:
    log_test("Streaming File Denoise", False, str(e))

# ============================================================================
# TEST 9: WebSocket Streaming Denoising
# ============================================================================
print("\n" + "=" * 80)
print("TEST 9: WebSocket Streaming Denoising (denoise_file_ws)")
print("=" * 80)

try:
    streaming_client = DenoiseStreamingClient(api_key=API_KEY, timeout=120)
    
    if not os.path.exists(TEST_AUDIO):
        log_test("WebSocket Denoise", False, f"Test audio file not found: {TEST_AUDIO}")
    else:
        output_file = "test_output_websocket.wav"
        
        start = time.time()
        denoised = streaming_client.denoise_file_ws(
            TEST_AUDIO,
            output_path=output_file
        )
        duration = time.time() - start
        
        if denoised is not None and len(denoised) > 0:
            log_test("WebSocket Denoise", True, f"Output shape: {denoised.shape}", duration)
            print(f"   Saved to: {output_file}")
        else:
            log_test("WebSocket Denoise", False, "Empty output", duration)
except ImportError as e:
    log_test("WebSocket Denoise", False, f"Missing dependency: {e}")
except Exception as e:
    log_test("WebSocket Denoise", False, str(e))

# ============================================================================
# TEST 10: Error Handling - Invalid API Key
# ============================================================================
print("\n" + "=" * 80)
print("TEST 10: Error Handling - Invalid API Key")
print("=" * 80)

try:
    invalid_client = DenoiseHttpClient(api_key="invalid_api_key_12345")
    
    try:
        invalid_client.denoise_file(TEST_AUDIO)
        log_test("Invalid API Key Error", False, "Should have raised an error")
    except Exception as e:
        if "401" in str(e) or "Unauthorized" in str(e) or "Invalid" in str(e):
            log_test("Invalid API Key Error", True, "Correctly rejected invalid API key")
        else:
            log_test("Invalid API Key Error", False, f"Unexpected error: {e}")
except Exception as e:
    log_test("Invalid API Key Error", False, str(e))

# ============================================================================
# TEST 11: Error Handling - File Not Found
# ============================================================================
print("\n" + "=" * 80)
print("TEST 11: Error Handling - File Not Found")
print("=" * 80)

try:
    client = DenoiseHttpClient(api_key=API_KEY)
    
    try:
        client.denoise_file("nonexistent_file.wav")
        log_test("File Not Found Error", False, "Should have raised FileNotFoundError")
    except FileNotFoundError:
        log_test("File Not Found Error", True, "Correctly raised FileNotFoundError")
    except Exception as e:
        log_test("File Not Found Error", False, f"Unexpected error: {e}")
except Exception as e:
    log_test("File Not Found Error", False, str(e))

# ============================================================================
# TEST 12: Context Manager Support
# ============================================================================
print("\n" + "=" * 80)
print("TEST 12: Context Manager Support")
print("=" * 80)

try:
    with DenoiseHttpClient(api_key=API_KEY) as client:
        health = client.health_check()
        if health and "status" in health:
            log_test("Context Manager", True, "Client works with context manager")
        else:
            log_test("Context Manager", False, "Health check failed")
except Exception as e:
    log_test("Context Manager", False, str(e))

# ============================================================================
# TEST 13: Multiple Sequential Requests
# ============================================================================
print("\n" + "=" * 80)
print("TEST 13: Multiple Sequential Requests")
print("=" * 80)

try:
    client = DenoiseHttpClient(api_key=API_KEY, timeout=300)
    
    if not os.path.exists(TEST_AUDIO):
        log_test("Sequential Requests", False, f"Test audio file not found: {TEST_AUDIO}")
    else:
        num_requests = 3
        start = time.time()
        
        for i in range(num_requests):
            denoised = client.denoise_file(TEST_AUDIO)
            if not denoised or len(denoised) == 0:
                log_test("Sequential Requests", False, f"Request {i+1} failed")
                break
        else:
            duration = time.time() - start
            avg_time = duration / num_requests
            log_test("Sequential Requests", True, f"{num_requests} requests completed, avg: {avg_time:.2f}s", duration)
except Exception as e:
    log_test("Sequential Requests", False, str(e))

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Total Tests: {tests_passed + tests_failed}")
print(f"Passed: {tests_passed} ✅")
print(f"Failed: {tests_failed} ❌")
print(f"Success Rate: {(tests_passed/(tests_passed+tests_failed)*100):.1f}%")
print("=" * 80)

# Detailed results
if tests_failed > 0:
    print("\nFailed Tests:")
    for name, passed, message, duration in test_results:
        if not passed:
            print(f"  ❌ {name}: {message}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)

# Exit with appropriate code
sys.exit(0 if tests_failed == 0 else 1)


