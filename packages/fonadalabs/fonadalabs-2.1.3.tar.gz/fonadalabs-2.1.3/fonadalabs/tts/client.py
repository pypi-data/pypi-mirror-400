"""
Main TTS Client for FonadaLabs SDK
"""

import httpx
import websockets
import asyncio
import json
from typing import Optional, Callable, AsyncGenerator, Dict, Any
from pathlib import Path
import io


class TTSError(Exception):
    """Custom exception for TTS-related errors"""
    pass


class CreditsExhaustedError(TTSError):
    """Raised when API credits are exhausted"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details or {}
        self.current_usage = details.get("current_usage") if details else None
        self.credit_limit = details.get("credit_limit") if details else None
        self.remaining_balance = details.get("remaining_balance") if details else None
        self.estimated_cost = details.get("estimated_cost") if details else None
        self.billing_cycle_end = details.get("billing_cycle_end") if details else None
        self.tier = details.get("tier") if details else None


class RateLimitError(TTSError):
    """Raised when API rate limit is exceeded"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details or {}
        self.rate_limit = details.get("rate_limit") if details else None
        self.current_usage = details.get("current_usage") if details else None
        self.remaining = details.get("remaining") if details else None
        self.reset_at = details.get("reset_at") if details else None
        self.retry_after_seconds = details.get("retry_after_seconds") if details else None
        self.rate_period = details.get("rate_period") if details else None


