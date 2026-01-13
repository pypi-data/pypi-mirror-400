"""
FonadaLabs SDK
Unified Python SDK for FonadaLabs APIs: TTS, ASR, and Denoise.

Quick Start:
    # Text-to-Speech
    from fonadalabs import TTSClient
    
    client = TTSClient(api_key="your-api-key")
    audio = client.generate_audio("Hello world", "Pravaha")
    
    # WebSocket streaming
    audio = client.generate_audio_ws("Long text here", "Shruti")
    
    # With callbacks
    def on_chunk(num, data):
        print(f"Chunk {num}: {len(data)} bytes")
    
    audio = client.generate_audio_ws(
        "Text here", 
        "Pravaha",
        on_chunk=on_chunk
    )

Features:
    - Multiple Indian voices (Pravaha, Shruti, Aabha, Svara, Vaanee)
    - HTTP POST and WebSocket streaming
    - Redis-cached authentication (100x faster)
    - Comprehensive error handling
    - Context manager support
"""

# TTS exports
from .tts.client import (
    TTSClient,
    TTSError,
    CreditsExhaustedError,  # Global exception for all services
    RateLimitError           # Global exception for all services
)

# Service-specific aliases (for clarity/backwards compatibility)
TTSCreditsExhaustedError = CreditsExhaustedError
TTSRateLimitError = RateLimitError

# ASR exports
from .asr.client import ASRClient
from .asr.ws_client import ASRWebSocketClient
from .asr.exceptions import (
    ASRSDKError,
    ConfigurationError,
    ValidationError,
    AuthenticationError,
    HTTPRequestError,
    ServerError,
    TimeoutError,
    CreditsExhaustedError as ASRCreditsExhaustedError,  # Alias to global
    RateLimitError as ASRRateLimitError,                # Alias to global
)
from .asr.languages import SUPPORTED_LANGUAGES, normalize_language, is_supported_language
from .asr.models.types import TranscribeResult, BatchResult, FailedTranscription

# Denoise exports (if available)
try:
    from .denoise.http_client import DenoiseHttpClient
    from .denoise.streaming_client import DenoiseStreamingClient
    from .denoise.exceptions import (
        DenoiseError,
        CreditsExhaustedError as DenoiseCreditsExhaustedError,  # Alias to global
        RateLimitError as DenoiseRateLimitError,                # Alias to global
    )
    _has_denoise = True
except ImportError:
    _has_denoise = False

# Version info
__version__ = "2.1.2"
__author__ = "FonadaLabs"
__license__ = "Proprietary"

# Public API
__all__ = [
    # TTS Client & Exceptions
    "TTSClient",
    "TTSError",
    
    # Global Exceptions (work for all services: TTS, ASR, Denoise)
    "CreditsExhaustedError",
    "RateLimitError",
    
    # Service-specific exception aliases (optional, for clarity)
    "TTSCreditsExhaustedError",
    "TTSRateLimitError",
    "ASRCreditsExhaustedError",
    "ASRRateLimitError",
    
    # ASR Clients
    "ASRClient",
    "ASRWebSocketClient",
    
    # ASR Exceptions
    "ASRSDKError",
    "ConfigurationError",
    "ValidationError",
    "AuthenticationError",
    "HTTPRequestError",
    "ServerError",
    "TimeoutError",
    
    # ASR Language utilities
    "SUPPORTED_LANGUAGES",
    "normalize_language",
    "is_supported_language",
    
    # ASR Models
    "TranscribeResult",
    "BatchResult",
    "FailedTranscription",
]

# Add denoise exports if available
if _has_denoise:
    __all__.extend([
        "DenoiseHttpClient",
        "DenoiseStreamingClient",
        "DenoiseError",
        "DenoiseCreditsExhaustedError",
        "DenoiseRateLimitError",
    ])


