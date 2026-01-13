# fonada_asr/client.py
from __future__ import annotations

import asyncio
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable, List, Optional, Dict, Any
from urllib.parse import urlparse

import httpx
import sys
from loguru import logger

from .config import get_config
from .exceptions import (
    ConfigurationError,
    ValidationError,
    AuthenticationError,
    HTTPRequestError,
    ServerError,
    RateLimitError,
    TimeoutError,
    CreditsExhaustedError,
)
from .languages import normalize_language, is_supported_language
from .models import TranscribeResult, BatchResult, FailedTranscription
from .utils import make_file_tuple, safe_join_url, list_audio_files, Timer
from .ws_client import ASRWebSocketClient

class ASRClient:
    """
    FonadaLabs ASR SDK client.

    -  Works with both sync and async usage
    -  Handles batch & folder transcriptions
    -  Validates languages automatically
    -  Requires API key authentication for all endpoints
    -  Includes retry, timeout, and rate-limit handling
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
        retry_backoff: Optional[float] = None,
        max_concurrency: Optional[int] = None,
        ws_endpoint: Optional[str] = None,
        ws_url: Optional[str] = None,
        token: Optional[str] = None,
    ):
        cfg = get_config()
        # Base URL is configured internally via environment variable or config
        # Users cannot override it for security reasons
        self.base_url = cfg.base_url
        self.api_key = api_key or cfg.api_key or os.getenv("FONADALABS_API_KEY")
        self.endpoint = endpoint or cfg.http_endpoint
        self.timeout = timeout or cfg.timeout
        self.retries = retries or cfg.retries
        self.retry_backoff = retry_backoff or cfg.retry_backoff
        self.max_concurrency = max_concurrency or cfg.max_concurrency
        self.ws_endpoint = ws_endpoint or cfg.ws_endpoint
        self.token = token or cfg.token or os.getenv("FONADALABS_API_KEY")

        if not self.base_url:
            raise ConfigurationError("base_url cannot be empty")
        
        # Validate that API key is provided (required for authentication)
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Please provide it via:\n"
                "1. ASRClient(api_key='your-api-key')\n"
                "2. Environment variable: export FONADALABS_API_KEY='your-api-key'\n"
                "3. .env file with FONADALABS_API_KEY='your-api-key'"
            )

        self.url = safe_join_url(self.base_url, self.endpoint)
        self.ws_url = ws_url or self._compose_ws_url(self.base_url, self.ws_endpoint)
        self._client = httpx.Client(timeout=self.timeout, headers=self._default_headers())
        self._aclient = httpx.AsyncClient(timeout=self.timeout, headers=self._default_headers())

    # ---------- Internal helpers ----------

    def _default_headers(self) -> Dict[str, str]:
        h = {"accept": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def _compose_ws_url(self, base_url: str, endpoint: str) -> str:
        parsed = urlparse(base_url)
        scheme = "wss"
        host = parsed.netloc or parsed.path
        path = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        return f"{scheme}://{host}{path}"

    def _build_ws_client(
        self,
        *,
        url: Optional[str] = None,
        token: Optional[str] = None,
        ) -> ASRWebSocketClient:
        if url is not None:
            target_url = url
        else:
            target_url = self.ws_url
        return ASRWebSocketClient(
            url=target_url,
            token=token or self.token,
        )

    def _validate_language(self, lang: str) -> str:
        norm = normalize_language(lang)
        if not is_supported_language(norm):
            raise ValidationError(f"Unsupported language '{lang}'. Supported codes only.")
        return norm

    def _read_file(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    def _backoff(self, attempt: int): import time; time.sleep(self.retry_backoff * attempt)
    async def _abackoff(self, attempt: int): await asyncio.sleep(self.retry_backoff * attempt)

    # ---------- Public synchronous methods ----------

    def transcribe_file(self, file_path: str, language_id: str = "hi") -> TranscribeResult:
        language_id = self._validate_language(language_id)
        data = self._read_file(file_path)
        files = [make_file_tuple("file", os.path.basename(file_path), data)]
        form = {"language_id": language_id}
        attempt = 0
        while True:
            attempt += 1
            try:
                with Timer() as t:
                    resp = self._client.post(self.url, files=files, data=form)
                result = self._handle_response(resp, language_id, file_path)
                result.latency_ms = t.elapsed_ms
                return result
            except httpx.ReadTimeout:
                if attempt <= self.retries:
                    self._backoff(attempt)
                    continue
                raise TimeoutError(f"Timed out after {self.retries} retries")
            except httpx.RequestError as e:
                raise HTTPRequestError(str(e)) from e

    def batch_transcribe(
        self,
        file_paths: Iterable[str],
        language_id: str = "hi",
        concurrency: Optional[int] = None,
    ) -> BatchResult:
        """
        Transcribe multiple files concurrently using a thread pool.
        """
        return self._transcribe_many(file_paths, language_id, concurrency)

    def transcribe_folder(self, folder: str, language_id: str = "hi") -> BatchResult:
        """Transcribe all audio files in a folder concurrently."""
        files = list_audio_files(folder)
        if not files:
            raise ValidationError(f"No audio files found in {folder}")
        logger.info(f"Found {len(files)} audio files in {folder}")
        return self._transcribe_many(files, language_id)

    def transcribe_files(self, paths: Iterable[str], language_id: str = "hi") -> BatchResult:
        return self._transcribe_many(paths, language_id)

    def stream_transcribe_file(
        self,
        file_path: str,
        language_id: str = "hi",
        *,
        ws_url: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Stream a single file over WebSocket using the same client instance.
        """
        lang = self._validate_language(language_id)
        ws_client = self._build_ws_client(url=ws_url, token=token)
        return ws_client.transcribe(file_path, lang)

    def _transcribe_many(
        self,
        paths: Iterable[str],
        language_id: str,
        concurrency: Optional[int] = None,
    ) -> BatchResult:
        normalized_lang = self._validate_language(language_id)
        file_list = list(paths)
        if not file_list:
            raise ValidationError("No audio files provided")

        if concurrency is not None and concurrency < 1:
            raise ValidationError("concurrency must be >= 1")

        configured_workers = concurrency or self.max_concurrency or 1
        max_workers = min(configured_workers, len(file_list))
        max_workers = max(max_workers, 1)
        successes: List[TranscribeResult] = []
        failures: List[FailedTranscription] = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_path = {
                executor.submit(self.transcribe_file, path, normalized_lang): path
                for path in file_list
            }
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    # Preserve the original path for downstream reporting
                    result.file_path = path
                    successes.append(result)
                except Exception as exc:
                    logger.warning(f"File {path} failed: {exc}")
                    failures.append(FailedTranscription(file_path=path, error=str(exc)))

        return BatchResult(results=successes, failed=failures)

    # ---------- Async methods (for high-throughput) ----------

    async def atranscribe_file(self, file_path: str, language_id: str = "hi") -> TranscribeResult:
        lang = self._validate_language(language_id)
        data = self._read_file(file_path)
        files = [("file", (os.path.basename(file_path), data, "application/octet-stream"))]
        form = {"language_id": lang}
        attempt = 0
        while True:
            attempt += 1
            try:
                start = asyncio.get_event_loop().time()
                resp = await self._aclient.post(self.url, files=files, data=form)
                res = self._handle_response(resp, lang, file_path)
                res.latency_ms = (asyncio.get_event_loop().time() - start) * 1000
                return res
            except httpx.ReadTimeout:
                if attempt <= self.retries:
                    await self._abackoff(attempt)
                    continue
                raise TimeoutError(f"Timed out after {self.retries} retries")
            except httpx.RequestError as e:
                raise HTTPRequestError(str(e)) from e

    async def abatch_transcribe(
        self,
        file_paths: Iterable[str],
        language_id: str = "hi",
        concurrency: Optional[int] = None,
    ) -> BatchResult:
        lang = self._validate_language(language_id)
        file_list = list(file_paths)
        if not file_list:
            raise ValidationError("No audio files provided")
        if concurrency is not None and concurrency < 1:
            raise ValidationError("concurrency must be >= 1")

        configured_limit = concurrency or self.max_concurrency or 1
        limit = min(configured_limit, len(file_list))
        limit = max(limit, 1)
        sem = asyncio.Semaphore(limit)
        results: List[TranscribeResult] = []
        failed: List[FailedTranscription] = []

        async def _worker(path: str):
            async with sem:
                try:
                    res = await self.atranscribe_file(path, language_id=lang)
                    res.file_path = path
                    results.append(res)
                except Exception as exc:
                    logger.warning(f"File {path} failed: {exc}")
                    failed.append(FailedTranscription(file_path=path, error=str(exc)))

        await asyncio.gather(*[asyncio.create_task(_worker(p)) for p in file_list])
        return BatchResult(results=results, failed=failed)

    async def astream_transcribe_file(
        self,
        file_path: str,
        language_id: str = "hi",
        *,
        ws_url: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Async streaming transcription helper tied to this client configuration.
        """
        lang = self._validate_language(language_id)
        ws_client = self._build_ws_client(url=ws_url, token=token)
        return await ws_client.transcribe_file(file_path, lang)

    # ---------- Response handling ----------

    def _handle_response(self, resp: httpx.Response, lang: str, source_path: str) -> TranscribeResult:
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError:
            self._raise_for_status(resp)
        data = resp.json() if resp.content else {}

        payload: Dict[str, Any] = data if isinstance(data, dict) else {}
        if isinstance(payload.get("result"), dict):
            payload = payload["result"]  # unwrap common {"status":"ok","result":{...}} responses

        text = ""
        for candidate in ("text", "transcript", "transcription"):
            value = payload.get(candidate)
            if isinstance(value, str):
                text = value
                break

        engine = payload.get("engine") or data.get("engine")
        language = payload.get("language_id") or payload.get("language") or lang
        request_id = payload.get("request_id") or data.get("request_id")

        return TranscribeResult(
            text=text,
            engine=engine,
            language_id=language,
            request_id=request_id,
            file_path=source_path,
            raw=data,
        )

    def _raise_for_status(self, resp: httpx.Response):
        code = resp.status_code
        
        # Check for credits exhausted or rate limit (402 Payment Required or 429)
        if code in (402, 429):
            try:
                error_data = resp.json()
                error_type = error_data.get("error")
                
                if error_type == "credits_exhausted":
                    raise CreditsExhaustedError(
                        error_data.get("message", "Credits exhausted"),
                        details=error_data.get("details", {})
                    )
                elif error_type == "rate_limit_exceeded":
                    raise RateLimitError(
                        error_data.get("message", "Rate limit exceeded"),
                        details=error_data.get("details", {})
                    )
            except (ValueError, KeyError, CreditsExhaustedError, RateLimitError):
                # Re-raise our custom exceptions
                if isinstance(sys.exc_info()[1], (CreditsExhaustedError, RateLimitError)):
                    raise
        
        if code in (401, 403):
            raise AuthenticationError(resp.text)
        if code == 429:
            raise RateLimitError("Rate limit exceeded", details={})
        if 400 <= code < 500:
            raise ValidationError(f"{code} {resp.text}")
        if code >= 500:
            raise ServerError(f"{code} {resp.text}")
        resp.raise_for_status()

    # ---------- Cleanup ----------

    def close(self):
        try:
            self._client.close()
        except Exception:
            pass

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(self._aclient.aclose())
            return

        if loop.is_running():
            loop.create_task(self._aclient.aclose())
        else:
            loop.run_until_complete(self._aclient.aclose())

    async def aclose(self):
        self._client.close()
        await self._aclient.aclose()

    def __enter__(self): return self
    def __exit__(self, *a): self.close()