class TTSClient:
    """
    Client for interacting with FonadaLabs TTS API.
    
    Supports both HTTP POST and WebSocket connections for text-to-speech generation.
    Supports up to 40 concurrent requests.
    
    Example:
        >>> client = TTSClient()
        >>> # HTTP POST method
        >>> audio_data = client.generate_audio("Hello world", "Anuradha")
        >>> # WebSocket method with callbacks
        >>> client.generate_audio_ws(
        ...     "Long text here",
        ...     "Anuradha",
        ...     on_progress=lambda data: print(f"Progress: {data['percent']}%")
        ... )
        >>> # Check server health
        >>> health = client.health_check()
        >>> print(f"Available slots: {health['available_slots']}")
    """
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 300):
        """
        Initialize the TTS client.
        
        Args:
            api_key: API key for authentication (required, uses FONADALABS_API_KEY env var if not provided)
            timeout: Request timeout in seconds (default: 300)
            
        Raises:
            TTSError: If no API key is provided
            
        Note:
            The base URL is configured internally via FONADALABS_API_URL
            environment variable (default: http://localhost:9557).
            Users cannot override it for security reasons.
        """
        # Internal base URL configuration
        # Users cannot override it for security reasons
        import os
        self.base_url = os.getenv("FONADALABS_API_URL", "https://api.fonada.ai").rstrip("/")
        self.api_key = api_key or os.getenv("FONADALABS_API_KEY")
        
        # Validate that API key is provided
        if not self.api_key:
            raise TTSError(
                "API key is required. Please provide it via:\n"
                "1. TTSClient(api_key='your-api-key')\n"
                "2. Environment variable: export FONADALABS_API_KEY='your-api-key'\n"
                "3. .env file with FONADALABS_API_KEY='your-api-key'"
            )
        
        self.timeout = timeout
        self.http_client = None
    
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(timeout=self.timeout)
        return self.http_client
    
    async def _close_http_client(self):
        """Close HTTP client"""
        if self.http_client is not None:
            await self.http_client.aclose()
            self.http_client = None
    
    def _get_auth_headers(self) -> Dict[str, Any]:
        """Get authorization headers for HTTP requests"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def generate_audio_async(
        self,
        text: str,
        voice: str,
        language: str = "Hindi",
        output_file: Optional[str] = None
    ) -> bytes:
        """
        Generate audio from text using HTTP POST (async version).
        Suitable for large texts. Streams response progressively.
        
        Args:
            text: Text to convert to speech
            voice: Voice name (e.g., "Anuradha")
            language: Language name (e.g., "Hindi", "English", "Telugu", "Tamil")
            output_file: Optional path to save the audio file
            
        Returns:
            Audio data as bytes
            
        Raises:
            TTSError: If the API request fails
        """
        endpoint = f"{self.base_url}/tts/generate-audio-large"
        
        try:
            client = await self._get_http_client()
            
            async with client.stream(
                "POST",
                endpoint,
                headers=self._get_auth_headers(),
                json={"input": text, "voice": voice, "language": language}
            ) as response:
                # Check for credit exhaustion or rate limit
                if response.status_code in (402, 429):
                    try:
                        error_text = await response.aread()
                        error_json = json.loads(error_text.decode())
                        error_type = error_json.get("error")
                        
                        if error_type == "credits_exhausted":
                            raise CreditsExhaustedError(
                                error_json.get("message", "Credits exhausted"),
                                details=error_json.get("details", {})
                            )
                        elif error_type == "rate_limit_exceeded":
                            raise RateLimitError(
                                error_json.get("message", "Rate limit exceeded"),
                                details=error_json.get("details", {})
                            )
                    except (json.JSONDecodeError, AttributeError):
                        pass
                
                if response.status_code == 429:
                    error_text = await response.aread()
                    raise TTSError(f"Too many concurrent requests: {error_text.decode()}")
                elif response.status_code != 200:
                    error_text = await response.aread()
                    raise TTSError(
                        f"API request failed with status {response.status_code}: {error_text.decode()}"
                    )
                
                # Collect all chunks
                audio_chunks = []
                async for chunk in response.aiter_bytes():
                    audio_chunks.append(chunk)
                
                audio_data = b"".join(audio_chunks)
                
                # Save to file if requested
                if output_file:
                    Path(output_file).write_bytes(audio_data)
                
                return audio_data
                
        except httpx.HTTPError as e:
            raise TTSError(f"HTTP error occurred: {str(e)}")
        except Exception as e:
            raise TTSError(f"An error occurred: {str(e)}")
    
    def generate_audio(
        self,
        text: str,
        voice: str,
        language: str = "Hindi",
        output_file: Optional[str] = None
    ) -> bytes:
        """
        Generate audio from text using HTTP POST (synchronous wrapper).
        Suitable for large texts. Streams response progressively.
        
        Args:
            text: Text to convert to speech
            voice: Voice name (e.g., "Anuradha")
            language: Language name (e.g., "Hindi", "English", "Telugu", "Tamil")
            output_file: Optional path to save the audio file
            
        Returns:
            Audio data as bytes
            
        Raises:
            TTSError: If the API request fails
        """
        async def _run():
            try:
                return await self.generate_audio_async(text, voice, language, output_file)
            finally:
                await self._close_http_client()
        
        return asyncio.run(_run())
    
    async def generate_audio_ws_async(
        self,
        text: str,
        voice: str,
        language: str = "Hindi",
        output_file: Optional[str] = None,
        on_chunk: Optional[Callable[[int, bytes], None]] = None,
        on_complete: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[str], None]] = None
    ) -> bytes:
        """
        Generate audio from text using WebSocket (async version).
        Streams audio chunks as they are generated.
        
        Protocol (matches current TTS API):
        1. Client sends: {"api_key": "...", "text": "...", "voice_id": "...", "language": "..."}
        2. Server sends: {"status": "streaming", "request_id": 123}
        3. Server sends: Binary audio chunks
        4. Server sends: {"status": "complete", "stats": {...}}
        
        Args:
            text: Text to convert to speech
            voice: Voice name (e.g., "Pravaha", "Shruti", "Aabha")
            language: Language name (e.g., "Hindi", "English", "Telugu", "Tamil")
            output_file: Optional path to save the audio file
            on_chunk: Callback for audio chunks (receives chunk_number and audio bytes)
            on_complete: Callback when generation is complete (receives stats dict)
            on_error: Callback for errors (receives error message)
            
        Returns:
            Complete audio data as bytes
            
        Raises:
            TTSError: If the WebSocket connection or generation fails
            CreditsExhaustedError: If credits are exhausted
            RateLimitError: If rate limit is exceeded
        """
        ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_endpoint = f"{ws_url}/tts/generate-audio-ws"
        
        audio_chunks = []
        chunk_number = 0
        
        try:
            # Connect with larger max message size for audio chunks
            async with websockets.connect(ws_endpoint, max_size=16 * 1024 * 1024, ping_interval=20) as websocket:                
                # Send TTS request (current API format)
                request_data = {
                    "api_key": self.api_key,
                    "text": text,
                    "voice_id": voice,
                    "language": language
                }
                
                await websocket.send(json.dumps(request_data))
                
                # Process messages
                streaming_started = False
                
                async for message in websocket:
                    # Check if message is JSON or binary
                    if isinstance(message, bytes):
                        # Binary audio chunk
                        chunk_number += 1
                        audio_chunks.append(message)
                        
                        if on_chunk:
                            try:
                                on_chunk(chunk_number, message)
                            except Exception as callback_error:
                                import sys
                                print(f"Warning: on_chunk callback error: {callback_error}", file=sys.stderr)
                    
                    elif isinstance(message, str):
                        # JSON message
                        try:
                            data = json.loads(message)
                            status = data.get("status")
                            msg_type = data.get("type")
                            
                            # Handle "status" or "type" field (API uses both)
                            if status == "streaming" or msg_type == "status":
                                streaming_started = True
                                # Optional: notify that streaming started
                            
                            elif status == "complete" or msg_type == "complete":
                                # Stream complete
                                if on_complete:
                                    try:
                                        on_complete(data.get("stats", {}))
                                    except Exception as callback_error:
                                        import sys
                                        print(f"Warning: on_complete callback error: {callback_error}", file=sys.stderr)
                                break
                            
                            elif status == "error" or msg_type == "error":
                                error_msg = data.get("error") or data.get("message", "Unknown error")
                                error_type = data.get("error")
                                
                                # Check for specific error types
                                if error_type == "credits_exhausted":
                                    raise CreditsExhaustedError(
                                        data.get("message", "Credits exhausted"),
                                        details=data.get("details", {})
                                    )
                                elif error_type == "rate_limit_exceeded":
                                    raise RateLimitError(
                                        data.get("message", "Rate limit exceeded"),
                                        details=data.get("details", {})
                                    )
                                
                                if on_error:
                                    try:
                                        on_error(error_msg)
                                    except Exception as callback_error:
                                        import sys
                                        print(f"Warning: on_error callback error: {callback_error}", file=sys.stderr)
                                
                                raise TTSError(f"Server error: {error_msg}")
                        
                        except json.JSONDecodeError:
                            # Not valid JSON, skip
                            import sys
                            print(f"Warning: Received non-JSON text message: {message[:100]}", file=sys.stderr)
                
                # Combine all audio chunks
                audio_data = b"".join(audio_chunks)
                
                if not audio_data:
                    raise TTSError("No audio data received from server")
                
                # Save to file if requested
                if output_file:
                    Path(output_file).write_bytes(audio_data)
                
                return audio_data
                
        except websockets.exceptions.WebSocketException as e:
            raise TTSError(f"WebSocket error: {str(e)}")
        except (CreditsExhaustedError, RateLimitError):
            raise
        except Exception as e:
            raise TTSError(f"An error occurred: {str(e)}")
    
    def generate_audio_ws(
        self,
        text: str,
        voice: str,
        language: str = "Hindi",
        output_file: Optional[str] = None,
        on_chunk: Optional[Callable[[int, bytes], None]] = None,
        on_complete: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[str], None]] = None
    ) -> bytes:
        """
        Generate audio from text using WebSocket (synchronous wrapper).
        Streams audio chunks as they are generated.
        
        Args:
            text: Text to convert to speech
            voice: Voice name (e.g., "Pravaha", "Shruti", "Aabha", "Svara", "Vaanee")
            language: Language name (e.g., "Hindi", "English", "Telugu", "Tamil")
            output_file: Optional path to save the audio file
            on_chunk: Callback for audio chunks (receives chunk_number and audio bytes)
            on_complete: Callback when generation is complete (receives stats dict)
            on_error: Callback for errors (receives error message)
            
        Returns:
            Complete audio data as bytes
            
        Raises:
            TTSError: If the WebSocket connection or generation fails
            CreditsExhaustedError: If credits are exhausted
            RateLimitError: If rate limit is exceeded
        """
        return asyncio.run(
            self.generate_audio_ws_async(
                text, voice, language, output_file,
                on_chunk, on_complete, on_error
            )
        )
    
    async def stream_audio_async(
        self,
        text: str,
        voice: str
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream audio chunks as they are generated (async generator).
        Useful for playing audio in real-time without waiting for full generation.
        
        Args:
            text: Text to convert to speech
            voice: Voice name (e.g., "Anuradha")
            
        Yields:
            Audio chunk bytes
            
        Raises:
            TTSError: If the API request fails
        """
        endpoint = f"{self.base_url}/tts/generate-audio-large"
        
        try:
            client = await self._get_http_client()
            
            async with client.stream(
                "POST",
                endpoint,
                headers=self._get_auth_headers(),
                json={"input": text, "voice": voice}
            ) as response:
                # Check for credit exhaustion or rate limit
                if response.status_code in (402, 429):
                    try:
                        error_text = await response.aread()
                        error_json = json.loads(error_text.decode())
                        error_type = error_json.get("error")
                        
                        if error_type == "credits_exhausted":
                            raise CreditsExhaustedError(
                                error_json.get("message", "Credits exhausted"),
                                details=error_json.get("details", {})
                            )
                        elif error_type == "rate_limit_exceeded":
                            raise RateLimitError(
                                error_json.get("message", "Rate limit exceeded"),
                                details=error_json.get("details", {})
                            )
                    except (json.JSONDecodeError, AttributeError):
                        pass
                
                if response.status_code == 429:
                    error_text = await response.aread()
                    raise TTSError(f"Too many concurrent requests: {error_text.decode()}")
                elif response.status_code != 200:
                    error_text = await response.aread()
                    raise TTSError(
                        f"API request failed with status {response.status_code}: {error_text.decode()}"
                    )
                
                async for chunk in response.aiter_bytes():
                    yield chunk
                    
        except httpx.HTTPError as e:
            raise TTSError(f"HTTP error occurred: {str(e)}")
        except Exception as e:
            raise TTSError(f"An error occurred: {str(e)}")
        finally:
            await self._close_http_client()
    
    async def health_check_async(self) -> Dict[str, Any]:
        """
        Check the health status of the TTS API server (async version).
        
        Returns:
            Dictionary containing health status information:
            - status: "healthy" if server is operational
            - active_requests: Current number of active requests
            - max_concurrent_requests: Maximum allowed concurrent requests
            - available_slots: Number of available request slots
            
        Raises:
            TTSError: If the health check fails
        """
        endpoint = f"{self.base_url}/health"
        
        try:
            client = await self._get_http_client()
            response = await client.get(endpoint, headers=self._get_auth_headers())
            
            if response.status_code != 200:
                raise TTSError(f"Health check failed with status {response.status_code}")
            
            return response.json()
            
        except httpx.HTTPError as e:
            raise TTSError(f"HTTP error during health check: {str(e)}")
        except Exception as e:
            raise TTSError(f"Health check error: {str(e)}")
        finally:
            await self._close_http_client()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health status of the TTS API server (synchronous wrapper).
        
        Returns:
            Dictionary containing health status information
            
        Raises:
            TTSError: If the health check fails
        """
        return asyncio.run(self.health_check_async())
    
    async def get_server_status_async(self) -> Dict[str, Any]:
        """
        Get detailed server status information (async version).
        
        Returns:
            Dictionary containing detailed server status:
            - server: Server name
            - version: Server version
            - concurrency: Concurrency information
            - endpoints: Available endpoints
            
        Raises:
            TTSError: If the status check fails
        """
        endpoint = f"{self.base_url}/status"
        
        try:
            client = await self._get_http_client()
            response = await client.get(endpoint, headers=self._get_auth_headers())
            
            if response.status_code != 200:
                raise TTSError(f"Status check failed with status {response.status_code}")
            
            return response.json()
            
        except httpx.HTTPError as e:
            raise TTSError(f"HTTP error during status check: {str(e)}")
        except Exception as e:
            raise TTSError(f"Status check error: {str(e)}")
        finally:
            await self._close_http_client()
    
    def get_server_status(self) -> Dict[str, Any]:
        """
        Get detailed server status information (synchronous wrapper).
        
        Returns:
            Dictionary containing detailed server status
            
        Raises:
            TTSError: If the status check fails
        """
        return asyncio.run(self.get_server_status_async())
    
    def __enter__(self):
        """Context manager support"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        if self.http_client:
            asyncio.run(self._close_http_client())
    
    async def __aenter__(self):
        """Async context manager support"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager cleanup"""
        await self._close_http_client()

