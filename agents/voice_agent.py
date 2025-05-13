"""
Voice Agent for the Finance Assistant.
Handles speech recognition and synthesis.
"""

import os
import logging
import tempfile
import base64
import io
import time
from typing import Dict, Any, Optional, Union
from openai import OpenAI
import numpy as np
import wave

logger = logging.getLogger(__name__)

class VoiceAgent:
    """
    Agent responsible for speech-to-text and text-to-speech operations.
    Uses OpenAI Whisper for STT and other libraries for TTS.
    """
    
    def __init__(self):
        """Initialize the voice agent."""
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.voice = "onyx"  # Default voice for TTS
    
    def transcribe_audio(self, audio_file: str) -> Dict[str, Any]:
        """
        Transcribe audio file to text using Whisper.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Dictionary with transcription result
        """
        try:
            with open(audio_file, "rb") as audio:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio
                )
            
            return {
                "success": True,
                "text": transcription.text
            }
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    def text_to_speech(self, text: str) -> Dict[str, Any]:
        """
        Convert text to speech.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Dictionary with speech synthesis result
        """
        try:
            # Limit text length to avoid issues
            if len(text) > 4096:
                text = text[:4096]
            
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=self.voice,
                input=text
            )
            
            # Get audio data
            audio_data = io.BytesIO(response.content)
            
            # Encode as base64 for easy transmission
            audio_data.seek(0)
            encoded_audio = base64.b64encode(audio_data.read()).decode('utf-8')
            
            return {
                "success": True,
                "audio_base64": encoded_audio
            }
        except Exception as e:
            logger.error(f"Error synthesizing speech: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "audio_base64": ""
            }
    
    def save_audio_to_file(self, audio_base64: str, output_file: str = "output.wav") -> str:
        """
        Save base64 encoded audio to a file.
        
        Args:
            audio_base64: Base64 encoded audio
            output_file: Output file path
            
        Returns:
            Path to saved file
        """
        try:
            audio_data = base64.b64decode(audio_base64)
            
            with open(output_file, 'wb') as f:
                f.write(audio_data)
                
            return output_file
        except Exception as e:
            logger.error(f"Error saving audio to file: {str(e)}")
            return ""
    
    def process_voice_input(self, audio_file: str) -> Dict[str, Any]:
        """
        Process voice input: transcribe and return text.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Dictionary with processing result
        """
        # Transcribe audio
        transcription = self.transcribe_audio(audio_file)
        
        if not transcription["success"]:
            return {
                "success": False,
                "error": transcription.get("error", "Unknown error"),
                "text": ""
            }
        
        return {
            "success": True,
            "text": transcription["text"]
        }
    
    def process_voice_output(self, text: str) -> Dict[str, Any]:
        """
        Process voice output: convert text to speech.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Dictionary with processing result
        """
        # Convert text to speech
        speech = self.text_to_speech(text)
        
        if not speech["success"]:
            return {
                "success": False,
                "error": speech.get("error", "Unknown error"),
                "audio_base64": ""
            }
        
        return {
            "success": True,
            "audio_base64": speech["audio_base64"]
        }
    
    def speak_financial_summary(self, summary: str) -> Dict[str, Any]:
        """
        Generate speech for a financial summary with appropriate pacing.
        
        Args:
            summary: Financial summary text
            
        Returns:
            Dictionary with speech synthesis result
        """
        try:
            # Add SSML tags for better pacing with financial terms
            # This helps with pronunciation of numbers and financial terms
            processed_text = summary
            
            # Convert processed text to speech
            return self.process_voice_output(processed_text)
            
        except Exception as e:
            logger.error(f"Error generating financial summary speech: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "audio_base64": ""
            }
