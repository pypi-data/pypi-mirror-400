# FonadaLabs SDK

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Version 2.0.0](https://img.shields.io/badge/version-2.0.0-green.svg)](https://github.com/fonadalabs/fonadalabs-sdk)

Unified Python SDK for FonadaLabs **Text-to-Speech (TTS)**, **Automatic Speech Recognition (ASR)**, and **Audio Denoising** APIs.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [Text-to-Speech (TTS)](#text-to-speech-tts)
  - [Automatic Speech Recognition (ASR)](#automatic-speech-recognition-asr)
  - [Audio Denoising](#audio-denoising)
- [Authentication](#authentication)
- [Advanced Features](#advanced-features)
- [Error Handling](#error-handling)
- [Security Features](#security-features)
- [Documentation](#documentation)
- [Examples](#examples)
- [Package Structure](#package-structure)
- [Importing](#importing)
- [Requirements](#requirements)
- [License](#license)
- [Support](#support)

## Features

### Text-to-Speech (TTS)
- 🎙️ High-quality text-to-speech generation with multiple voices
- 🌍 **Multi-language support** (Hindi, English, Telugu, Tamil, and more)
- 🚀 HTTP POST and WebSocket support
- 📊 Real-time progress tracking
- ⚡ Async support for concurrent requests
- 🎵 Audio streaming with chunk callbacks
- 🔒 Secure API key authentication
- ⚠️ Built-in error handling for rate limits and credit exhaustion

### Automatic Speech Recognition (ASR)
- 🎤 Audio file transcription
- 🌐 WebSocket streaming for real-time transcription
- 🔄 Concurrent batch processing
- 🌍 Multi-language support (50+ languages)
- 🔒 Secure API key authentication
- ⚠️ Comprehensive error handling

### Audio Denoising
- 🔇 High-quality audio denoising (DeepFilterNet + CMGAN)
- 🎯 Full audio and streaming chunk processing
- ⚡ Real-time WebSocket streaming with progress callbacks
- 📦 Batch processing support
- 🔒 Secure API key authentication
- ⚠️ Built-in rate limit and credit management

## Installation

### From PyPI (Recommended)

```bash
# Install with all dependencies for TTS, ASR, and Denoise
pip install fonadalabs
```

**Note for Windows users:** Make sure you have Python 3.9-3.12 and upgraded pip:
```bash
python -m pip install --upgrade pip setuptools wheel
pip install fonadalabs
```

### From Source (Development)

```bash
git clone https://github.com/fonadalabs/fonadalabs-sdk.git
cd fonadalabs-sdk
pip install -e .
```

### For Development

```bash
# Install with development tools (pytest, black, etc.)
pip install fonadalabs[dev]
```

## Quick Start

### Text-to-Speech (TTS)

```python
from fonadalabs import TTSClient, TTSError, CreditsExhaustedError, RateLimitError

# Initialize with API key (or set FONADALABS_API_KEY env variable)
client = TTSClient(api_key="your-api-key-here")

try:
    # Generate audio with language
    audio_data = client.generate_audio(
        text="नमस्ते! यह FonadaLabs TTS SDK का परीक्षण है।",
        voice="Pravaha",
        language="Hindi",  # Supported: Hindi, English, Telugu, Tamil, etc.
        output_file="output.wav"
    )
    print(f"✓ Generated {len(audio_data)} bytes")
    
except CreditsExhaustedError as e:
    print(f"⚠️ API credits exhausted. Balance: {e.current_balance}")
except RateLimitError as e:
    print(f"⚠️ Rate limit exceeded. Retry after: {e.retry_after_seconds}s")
except TTSError as e:
    print(f"❌ TTS Error: {e}")
```

### Automatic Speech Recognition (ASR)

```python
from fonadalabs import (
    ASRClient, 
    ASRSDKError,
    AuthenticationError,
    ASRCreditsExhaustedError,
    ASRRateLimitError,
    is_supported_language
)

# Initialize with API key (or set FONADALABS_API_KEY env variable)
asr_client = ASRClient(api_key="your-api-key-here")

try:
    # Check if language is supported
    if is_supported_language("hi"):
        print("✓ Hindi is supported!")
    
    # Transcribe audio file
    result = asr_client.transcribe_file(
        audio_path="audio.wav",
        language_id="hi"  # Hindi
    )
    print(f"✓ Transcription: {result.text}")
    print(f"✓ Language: {result.language_id}")
    print(f"✓ File: {result.file_path}")
    
except ASRCreditsExhaustedError as e:
    print(f"⚠️ API credits exhausted. Usage: {e.current_usage}")
except ASRRateLimitError as e:
    print(f"⚠️ Rate limit exceeded. Retry after: {e.retry_after_seconds}s")
except AuthenticationError as e:
    print(f"❌ Authentication failed: {e}")
except ASRSDKError as e:
    print(f"❌ ASR Error: {e}")
```

### Audio Denoising

```python
from fonadalabs import (
    DenoiseHttpClient, 
    DenoiseStreamingClient,
    DenoiseCreditsExhaustedError,
    DenoiseRateLimitError
)

try:
    # Full audio denoising (HTTP)
    http_client = DenoiseHttpClient(api_key="your-api-key-here")
    denoised = http_client.denoise_file("noisy.wav", "clean.wav")
    print("✓ Denoised audio saved to clean.wav")
    
    # Streaming denoising with progress
    streaming_client = DenoiseStreamingClient(api_key="your-api-key-here")
    
    def progress_callback(current, total):
        percent = (current / total) * 100
        print(f"Progress: {current}/{total} chunks ({percent:.1f}%)")
    
    denoised = streaming_client.denoise_file(
        "noisy.wav", 
        "clean.wav",
        progress_callback=progress_callback
    )
    print("✓ Streaming denoising complete!")
    
except DenoiseCreditsExhaustedError:
    print("⚠️ API credits exhausted. Please add more credits.")
except DenoiseRateLimitError:
    print("⚠️ Rate limit exceeded. Please try again later.")
except Exception as e:
    print(f"❌ Denoise Error: {e}")
```

## Authentication

All FonadaLabs APIs require API key authentication. You can obtain your API key from the [FonadaLabs Dashboard](https://fonadalabs.com/dashboard).

### Method 1: Environment Variable (Recommended)

```bash
# Set environment variable
export FONADALABS_API_KEY=your-api-key-here

# Or add to .env file
echo "FONADALABS_API_KEY=your-api-key-here" >> .env
```

Then use the SDK without passing the key:

```python
from fonadalabs import TTSClient, ASRClient, DenoiseHttpClient

# API key is automatically loaded from environment
tts_client = TTSClient()
asr_client = ASRClient()
denoise_client = DenoiseHttpClient()
```

### Method 2: Pass Directly in Code

```python
from fonadalabs import TTSClient, ASRClient, DenoiseHttpClient

tts_client = TTSClient(api_key="your-api-key")
asr_client = ASRClient(api_key="your-api-key")
denoise_client = DenoiseHttpClient(api_key="your-api-key")
```

**⚠️ Security Note:** Never hardcode API keys in your source code. Always use environment variables or secure key management systems.

## Advanced Features

### Available TTS Voices

FonadaLabs TTS supports multiple high-quality Hindi voices:

| Voice Name | Description | Gender | Best For |
|-----------|-------------|--------|----------|
| **Pravaha** | Clear, professional | Female | Business, formal content |
| **Shruti** | Warm, friendly | Female | Casual conversation, storytelling |
| **Aabha** | Energetic, bright | Female | Educational, upbeat content |
| **Svara** | Melodious, soft | Female | Audiobooks, meditation |
| **Vaanee** | Strong, confident | Female | News, announcements |

**Usage:**
```python
from fonadalabs import TTSClient

client = TTSClient(api_key="your-api-key")

# Test different voices
for voice in ["Pravaha", "Shruti", "Aabha", "Svara", "Vaanee"]:
    audio = client.generate_audio(
        text="यह एक आवाज़ का परीक्षण है।",
        voice=voice,
        language="Hindi",
        output_file=f"test_{voice.lower()}.wav"
    )
    print(f"✓ Generated audio with {voice} voice")
```

### Supported TTS Languages

| Language | Name | Example |
|----------|------|---------|
| Hindi | `Hindi` | नमस्ते |
| English | `English` | Hello |
| Telugu | `Telugu` | నమస్కారం |
| Tamil | `Tamil` | வணக்கம் |

**Multi-language Example:**
```python
# Generate audio in different languages
client.generate_audio("Hello!", "Pravaha", "English", "english.wav")
client.generate_audio("నమస్కారం!", "Pravaha", "Telugu", "telugu.wav")
client.generate_audio("வணக்கம்!", "Pravaha", "Tamil", "tamil.wav")
```
### Context Manager Support

Use TTSClient with Python's context manager for automatic resource cleanup:

```python
from fonadalabs import TTSClient

# Resources are automatically cleaned up after the block
with TTSClient(api_key="your-api-key") as client:
    audio = client.generate_audio(
        text="Testing context manager",
        voice="Pravaha",
        language="English",
        output_file="output.wav"
    )
    print(f"Generated: {len(audio)} bytes")

# Client is automatically closed here
print("Resources cleaned up automatically!")
```

### WebSocket Streaming (TTS)

Stream audio with real-time progress updates and callbacks:

```python
from fonadalabs import TTSClient

client = TTSClient(api_key="your-api-key")

# Define callbacks for streaming events
def on_chunk(chunk_num, chunk_bytes):
    print(f"📦 Chunk {chunk_num} received: {len(chunk_bytes)} bytes")

def on_complete(stats):
    print(f"✅ Complete! Chunks: {stats.get('chunks_sent')}, Bytes: {stats.get('bytes_sent')}")

def on_error(error_msg):
    print(f"❌ Error: {error_msg}")

# Generate audio via WebSocket with callbacks
audio = client.generate_audio_ws(
    text="Hello! This is a WebSocket streaming test.",
    voice="Shruti",
    language="English",
    output_file="output.wav",
    on_chunk=on_chunk,
    on_complete=on_complete,
    on_error=on_error
)
```

### Async Operations (TTS)

Use async methods for concurrent requests:

```python
import asyncio
from fonadalabs import TTSClient

client = TTSClient(api_key="your-api-key")

async def generate_multiple():
    tasks = [
        client.generate_audio_async("Text 1", "Pravaha", "Hindi", "output1.wav"),
        client.generate_audio_async("Text 2", "Shruti", "English", "output2.wav"),
        client.generate_audio_async("Text 3", "Aabha", "Telugu", "output3.wav"),
    ]
    results = await asyncio.gather(*tasks)
    return results

audio_files = asyncio.run(generate_multiple())
```

### WebSocket Streaming (ASR)

Real-time transcription with WebSocket - **2x faster than HTTP** for batch processing:

```python
from fonadalabs import ASRWebSocketClient, ASRSDKError

# Initialize WebSocket client (API key from env or parameter)
ws_client = ASRWebSocketClient(api_key="your-api-key")

try:
    # Transcribe using WebSocket (persistent connection)
    result = ws_client.transcribe(
        audio_path="audio.wav",
        language_id="hi"  # Hindi
    )
    
    # Result is a dict
    print(f"✓ Transcription: {result.get('text')}")
    print(f"✓ Status: {result.get('status')}")
    
except ASRSDKError as e:
    print(f"❌ WebSocket transcription failed: {e}")

# Benefits:
# - Authenticate once, transcribe multiple files
# - 2x faster latency (190ms vs 382ms)
# - 95% less auth overhead
```

### Multiple Languages (ASR)

ASR supports **50+ languages** including all major Indian languages:

```python
from fonadalabs import ASRClient, is_supported_language, SUPPORTED_LANGUAGES

client = ASRClient(api_key="your-api-key")

# Check if a language is supported
if is_supported_language("hi"):
    print("✓ Hindi is supported!")

# Test multiple languages
languages = ["hi", "en", "ta", "te", "bn", "gu", "mr", "kn", "ml", "pa"]

for lang in languages:
    if is_supported_language(lang):
        result = client.transcribe_file("audio.wav", language_id=lang)
        print(f"{lang}: {result.text}")

# View all supported languages
print(f"Total languages: {len(SUPPORTED_LANGUAGES)}")
```

**Popular Indian Languages:**
- Hindi (`hi`), English (`en`), Tamil (`ta`), Telugu (`te`)
- Bengali (`bn`), Gujarati (`gu`), Marathi (`mr`), Kannada (`kn`)
- Malayalam (`ml`), Punjabi (`pa`), Odia (`or`), Assamese (`as`)
- Urdu (`ur`), Nepali (`ne`), Sanskrit (`sa`), and more!

### Batch Processing (ASR)

Process multiple audio files concurrently:

```python
from fonadalabs import ASRClient

client = ASRClient(api_key="your-api-key")

# List of audio files to transcribe
file_paths = ["audio1.wav", "audio2.wav", "audio3.wav"]

# Batch transcribe with custom concurrency
results = client.batch_transcribe(
    file_paths=file_paths,
    language_id="en",
    concurrency=3
)

# Process successful transcriptions
for result in results.successful:
    print(f"✓ {result.file_path}: {result.text}")

# Handle failed transcriptions
for failed in results.failed:
    print(f"✗ {failed.file_path}: {failed.error}")
```

## Error Handling

The SDK provides specific exception types for different error scenarios:

### TTS Exceptions

```python
from fonadalabs import (
    TTSError,                 # Base exception
    CreditsExhaustedError,    # Credits exhausted (402/429)
    RateLimitError            # Rate limit exceeded (429)
)

# Exception usage example
try:
    audio = client.generate_audio("Text", "Pravaha")
except CreditsExhaustedError as e:
    print(f"Credits exhausted. Balance: {e.current_balance}, Cost: {e.estimated_cost}")
except RateLimitError as e:
    print(f"Rate limited. Limit: {e.rate_limit}, Retry after: {e.retry_after_seconds}s")
except TTSError as e:
    print(f"TTS Error: {e}")
```

### ASR Exceptions

```python
from fonadalabs import (
    ASRSDKError,                 # Base exception
    AuthenticationError,         # Invalid API key (401/403)
    ValidationError,             # Invalid parameters
    HTTPRequestError,            # HTTP request failed
    ServerError,                 # Server error (500+)
    ASRRateLimitError,           # Rate limit exceeded (429)
    ASRTimeoutError,             # Request timeout
    ASRCreditsExhaustedError     # Credits exhausted (402/429)
)

# Exception usage example
try:
    result = asr_client.transcribe_file("audio.wav", language_id="hi")
except ASRCreditsExhaustedError as e:
    print(f"Credits exhausted. Usage: {e.current_usage}, Limit: {e.credit_limit}")
except ASRRateLimitError as e:
    print(f"Rate limited. Limit: {e.rate_limit}, Reset at: {e.reset_at}")
except AuthenticationError as e:
    print(f"Auth failed: {e}")
except ValidationError as e:
    print(f"Invalid parameters: {e}")
except ASRSDKError as e:
    print(f"ASR Error: {e}")
```

### Denoise Exceptions

```python
from fonadalabs import (
    DenoiseError,                    # Base exception
    DenoiseCreditsExhaustedError,    # Credits exhausted
    DenoiseRateLimitError            # Rate limit exceeded
)
```

## Security Features

### 🔒 Base URL Lockdown

All SDK clients use **hardcoded, secure base URLs** that cannot be overridden. This prevents:
- URL injection attacks
- Data exfiltration attempts
- Man-in-the-middle attacks

```python
# ✅ SECURE: Base URLs are locked
client = TTSClient(api_key="your-key")

# ❌ PREVENTED: Cannot override base URL
# client = TTSClient(api_key="key", base_url="http://malicious.com")  # Not allowed
```

Base URLs can only be configured via environment variables by authorized administrators:
```bash
export FONADALABS_API_URL=https://your-secure-endpoint.com
```

### 🔐 API Key Validation

All API requests are validated:
- API keys are required for all endpoints
- Invalid keys return `401 Unauthorized`
- Keys are transmitted securely via HTTPS
- Never logged or exposed in error messages

## Documentation

- **TTS Documentation:** See [TEXT_TO_SPEECH_QUICKSTART.md](tts_sdk/TEXT_TO_SPEECH_QUICKSTART.md)
- **ASR Documentation:** See [ASR_AUTHENTICATION.md](ASR_AUTHENTICATION.md)
- **Denoise Documentation:** See [denoise_sdk/README.md](denoise_sdk/README.md)
- **Security Audit:** See [SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md)

## Examples

### TTS Examples
Located in `tts_sdk/examples/`:
- `basic_usage.py` - Simple HTTP generation
- `websocket_usage.py` - WebSocket with progress tracking
- `async_usage.py` - Concurrent requests
- `streaming_usage.py` - Audio chunk streaming
- `auth_usage.py` - Authentication examples

### ASR Examples
Located in `test/`:
- `asr_test.py` - Comprehensive test suite with all features
- Tests include: HTTP POST, WebSocket, multiple languages, error handling

**Run ASR Tests:**
```bash
# Set API key
export FONADALABS_API_KEY="your_api_key_here"

# Run all tests
cd test
python asr_test.py --audio test_audio.wav

# Run specific test
python asr_test.py --test post         # HTTP POST transcription
python asr_test.py --test ws           # WebSocket transcription
python asr_test.py --test languages    # Test multiple languages
python asr_test.py --test errors       # Error handling
```

### Denoise Examples
Located in `denoise_sdk/`:
- `sdk_test.py` - Quick start examples for HTTP and WebSocket denoising

## Package Structure

```
fonadalabs/
├── __init__.py                    # Unified package exports
├── tts/                           # TTS submodule
│   ├── __init__.py
│   └── client.py                 # TTSClient
├── asr/                           # ASR submodule
│   ├── __init__.py
│   ├── client.py                 # ASRClient
│   ├── ws_client.py              # ASRWebSocketClient
│   ├── config.py                 # Configuration
│   ├── exceptions.py             # ASR exceptions
│   ├── languages.py              # Language utilities
│   ├── utils.py                  # Utility functions
│   └── models/                   # Data models
│       └── types.py
└── denoise/                       # Denoise submodule
    ├── __init__.py
    ├── http_client.py            # DenoiseHttpClient
    ├── streaming_client.py       # DenoiseStreamingClient
    └── exceptions.py             # Denoise exceptions
```

## Importing

### All Three SDKs
```python
from fonadalabs import (
    TTSClient,
    ASRClient,
    DenoiseHttpClient,
    DenoiseStreamingClient
)

tts = TTSClient(api_key="your-key")
asr = ASRClient(api_key="your-key")
denoise = DenoiseHttpClient(api_key="your-key")
```

### TTS Only
```python
from fonadalabs import TTSClient, TTSError, CreditsExhaustedError, RateLimitError
# or explicitly from submodule
from fonadalabs.tts import TTSClient, TTSError
```

### ASR Only
```python
from fonadalabs import ASRClient, ASRWebSocketClient
# or explicitly from submodule
from fonadalabs.asr import ASRClient, ASRWebSocketClient
```

### Denoise Only
```python
from fonadalabs import DenoiseHttpClient, DenoiseStreamingClient
# or explicitly from submodule
from fonadalabs.denoise import DenoiseHttpClient, DenoiseStreamingClient
```

## Requirements

### Dependencies (Installed Automatically)

**Python:** >= 3.9 (3.9, 3.10, 3.11, 3.12 supported)

**Core Libraries:**
- **httpx** >= 0.24, < 1.0 (HTTP client)
- **websockets** >= 11, < 13 (WebSocket support)
- **loguru** >= 0.7, < 1.0 (Logging)
- **requests** >= 2.28, < 3.0 (HTTP requests)

**Audio Processing (for all services):**
- **numpy** >= 1.24.0, < 2.0 (Audio processing)
- **soundfile** >= 0.12, < 0.14 (Audio I/O)
- **librosa** >= 0.10, < 1.0 (Audio analysis - denoise)
- **websocket-client** >= 1.5, < 2.0 (WebSocket streaming)

**Development (optional - `pip install fonadalabs[dev]`):**
- pytest >= 7.0, < 8.0
- black >= 23.0, < 24.0
- isort >= 5.0, < 6.0
- python-dotenv >= 1.0, < 2.0
- nest-asyncio >= 1.5, < 2.0
- build >= 0.10.0
- twine >= 4.0.0

## Contributing

We welcome contributions! Please see our contributing guidelines and feel free to submit pull requests.

## License

MIT License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2025 FonadaLabs

## Support

- 📧 **Email:** support@fonadalabs.com
- 🐛 **Issues:** [GitHub Issues](https://github.com/fonadalabs/fonadalabs-sdk/issues)
- 📖 **Documentation:** 
  - [TTS Quickstart](tts_sdk/TEXT_TO_SPEECH_QUICKSTART.md)
  - [ASR Authentication](ASR_AUTHENTICATION.md)
  - [Denoise SDK](denoise_sdk/README.md)
- 🌐 **Website:** https://fonadalabs.com
- 💬 **Community:** [Discord](https://discord.gg/fonadalabs) (if available)

## Version

**Current version:** 2.0.0 (Unified SDK)

### Version History
- **v2.0.0** (2025-12-05): Multi-language TTS support
  - Added `language` parameter to all TTS methods
  - Supports 4 languages: Hindi, English, Tamil, Telugu
  - Updated SDK documentation
- **v1.0.0** (2025-10-16): Unified package with TTS, ASR, and Denoise
  - Base URL security lockdown
  - Required API key authentication for all endpoints
  - Comprehensive error handling with specific exception types
  - WebSocket streaming support for all services
  - Async/await support
  - Batch processing capabilities

---

**Made with ❤️ by FonadaLabs**


