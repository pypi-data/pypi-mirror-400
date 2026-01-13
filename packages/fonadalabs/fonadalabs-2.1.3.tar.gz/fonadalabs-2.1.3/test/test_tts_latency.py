#!/usr/bin/env python3
"""
FonadaLabs TTS SDK - Latency Test Suite
Tests TTS functionality and measures latency for HTTP and WebSocket methods
"""

import os
import time
import asyncio
from pathlib import Path
from fonadalabs import TTSClient

# Configuration
API_KEY = os.getenv("FONADALABS_API_KEY", "your-api-key-here")
TEST_TEXTS = [
    "नमस्ते! यह FonadaLabs TTS SDK का परीक्षण है।",
    "Hello! This is a test of the FonadaLabs TTS SDK.",
    "यह एक लंबा टेक्स्ट है जो TTS की गुणवत्ता और प्रदर्शन का परीक्षण करने के लिए उपयोग किया जाता है।",
]
VOICES = ["Pravaha", "Shruti", "Aabha", "Svara", "Vaanee"]
OUTPUT_DIR = Path("tts_test_outputs")


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_result(label, value, unit=""):
    """Print formatted result"""
    print(f"  ✓ {label}: {value} {unit}")


class TTSLatencyTest:
    def __init__(self, api_key: str):
        self.client = TTSClient(api_key=api_key)
        OUTPUT_DIR.mkdir(exist_ok=True)
        self.results = []

    def test_http_post(self, text: str, voice: str, output_file: str):
        """Test HTTP POST method with latency measurement"""
        print(f"\n🔹 Testing HTTP POST - Voice: {voice}")
        
        start_time = time.time()
        try:
            audio_data = self.client.generate_audio(
                text=text,
                voice=voice,
                output_file=output_file
            )
            latency = (time.time() - start_time) * 1000  # Convert to ms
            
            audio_size = len(audio_data)
            print_result("Latency", f"{latency:.2f}", "ms")
            print_result("Audio size", f"{audio_size:,}", "bytes")
            print_result("Output", output_file)
            
            self.results.append({
                "method": "HTTP POST",
                "voice": voice,
                "latency_ms": latency,
                "audio_size": audio_size,
                "success": True
            })
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            self.results.append({
                "method": "HTTP POST",
                "voice": voice,
                "latency_ms": None,
                "audio_size": None,
                "success": False,
                "error": str(e)
            })
            return False

    def test_websocket(self, text: str, voice: str, output_file: str):
        """Test WebSocket method with latency measurement"""
        print(f"\n🔹 Testing WebSocket - Voice: {voice}")
        
        chunks_received = []
        start_time = time.time()
        first_chunk_time = None
        
        def on_chunk(chunk_num, chunk_bytes):
            nonlocal first_chunk_time
            if first_chunk_time is None:
                first_chunk_time = time.time()
            chunks_received.append((chunk_num, len(chunk_bytes)))
        
        try:
            audio_data = self.client.generate_audio_ws(
                text=text,
                voice=voice,
                output_file=output_file,
                on_chunk=on_chunk
            )
            
            total_latency = (time.time() - start_time) * 1000
            first_chunk_latency = (first_chunk_time - start_time) * 1000 if first_chunk_time else 0
            
            print_result("Total latency", f"{total_latency:.2f}", "ms")
            print_result("First chunk latency", f"{first_chunk_latency:.2f}", "ms")
            print_result("Chunks received", len(chunks_received))
            print_result("Audio size", f"{len(audio_data):,}", "bytes")
            print_result("Output", output_file)
            
            self.results.append({
                "method": "WebSocket",
                "voice": voice,
                "total_latency_ms": total_latency,
                "first_chunk_latency_ms": first_chunk_latency,
                "chunks": len(chunks_received),
                "audio_size": len(audio_data),
                "success": True
            })
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            self.results.append({
                "method": "WebSocket",
                "voice": voice,
                "total_latency_ms": None,
                "success": False,
                "error": str(e)
            })
            return False

    async def test_async(self, text: str, voice: str, output_file: str):
        """Test async method with latency measurement"""
        print(f"\n🔹 Testing Async - Voice: {voice}")
        
        start_time = time.time()
        try:
            audio_data = await self.client.generate_audio_async(
                text=text,
                voice=voice,
                output_file=output_file
            )
            latency = (time.time() - start_time) * 1000
            
            print_result("Latency", f"{latency:.2f}", "ms")
            print_result("Audio size", f"{len(audio_data):,}", "bytes")
            print_result("Output", output_file)
            
            self.results.append({
                "method": "Async",
                "voice": voice,
                "latency_ms": latency,
                "audio_size": len(audio_data),
                "success": True
            })
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            self.results.append({
                "method": "Async",
                "voice": voice,
                "latency_ms": None,
                "success": False,
                "error": str(e)
            })
            return False

    def test_multiple_voices(self):
        """Test all available voices"""
        print_header("Testing All Voices (HTTP POST)")
        text = TEST_TEXTS[0]
        
        for voice in VOICES:
            output_file = OUTPUT_DIR / f"test_voice_{voice.lower()}.wav"
            self.test_http_post(text, voice, str(output_file))
            time.sleep(0.5)  # Small delay between requests

    def test_latency_comparison(self):
        """Compare latency between HTTP and WebSocket"""
        print_header("Latency Comparison: HTTP vs WebSocket")
        text = TEST_TEXTS[0]
        voice = "Pravaha"
        
        # HTTP test
        http_file = OUTPUT_DIR / "latency_http.wav"
        self.test_http_post(text, voice, str(http_file))
        
        time.sleep(1)
        
        # WebSocket test
        ws_file = OUTPUT_DIR / "latency_ws.wav"
        self.test_websocket(text, voice, str(ws_file))

    async def test_concurrent_async(self):
        """Test concurrent async requests"""
        print_header("Concurrent Async Requests (3 requests)")
        
        start_time = time.time()
        tasks = [
            self.test_async(TEST_TEXTS[0], "Pravaha", str(OUTPUT_DIR / "async_1.wav")),
            self.test_async(TEST_TEXTS[0], "Shruti", str(OUTPUT_DIR / "async_2.wav")),
            self.test_async(TEST_TEXTS[0], "Aabha", str(OUTPUT_DIR / "async_3.wav")),
        ]
        
        results = await asyncio.gather(*tasks)
        total_time = (time.time() - start_time) * 1000
        
        print(f"\n  ✓ Total time (concurrent): {total_time:.2f} ms")
        print(f"  ✓ Successful: {sum(results)}/{len(results)}")

    def print_summary(self):
        """Print test summary and statistics"""
        print_header("Test Summary")
        
        successful = sum(1 for r in self.results if r.get("success", False))
        total = len(self.results)
        
        print(f"\n  Total Tests: {total}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {total - successful}")
        
        # Calculate average latencies
        http_latencies = [r["latency_ms"] for r in self.results 
                         if r.get("method") == "HTTP POST" and r.get("latency_ms")]
        ws_latencies = [r["total_latency_ms"] for r in self.results 
                       if r.get("method") == "WebSocket" and r.get("total_latency_ms")]
        
        if http_latencies:
            avg_http = sum(http_latencies) / len(http_latencies)
            print(f"\n  Average HTTP POST Latency: {avg_http:.2f} ms")
        
        if ws_latencies:
            avg_ws = sum(ws_latencies) / len(ws_latencies)
            print(f"  Average WebSocket Latency: {avg_ws:.2f} ms")
            
            ws_first_chunk = [r["first_chunk_latency_ms"] for r in self.results 
                             if r.get("method") == "WebSocket" and r.get("first_chunk_latency_ms")]
            if ws_first_chunk:
                avg_first_chunk = sum(ws_first_chunk) / len(ws_first_chunk)
                print(f"  Average First Chunk Latency: {avg_first_chunk:.2f} ms")
        
        print(f"\n  Output directory: {OUTPUT_DIR.absolute()}")
        print("=" * 70 + "\n")


def main():
    """Main test runner"""
    print_header("FonadaLabs TTS SDK - Latency Test Suite")
    
    if API_KEY == "your-api-key-here":
        print("\n❌ Error: Please set FONADALABS_API_KEY environment variable")
        print("   Example: export FONADALABS_API_KEY='your-api-key'\n")
        return
    
    tester = TTSLatencyTest(API_KEY)
    
    try:
        # Test 1: All voices
        tester.test_multiple_voices()
        
        # Test 2: Latency comparison
        tester.test_latency_comparison()
        
        # Test 3: Concurrent async
        print_header("Running Async Tests")
        asyncio.run(tester.test_concurrent_async())
        
        # Print summary
        tester.print_summary()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()



