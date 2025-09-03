import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import json
import logging
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
import io

from .config import settings

# Configure logging
logger = logging.getLogger(__name__)

class GeminiClient:
    """
    Professional Gemini API client for various AI tasks including resume parsing.
    """
    
    def __init__(self):
        """Initialize the Gemini client with configuration from settings."""
        self._configure_api()
        self._model = None
        self._initialize_model()
    
    def _configure_api(self) -> None:
        """Configure the Gemini API with the provided API key."""
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            logger.info("Gemini API configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {str(e)}")
            raise
    
    def _initialize_model(self) -> None:
        """Initialize the Gemini model with safety settings and generation config."""
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=settings.GEMINI_TEMPERATURE,
                max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
                top_p=settings.GEMINI_TOP_P,
                top_k=settings.GEMINI_TOP_K,
            )
            
            # Configure safety settings to allow most content for professional use
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
            
            self._model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL_NAME,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            logger.info(f"Gemini model {settings.GEMINI_MODEL_NAME} initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {str(e)}")
            raise
    
    def generate_content_with_file(
        self, 
        prompt: str, 
        file_path: Optional[Union[str, Path]] = None,
        file_data: Optional[bytes] = None,
        mime_type: str = "application/pdf"
    ) -> str:
        """
        Generate content using Gemini with file input (PDF, image, etc.).
        
        Args:
            prompt: The text prompt to send to the model
            file_path: Path to the file to upload (optional)
            file_data: Raw file data as bytes (optional)
            mime_type: MIME type of the file
            
        Returns:
            Generated content as string
            
        Raises:
            ValueError: If neither file_path nor file_data is provided
            Exception: For API errors or other failures
        """
        if not file_path and not file_data:
            raise ValueError("Either file_path or file_data must be provided")
        
        try:
            # Upload file to Gemini
            if file_path:
                file_path = Path(file_path)
                if not file_path.exists():
                    raise FileNotFoundError(f"File not found: {file_path}")
                
                uploaded_file = genai.upload_file(
                    path=str(file_path),
                    mime_type=mime_type
                )
            else:
                # Create a temporary file-like object from bytes
                uploaded_file = genai.upload_file(
                    path=io.BytesIO(file_data),
                    mime_type=mime_type
                )
            
            logger.info(f"File uploaded successfully: {uploaded_file.name}")
            
            # Generate content with the uploaded file
            response = self._model.generate_content([prompt, uploaded_file])
            
            if not response.text:
                logger.error("Empty response from Gemini API")
                raise Exception("Empty response from Gemini API")
            
            logger.info("Content generated successfully")
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate content with file: {str(e)}")
            raise
    
    def generate_content(self, prompt: str) -> str:
        """
        Generate content using Gemini with text-only input.
        
        Args:
            prompt: The text prompt to send to the model
            
        Returns:
            Generated content as string
        """
        try:
            response = self._model.generate_content(prompt)
            
            if not response.text:
                logger.error("Empty response from Gemini API")
                raise Exception("Empty response from Gemini API")
            
            logger.info("Text content generated successfully")
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate text content: {str(e)}")
            raise
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response from Gemini, handling potential formatting issues.
        
        Args:
            response: Raw response string from Gemini
            
        Returns:
            Parsed JSON as dictionary
            
        Raises:
            json.JSONDecodeError: If response cannot be parsed as JSON
        """
        try:
            # Remove potential markdown code block markers
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            # Parse JSON
            parsed_json = json.loads(response)
            logger.info("JSON response parsed successfully")
            return parsed_json
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Raw response: {response[:500]}...")  # Log first 500 chars
            raise
    
    def validate_connection(self) -> bool:
        """
        Validate the connection to Gemini API.
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            test_response = self.generate_content("Test connection")
            return bool(test_response)
        except Exception as e:
            logger.error(f"Connection validation failed: {str(e)}")
            return False

# Global client instance
gemini_client = GeminiClient()