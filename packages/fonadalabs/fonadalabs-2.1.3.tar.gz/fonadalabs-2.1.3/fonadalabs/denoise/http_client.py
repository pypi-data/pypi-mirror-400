#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DenoiseHttpClient - Full Audio Denoising Client

HTTP client for full audio denoising using DeepFilterNet + CMGAN models.
Part of FonadaLabs unified SDK.
"""

import base64
import io
import json
from pathlib import Path
from typing import Optional, Union, Dict, Any

import numpy as np
import requests

from .exceptions import DenoiseError, CreditsExhaustedError, RateLimitError


class DenoiseHttpClient:
    """
    HTTP client for full audio denoising.
    
    Connects to the unified API and processes complete audio files
    using DeepFilterNet and CMGAN models for high-quality denoising.
    
    Example:
        ```python
        from fonadalabs import DenoiseHttpClient
        
        # Initialize
        client = DenoiseHttpClient(api_key="your-api-key")
        
        # Denoise a file
        denoised = client.denoise_file("noisy.wav")
        client.save_audio(denoised, "clean.wav")
        
        # Or use base64
        with open("noisy.wav", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        result = client.denoise_base64(b64)
        ```
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 120,
        verify_ssl: bool = True
    ):
        """
        Initialize the DenoiseHttpClient.
        
        Args:
            api_key: API key for authentication (required)
            timeout: Request timeout in seconds (default: 120)
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
                "1. DenoiseHttpClient(api_key='your-api-key')\n"
                "2. Environment variable: export FONADALABS_API_KEY='your-api-key'\n"
                "3. .env file with FONADALABS_API_KEY='your-api-key'"
            )
        
        self.session = requests.Session()
        
        # Add API key to headers (required for all requests)
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}"
        })
    
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
    
    def denoise_file(
        self,
        file_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None
    ) -> bytes:
        """
        Denoise an audio file using file upload.
        
        Args:
            file_path: Path to the audio file to denoise
            output_path: Optional path to save the denoised audio
            
        Returns:
            Denoised audio as bytes (WAV format)
            
        Raises:
            FileNotFoundError: If the input file doesn't exist
            requests.RequestException: If the request fails
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "audio/wav")}
            response = self.session.post(
                f"{self.base_url}/denoise",
                files=files,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
        
        self._check_credits_exhausted(response)
        response.raise_for_status()
        denoised_audio = response.content
        
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(denoised_audio)
        
        return denoised_audio
    
    def denoise_base64(
        self,
        audio_base64: str,
        filename: Optional[str] = None
    ) -> bytes:
        """
        Denoise audio provided as base64 encoded data.
        
        Internally converts base64 to bytes and sends to /denoise endpoint.
        
        Args:
            audio_base64: Base64 encoded audio data
            filename: Optional filename for the audio (default: audio.wav)
            
        Returns:
            Denoised audio as bytes (WAV format)
                
        Raises:
            requests.RequestException: If the request fails
        """
        # Decode base64 to bytes
        audio_bytes = base64.b64decode(audio_base64)
        
        # Send as file upload to /denoise endpoint
        filename = filename or "audio.wav"
        files = {"file": (filename, io.BytesIO(audio_bytes), "audio/wav")}
        
        response = self.session.post(
            f"{self.base_url}/denoise",
            files=files,
            timeout=self.timeout,
            verify=self.verify_ssl
        )
        
        self._check_credits_exhausted(response)
        response.raise_for_status()
        return response.content
    
    def denoise_numpy(
        self,
        audio_array: np.ndarray,
        sample_rate: int = 16000
    ) -> np.ndarray:
        """
        Denoise a numpy array of audio data.
        
        Args:
            audio_array: Audio data as numpy array
            sample_rate: Sample rate of the audio (default: 16000)
            
        Returns:
            Denoised audio as numpy array
            
        Raises:
            requests.RequestException: If the request fails
        """
        try:
            import soundfile as sf
        except ImportError:
            raise ImportError("soundfile is required for numpy audio processing")
        
        # Ensure audio is float32 and 1D
        if audio_array.ndim > 1:
            audio_array = audio_array.mean(axis=1)
        audio_array = audio_array.astype(np.float32)
        
        # Convert numpy array to WAV bytes (with proper WAV header)
        buffer = io.BytesIO()
        sf.write(buffer, audio_array, sample_rate, format='WAV', subtype='FLOAT')
        buffer.seek(0)
        
        # Send as file upload to /denoise endpoint
        files = {"file": ("numpy_audio.wav", buffer, "audio/wav")}
        
        response = self.session.post(
            f"{self.base_url}/denoise",
            files=files,
            timeout=self.timeout,
            verify=self.verify_ssl
        )
        
        self._check_credits_exhausted(response)
        response.raise_for_status()
        
        # API returns raw WAV bytes - parse with soundfile
        buffer_out = io.BytesIO(response.content)
        denoised_array, _ = sf.read(buffer_out)
        
        return denoised_array
    
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
    
    @staticmethod
    def save_audio(audio_bytes: bytes, output_path: Union[str, Path]) -> None:
        """
        Save audio bytes to a file.
        
        Args:
            audio_bytes: Audio data as bytes
            output_path: Path to save the audio file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


__all__ = ["DenoiseHttpClient", "DenoiseError", "CreditsExhaustedError", "RateLimitError"]

