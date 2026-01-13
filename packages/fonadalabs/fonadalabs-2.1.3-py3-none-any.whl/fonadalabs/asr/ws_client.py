# fonadalabs/ws_client.py
import asyncio
import json
import os
from pathlib import Path
from typing import Optional

from loguru import logger

class ASRWebSocketClient:
    """
    Fonada ASR WebSocket client.
    - Supports secure (wss) and insecure (ws) connections
    - Requires authentication token for all connections
    - Streams audio in chunks (real-time simulation)
    - Logs progress, buffering, and final results
    """

    def __init__(self, url: str = "wss://api.fonada.ai/v1/asr/stream", token: Optional[str] = None):
        self.url = url
        self.token = token or os.getenv("FONADALABS_API_KEY")
        
        # Validate that token is provided (required for authentication)
        if not self.token:
            raise ValueError(
                "Authentication token is required. Please provide it via:\n"
                "1. ASRWebSocketClient(token='your-api-key')\n"
                "2. Environment variable: export FONADALABS_API_KEY='your-api-key'\n"
                "3. .env file with FONADALABS_API_KEY='your-api-key'"
            )
        
    async def transcribe_file(self, file_path: str, language_id: str = "hi") -> dict:
        """
        Stream an audio file to the ASR backend over WebSocket and return the final transcription.
        """
        try:
            import websockets  # type: ignore
            from websockets.exceptions import WebSocketException
        except ImportError as exc:
            raise ImportError(
                "websockets is required for ASRWebSocketClient. Install the SDK with the 'ws' extra: "
                "pip install fonadalabs-sdk[ws]"
            ) from exc

        try:
            # Connect to WebSocket (no headers needed - auth is done via first message)
            async with websockets.connect(self.url, max_size=None) as ws:
                return await self._handle_transcription(ws, file_path, language_id)

        except WebSocketException as e:
            logger.exception(f"WebSocket error: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.exception(f"WebSocket error: {e}")
            return {"error": str(e)}

    async def _handle_transcription(self, ws, file_path: str, language_id: str) -> dict:
        """Handle the WebSocket transcription logic"""
        logger.info(f" Connected to {self.url}")

        # Step 1: Wait for server's "connected" message
        welcome_msg = await ws.recv()
        welcome_data = json.loads(welcome_msg)
        logger.info(f" Server says: {welcome_data.get('message')}")

        # Step 2: Send authentication with API key and language
        auth_message = {
            "api_key": self.token,
            "language": language_id
        }
        await ws.send(json.dumps(auth_message))
        logger.info(f" Sent authentication with language: {language_id}")

        # Step 3: Wait for authentication response
        auth_response = await ws.recv()
        auth_data = json.loads(auth_response)
        
        if auth_data.get("status") != "authenticated":
            error_msg = auth_data.get("message", "Authentication failed")
            logger.error(f" Authentication failed: {error_msg}")
            return {"error": error_msg}
        
        logger.success(f" Authenticated successfully")

        # Step 4: Send audio file as binary
        audio_bytes = Path(file_path).read_bytes()
        logger.info(f" Sending audio file ({len(audio_bytes)} bytes)")
        await ws.send(audio_bytes)
        
        # Step 5: Wait for transcription response
        response = await ws.recv()
        result = json.loads(response)
        
        if result.get("status") == "complete":
            logger.success(f" Transcription complete: {result.get('text')}")
            return {
                "text": result.get("text"),
                "language": result.get("language"),
                "duration": result.get("audio_duration"),
                "credits_used": result.get("credits_used")
            }
        elif result.get("status") == "error":
            error_msg = result.get("message", "Unknown error")
            logger.error(f" Error: {error_msg}")
            return {"error": error_msg}
        
        return {"error": "Unexpected response from server"}

    def transcribe(self, file_path: str, language_id: str = "hi"):
        """
        Synchronous wrapper (for convenience in scripts).
        """
        return asyncio.run(self.transcribe_file(file_path, language_id))
