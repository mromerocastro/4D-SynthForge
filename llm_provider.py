"""
LLM Provider Module

Defines the abstract base class and concrete implementations for different AI providers
(Gemini, Ollama) to support the Dual-Engine Architecture.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
import json
import logging
import time
import os

# Import provider libraries
try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import ollama
except ImportError:
    ollama = None

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
    GEMINI_CODE_MODEL,
    GEMINI_CODE_TEMPERATURE,
    OLLAMA_BASE_URL,
    OLLAMA_VISION_MODEL,
    OLLAMA_CODE_MODEL,
    OLLAMA_TEMPERATURE
)

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    """
    
    @abstractmethod
    def generate_text(self, prompt: str, system_instruction: str = None) -> str:
        """
        Generate text/code from a prompt.
        
        Args:
            prompt: User prompt
            system_instruction: System prompt/context
            
        Returns:
            Generated text string
        """
        pass

    @abstractmethod
    def analyze_video(self, video_path: str | Path, prompt: str) -> str:
        """
        Analyze a video file (or extracted frames) using a vision model.
        
        Args:
            video_path: Path to the video file
            prompt: analysis prompt
            
        Returns:
            Analysis result as string (usually JSON)
        """
        pass


class GeminiProvider(LLMProvider):
    """
    Implementation for Google's Gemini API.
    """
    
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set")
        if genai is None:
            raise ImportError("google-generativeai not installed")
            
        genai.configure(api_key=GEMINI_API_KEY)
        logger.info("✓ GeminiProvider initialized")

    def generate_text(self, prompt: str, system_instruction: str = None) -> str:
        model = genai.GenerativeModel(
            model_name=GEMINI_CODE_MODEL,
            generation_config={
                "temperature": GEMINI_CODE_TEMPERATURE,
                "response_mime_type": "text/plain"
            },
            system_instruction=system_instruction
        )
        
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini text generation failed: {e}")
            raise

    def analyze_video(self, video_path: str | Path, prompt: str) -> str:
        video_path = Path(video_path)
        
        # Initialize model
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            generation_config={
                "temperature": GEMINI_TEMPERATURE,
                "response_mime_type": "application/json"
            }
        )
        
        logger.info("⏳ Uploading to Gemini API...")
        video_file = genai.upload_file(str(video_path))
        
        # Wait for processing
        while video_file.state.name == "PROCESSING":
            time.sleep(1)
            video_file = genai.get_file(video_file.name)
            
        if video_file.state.name == "FAILED":
            raise RuntimeError("Video processing failed")
            
        logger.info("🤖 Running Gemini analysis...")
        response = model.generate_content(
            [prompt, video_file],
            request_options={"timeout": 600} # Increased timeout for video
        )
        
        return response.text


class OllamaProvider(LLMProvider):
    """
    Implementation for local Ollama instance.
    """
    
    def __init__(self):
        if ollama is None:
            raise ImportError("ollama library not installed. Run: pip install ollama")
        
        # Optional: Set client with custom host if provided
        if OLLAMA_BASE_URL:
            self.client = ollama.Client(host=OLLAMA_BASE_URL)
        else:
            self.client = ollama
            
        logger.info(f"✓ OllamaProvider initialized (Vision: {OLLAMA_VISION_MODEL}, Code: {OLLAMA_CODE_MODEL})")

    def generate_text(self, prompt: str, system_instruction: str = None) -> str:
        """
        Uses standard chat completion.
        """
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
            
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat(
                model=OLLAMA_CODE_MODEL,
                messages=messages,
                options={"temperature": OLLAMA_TEMPERATURE}
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Ollama text generation failed: {e}")
            raise

    def analyze_video(self, video_path: str | Path, prompt: str) -> str:
        """
        Note: Ollama current vision models (Llava) work best with images.
        For video, we extract a key frame (e.g., middle frame) or use a multi-frame approach.
        For this MVP, we will extract the middle frame using OpenCV.
        """
        import cv2
        import base64
        
        video_path = str(video_path)
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise IOError(f"Cannot open video: {video_path}")
            
        # Get total frames and pick the middle one
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        middle_frame_idx = total_frames // 2
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_idx)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise RuntimeError("Failed to read video frame")
            
        # Encode frame to JPEG bytes
        _, buffer = cv2.imencode('.jpg', frame)
        # Ollama python library expects bytes or path for 'images'
        image_bytes = buffer.tobytes()
        
        logger.info(f"🤖 Running Ollama analysis on frame {middle_frame_idx}...")
        
        # Enforce JSON structure via prompt since local models might not support 'response_format' perfectly yet
        # or depend on the specific model.
        prompt += "\n\nIMPORTANT: Output ONLY valid JSON."
        
        response = self.client.chat(
            model=OLLAMA_VISION_MODEL,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [image_bytes]
            }],
            options={"temperature": OLLAMA_TEMPERATURE}
        )
        
        content = response['message']['content']
        
        # Attempt to clean markdown if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        return content

def get_provider(provider_name: str) -> LLMProvider:
    """Factory to get the configured provider."""
    if provider_name.lower() == "gemini":
        return GeminiProvider()
    elif provider_name.lower() == "ollama":
        return OllamaProvider()
    else:
        raise ValueError(f"Unknown provider: {provider_name}")
