"""
Voice Service for the Finance Assistant.
Provides access to the voice agent functionality.
"""

import os
import requests
import logging
import base64
import json
from typing import Dict, Any, Optional, BinaryIO
from fastapi import HTTPException, UploadFile, File

logger = logging.getLogger(__name__)

class VoiceService:
    """
    Service class for accessing voice agent functionality.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the voice service.
        
        Args:
            base_url: Base URL for the orchestrator service
        """
        self.base_url = base_url
    
    async def transcribe_audio(self, audio_file: BinaryIO) -> str:
        """
        Transcribe audio to text.
        
        Args:
            audio_file: Audio file object
            
        Returns:
            Transcribed text
        """
        try:
            url = f"{self.base_url}/voice/transcribe"
            
            # Prepare the file for upload
            files = {"audio": audio_file}
            
            response = requests.post(url, files=files)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("text", "")
            else:
                logger.error(f"Error transcribing audio: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Error transcribing audio")
        except Exception as e:
            logger.error(f"Error connecting to voice service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to voice service: {str(e)}")
    
    async def text_to_speech(self, text: str) -> bytes:
        """
        Convert text to speech.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Audio data
        """
        try:
            url = f"{self.base_url}/voice/synthesize"
            
            payload = {
                "text": text
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                audio_base64 = result.get("audio_base64", "")
                
                if audio_base64:
                    # Decode base64 to binary
                    return base64.b64decode(audio_base64)
                else:
                    logger.error("No audio data received")
                    raise HTTPException(status_code=500, detail="No audio data received")
            else:
                logger.error(f"Error synthesizing speech: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Error synthesizing speech")
        except Exception as e:
            logger.error(f"Error connecting to voice service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to voice service: {str(e)}")
    
    async def process_voice_query(self, audio_file: BinaryIO) -> Dict[str, Any]:
        """
        Process a voice query: transcribe, process, and return response with audio.
        
        Args:
            audio_file: Audio file object
            
        Returns:
            Dictionary with text response and audio response
        """
        try:
            # Step 1: Transcribe audio
            text = await self.transcribe_audio(audio_file)
            
            if not text:
                return {
                    "success": False,
                    "error": "Failed to transcribe audio",
                    "text": "",
                    "audio": None
                }
            
            # Step 2: Process the transcribed query
            url = f"{self.base_url}/process"
            payload = {
                "query": text
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code != 200:
                logger.error(f"Error processing query: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Error processing query: {response.status_code}",
                    "text": text,
                    "audio": None
                }
                
            result = response.json()
            response_text = result.get("text", "")
            
            # Step 3: Convert response to speech
            audio_data = await self.text_to_speech(response_text)
            
            return {
                "success": True,
                "text": response_text,
                "transcribed_query": text,
                "audio": audio_data
            }
            
        except Exception as e:
            logger.error(f"Error processing voice query: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "audio": None
            }
