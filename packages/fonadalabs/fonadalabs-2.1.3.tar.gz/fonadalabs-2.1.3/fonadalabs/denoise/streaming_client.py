#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DenoiseStreamingClient - Real-time Streaming Audio Denoising Client

HTTP and WebSocket client for streaming chunk-based denoising.
Part of FonadaLabs unified SDK.
"""

import base64
import json
import math
from pathlib import Path
from typing import Optional, Union, Dict, Any, Callable

import numpy as np
import requests

from .exceptions import DenoiseError, CreditsExhaustedError, RateLimitError

# Try to import WebSocket client (websocket-client package)
create_connection = None
try:
    # Try websocket-client package first (correct package)
    from websocket import create_connection
except (ImportError, AttributeError):
    try:
        # Try alternative import path
        import websocket
        if hasattr(websocket, 'create_connection'):
            create_connection = websocket.create_connection
    except ImportError:
        pass


class DenoiseStreamingClient:
    """
    Streaming audio denoising client.
    
    Processes audio in fixed-size chunks (0.64s at 16kHz = 10,240 samples)
    using DeepFilterNet with constant-time batching for low latency.
    
    Example:
        ```python
        from fonadalabs import DenoiseStreamingClient
        
        # Initialize
        client = DenoiseStreamingClient(api_key="your-api-key")
        
        # Denoise single chunk
        chunk = np.random.randn(10240).astype(np.float32)
        denoised = client.denoise_chunk(chunk)
        
        # Denoise full file via HTTP
        client.denoise_file("noisy.wav", "clean.wav")
        
        # Denoise via WebSocket with callback
        def on_chunk(chunk):
            print(f"Got chunk: {len(chunk)} samples")
        
        client.denoise_file_ws("noisy.wav", "clean.wav", callback=on_chunk)
        ```
    """
    
    # Constants from the API
    SAMPLE_RATE = 16000
    CORE_SAMPLES = 10240  # 0.64 seconds at 16kHz
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 60,
        verify_ssl: bool = True
    ):
        """
        Initialize the DenoiseStreamingClient.
        
        Args:
            api_key: API key for authentication (required)
            timeout: Request timeout in seconds (default: 60)
            verify_ssl: Whether to verify SSL certificates (default: True)
            
        Raises:
            ValueError: If no API key is provided
            
        Note:
            The base URL is configured internally via FONADALABS_DENOISE_URL
            environment variable (default: http://localhost:9559).
            Users cannot override it for security reasons.
        """
        import os
        
        # Base URL is configured internally via environment variable
        # Users cannot override it for security reasons
        self.base_url = os.getenv("FONADALABS_DENOISE_URL", "https://api.fonada.ai").rstrip("/")
        self.api_key = api_key or os.getenv("FONADALABS_API_KEY")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        # Validate that API key is provided (required for authentication)
        if not self.api_key:
            raise ValueError(
                "API key is required. Please provide it via:\n"
                "1. DenoiseStreamingClient(api_key='your-api-key')\n"
                "2. Environment variable: export FONADALABS_API_KEY='your-api-key'\n"
                "3. .env file with FONADALABS_API_KEY='your-api-key'"
            )
        
        self.session = requests.Session()
        
        # Add API key to headers (required for all requests)
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}"
        })
    
    def _get_ws_url(self) -> str:
        """Convert HTTP URL to WebSocket URL."""
        return self.base_url.replace("http://", "ws://").replace("https://", "wss://")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check API health status.
        
        Returns:
            Dict containing health status information
            
        Raises:
            requests.RequestException: If the request fails
        """
        response = self.session.get(
            f"{self.base_url}/health",
            timeout=self.timeout,
            verify=self.verify_ssl
        )
        self._check_credits_exhausted(response)
        response.raise_for_status()
        return response.json()
    
    def get_batch_status(self) -> Dict[str, Any]:
        """
        Get current server and batch processing status.
        
        Returns:
            Dict containing:
                - server: Server name
                - version: API version
                - model: Model being used
                - engine: Engine configuration
                - concurrency: Concurrency info
                - ola_sessions: Number of OLA sessions
                - endpoints: Available endpoints
                
        Raises:
            requests.RequestException: If the request fails
        """
        response = self.session.get(
            f"{self.base_url}/status",
            timeout=self.timeout,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()
    
    def denoise_chunk(
        self,
        audio_chunk: np.ndarray,
        codec: str = "pcm_f32le",
        session_id: Optional[str] = None,
        is_first_chunk: bool = False
    ) -> np.ndarray:
        """
        Denoise a single audio chunk via HTTP.
        
        The chunk will be automatically padded or trimmed to CORE_SAMPLES (10,240).
        
        Args:
            audio_chunk: Audio data as numpy array (mono, float32)
            codec: Audio codec format (default: pcm_f32le)
            session_id: Optional session ID for OLA state tracking (smooth transitions)
            is_first_chunk: Whether this is the first chunk of a session (for fade-in)
            
        Returns:
            Denoised audio chunk as numpy array
            
        Raises:
            requests.RequestException: If the request fails
        """
        # Ensure correct format
        audio_chunk = audio_chunk.astype(np.float32)
        
        # Pad or trim to CORE_SAMPLES
        if len(audio_chunk) < self.CORE_SAMPLES:
            audio_chunk = np.pad(
                audio_chunk,
                (0, self.CORE_SAMPLES - len(audio_chunk)),
                mode='constant'
            )
        elif len(audio_chunk) > self.CORE_SAMPLES:
            audio_chunk = audio_chunk[:self.CORE_SAMPLES]
        
        # Encode to base64
        chunk_b64 = base64.b64encode(audio_chunk.tobytes()).decode('utf-8')
        
        payload = {
            "chunk_data": chunk_b64,
            "codec": codec,
            "is_first_chunk": is_first_chunk
        }
        
        # Add session_id if provided (for OLA smooth transitions)
        if session_id:
            payload["session_id"] = session_id
        
        response = self.session.post(
            f"{self.base_url}/denoise_chunk",
            json=payload,
            timeout=self.timeout,
            verify=self.verify_ssl
        )
        
        self._check_credits_exhausted(response)
        response.raise_for_status()
        result = response.json()
        
        if not result.get("success"):
            raise RuntimeError("Denoising failed")
        
        # Decode result
        denoised_bytes = base64.b64decode(result["denoised_chunk"])
        denoised_chunk = np.frombuffer(denoised_bytes, dtype=np.float32)
        
        return denoised_chunk
    
    def denoise_file(
        self,
        file_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        use_ola: bool = True
    ) -> np.ndarray:
        """
        Denoise a complete audio file via HTTP by chunking.
        
        The file will be automatically split into CORE_SAMPLES chunks,
        each chunk denoised separately, and results concatenated.
        
        Args:
            file_path: Path to input audio file
            output_path: Optional path to save denoised audio
            progress_callback: Optional callback(current_chunk, total_chunks)
            use_ola: Use OLA (Overlap-Add) for smooth transitions (default: True)
            
        Returns:
            Denoised audio as numpy array
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            requests.RequestException: If the request fails
        """
        try:
            import soundfile as sf
            import librosa
        except ImportError:
            raise ImportError("soundfile and librosa are required for file processing")
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Load audio
        audio, sr = sf.read(file_path)
        
        # Convert to mono if stereo
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        
        # Resample to 16kHz if needed
        if sr != self.SAMPLE_RATE:
            audio = librosa.resample(
                audio.astype(np.float32),
                orig_sr=sr,
                target_sr=self.SAMPLE_RATE
            )
        
        audio = audio.astype(np.float32)
        
        # Split into chunks
        num_chunks = math.ceil(len(audio) / self.CORE_SAMPLES)
        denoised_chunks = []
        
        # Generate session_id for OLA state tracking
        import uuid
        session_id = str(uuid.uuid4()) if use_ola else None
        
        for i in range(num_chunks):
            start = i * self.CORE_SAMPLES
            end = min(start + self.CORE_SAMPLES, len(audio))
            chunk = audio[start:end]
            
            # Denoise chunk with OLA support
            denoised_chunk = self.denoise_chunk(
                chunk,
                session_id=session_id,
                is_first_chunk=(i == 0)
            )
            denoised_chunks.append(denoised_chunk[:len(chunk)])  # Remove padding
            
            if progress_callback:
                progress_callback(i + 1, num_chunks)
        
        # Concatenate all chunks
        denoised_audio = np.concatenate(denoised_chunks)
        
        # Save if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            sf.write(output_path, denoised_audio, self.SAMPLE_RATE)
        
        return denoised_audio
    
    def denoise_file_ws(
        self,
        file_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        callback: Optional[Callable[[np.ndarray], None]] = None,
        codec: str = "pcm_f32le"
    ) -> np.ndarray:
        """
        Denoise a complete audio file via WebSocket streaming.
        
        Protocol:
        1. Connect to WebSocket
        2. Receive {"status": "connected"} from server
        3. Send {"api_key": "...", "codec": "..."} for authentication
        4. Receive {"status": "authenticated"} from server
        5. Send binary audio chunks
        6. Receive binary denoised chunks
        7. Send {"action": "close"} to finish
        
        Args:
            file_path: Path to input audio file
            output_path: Optional path to save denoised audio
            callback: Optional callback(denoised_chunk) called for each chunk
            codec: Audio codec (default: pcm_f32le)
            
        Returns:
            Complete denoised audio as numpy array
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            RuntimeError: If WebSocket connection fails
        """
        try:
            import soundfile as sf
            import librosa
        except ImportError:
            raise ImportError("soundfile and librosa are required for file processing")
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Load audio
        audio, sr = sf.read(file_path)
        
        # Convert to mono if stereo
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        
        # Resample to 16kHz if needed
        if sr != self.SAMPLE_RATE:
            audio = librosa.resample(
                audio.astype(np.float32),
                orig_sr=sr,
                target_sr=self.SAMPLE_RATE
            )
        
        audio = audio.astype(np.float32)
        
        # Split into chunks
        num_chunks = math.ceil(len(audio) / self.CORE_SAMPLES)
        chunks = []
        for i in range(num_chunks):
            start = i * self.CORE_SAMPLES
            end = min(start + self.CORE_SAMPLES, len(audio))
            chunk = audio[start:end]
            chunks.append(chunk)
        
        # Connect to WebSocket
        ws_url = f"{self._get_ws_url()}/ws/denoise_chunk"
        
        if create_connection is None:
            raise ImportError(
                "websocket-client is required for WebSocket streaming. "
                "Install with: pip install websocket-client"
            )
        
        ws = create_connection(ws_url)
        
        denoised_chunks = []
        
        try:
            # Step 1: Receive connection confirmation
            msg = ws.recv()
            connect_msg = json.loads(msg)
            if connect_msg.get("status") != "connected":
                raise RuntimeError(f"WebSocket connection failed: {connect_msg}")
            
            # Step 2: Send authentication
            auth_payload = {
                "api_key": self.api_key,
                "codec": codec
            }
            ws.send(json.dumps(auth_payload))
            
            # Step 3: Receive authentication confirmation
            msg = ws.recv()
            auth_msg = json.loads(msg)
            if auth_msg.get("status") != "authenticated":
                raise RuntimeError(f"WebSocket authentication failed: {auth_msg}")
            
            # Step 4: Send audio chunks and receive denoised chunks
            for i, chunk in enumerate(chunks):
                # Pad chunk if needed
                if len(chunk) < self.CORE_SAMPLES:
                    padded_chunk = np.pad(
                        chunk,
                        (0, self.CORE_SAMPLES - len(chunk)),
                        mode='constant'
                    ).astype(np.float32)
                else:
                    padded_chunk = chunk.astype(np.float32)
                
                # Send binary chunk
                ws.send_binary(padded_chunk.tobytes())
                
                # Receive denoised binary chunk
                result = ws.recv()
                
                # Check if it's a JSON message (error or status)
                if isinstance(result, str):
                    msg = json.loads(result)
                    if msg.get("status") == "error":
                        raise RuntimeError(f"Chunk {i} denoising failed: {msg.get('error')}")
                    continue
                
                # Binary response - decode as numpy array
                denoised_chunk = np.frombuffer(result, dtype=np.float32)
                
                # Remove padding
                denoised_chunk = denoised_chunk[:len(chunk)]
                denoised_chunks.append(denoised_chunk)
                
                if callback:
                    callback(denoised_chunk)
            
            # Step 5: Send close signal (API expects "close", not "end")
            ws.send(json.dumps({"action": "close"}))
        
        finally:
            ws.close()
        
        # Concatenate all chunks
        if not denoised_chunks:
            raise RuntimeError("No denoised chunks received")
        
        denoised_audio = np.concatenate(denoised_chunks)
        
        # Save if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            sf.write(output_path, denoised_audio, self.SAMPLE_RATE)
        
        return denoised_audio
    
    def _check_credits_exhausted(self, response: requests.Response) -> None:
        """Check if response indicates credits exhausted or rate limit and raise appropriate error"""
        if response.status_code in (402, 429):
            try:
                error_data = response.json()
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
            except (ValueError, KeyError, json.JSONDecodeError, CreditsExhaustedError, RateLimitError):
                # Re-raise our custom exceptions
                if isinstance(error_data, (CreditsExhaustedError, RateLimitError)):
                    raise
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


__all__ = ["DenoiseStreamingClient", "DenoiseError", "CreditsExhaustedError", "RateLimitError"]

