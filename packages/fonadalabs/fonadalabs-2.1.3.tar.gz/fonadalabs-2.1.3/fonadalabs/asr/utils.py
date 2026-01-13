# fonada_asr/utils.py
import os
import io
import time
import base64
import mimetypes
from pathlib import Path
from typing import Any, Dict, Tuple, Optional, Callable
from .exceptions import TimeoutError

# ----------------------------------------------------------------------
# File & Audio Helpers
# ----------------------------------------------------------------------

def encode_base64(audio_path: str) -> str:
    """Read an audio file and return base64 string."""
    with open(audio_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def list_audio_files(folder: str, exts=(".wav", ".mp3", ".flac")) -> list[str]:
    """Recursively list audio files under a folder."""
    folder = Path(folder)
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")
    return [str(p) for p in folder.rglob("*") if p.suffix.lower() in exts]

# ----------------------------------------------------------------------
# HTTP Upload & URL Helpers
# ----------------------------------------------------------------------

def ensure_base_url(base_url: str) -> str:
    """Ensure no trailing slash in base URL."""
    return base_url.rstrip("/")

def guess_mimetype(filename: str) -> str:
    """Guess MIME type of a file based on extension."""
    mime, _ = mimetypes.guess_type(filename)
    return mime or "application/octet-stream"

def make_file_tuple(field_name: str, filename: str, content: bytes) -> Tuple[str, Tuple[str, bytes, str]]:
    """
    Create a tuple suitable for multipart/form-data upload.
    Example: files = [make_file_tuple("file", "audio.wav", audio_bytes)]
    """
    return (field_name, (os.path.basename(filename), content, guess_mimetype(filename)))

def safe_join_url(base: str, path: str) -> str:
    """Safely join base URL and endpoint path."""
    base = ensure_base_url(base)
    path = path if path.startswith("/") else f"/{path}"
    return f"{base}{path}"

# ----------------------------------------------------------------------
# Timing Utilities
# ----------------------------------------------------------------------

class Timer:
    """Context manager for measuring execution time in ms."""
    def __enter__(self):
        self.start = time.time()
        return self
    def __exit__(self, *args):
        self.end = time.time()
        self.elapsed_ms = round((self.end - self.start) * 1000, 2)

def elapsed_ms(start: float) -> float:
    """Return elapsed time in milliseconds."""
    return (time.time() - start) * 1000.0

# ----------------------------------------------------------------------
# Timeout Wrapper
# ----------------------------------------------------------------------

def with_timeout(func: Callable, timeout: float, *args, **kwargs):
    """
    Synchronous timeout guard (fallback; httpx has built-in async timeouts).
    Raises TimeoutError if runtime exceeds the specified timeout.
    """
    start = time.time()
    result = func(*args, **kwargs)
    if (time.time() - start) > timeout:
        raise TimeoutError(f"Operation exceeded timeout {timeout}s")
    return result
