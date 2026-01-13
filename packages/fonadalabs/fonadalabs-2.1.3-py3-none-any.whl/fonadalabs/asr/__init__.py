"""
FonadaLabs ASR (Automatic Speech Recognition) Module
"""

from .client import ASRClient
from .ws_client import ASRWebSocketClient
from .config import get_config, SDKConfig
from .languages import SUPPORTED_LANGUAGES, normalize_language, is_supported_language
from .exceptions import (
    ASRSDKError,
    ConfigurationError,
    ValidationError,
    AuthenticationError,
    HTTPRequestError,
    ServerError,
    RateLimitError,
    TimeoutError,
    CreditsExhaustedError,
)
from .models import TranscribeResult, BatchResult, FailedTranscription

__all__ = [
    "ASRClient",
    "ASRWebSocketClient",
    "get_config",
    "SDKConfig",
    "SUPPORTED_LANGUAGES",
    "normalize_language",
    "is_supported_language",
    "ASRSDKError",
    "ConfigurationError",
    "ValidationError",
    "AuthenticationError",
    "HTTPRequestError",
    "ServerError",
    "RateLimitError",
    "TimeoutError",
    "CreditsExhaustedError",
    "TranscribeResult",
    "BatchResult",
    "FailedTranscription",
]
