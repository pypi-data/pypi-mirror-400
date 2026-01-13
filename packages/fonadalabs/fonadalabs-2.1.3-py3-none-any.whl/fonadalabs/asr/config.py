# fonada_asr/config.py
import os
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

@dataclass
class SDKConfig:
    # --- Core URLs ---
    base_url: str = os.getenv("FONADA_ASR_BASE_URL", "https://api.fonada.ai")
    http_endpoint: str = os.getenv("FONADA_ASR_HTTP_ENDPOINT", "/v1/asr/transcribe")
    ws_endpoint: str = os.getenv("FONADA_ASR_WS_ENDPOINT", "/v1/asr/stream")

    # --- Authentication ---
    api_key: Optional[str] = os.getenv("FONADA_ASR_API_KEY") or None
    token: Optional[str] = os.getenv("FONADA_ASR_TOKEN") or None

    # --- Behavior & limits ---
    language: str = os.getenv("FONADA_ASR_LANG", "hi")
    timeout: float = float(os.getenv("FONADA_ASR_TIMEOUT", "60"))
    retries: int = int(os.getenv("FONADA_ASR_RETRIES", "2"))
    retry_backoff: float = float(os.getenv("FONADA_ASR_BACKOFF", "0.5"))
    max_concurrency: int = int(os.getenv("FONADA_ASR_MAX_CONCURRENCY", "40"))

    # --- Derived fields (computed automatically) ---
    @property
    def api_url(self) -> str:
        """Full HTTP endpoint."""
        return f"{self.base_url.rstrip('/')}{self.http_endpoint}"

    @property
    def ws_url(self) -> str:
        """Construct secure or insecure WebSocket URL automatically."""
        parsed = urlparse(self.base_url)
        scheme = "wss" if (parsed.scheme == "https" or self.use_https) else "ws"
        host = parsed.netloc or parsed.path
        return f"{scheme}://{host}{self.ws_endpoint}"

def get_config() -> SDKConfig:
    """Return a fully constructed SDK configuration."""
    cfg = SDKConfig()
    return cfg
