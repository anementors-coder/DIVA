from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
import os 

BASEDIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_FILE_PATH = os.path.join(BASEDIR, '.env')

class Settings(BaseSettings):
    # App Configuration
    APP_NAME: str = "AI Mentor API"
    
    # Gemini Configuration
    GEMINI_API_KEY: str
    GEMINI_MODEL_NAME: str = "gemini-2.5-flash"
    GEMINI_TEMPERATURE: float = 0.1
    GEMINI_MAX_OUTPUT_TOKENS: int = 8192
    GEMINI_TOP_P: float = 0.95
    GEMINI_TOP_K: int = 40
    
    # Resume Parser Configuration
    RESUME_PARSER_SYSTEM_PROMPT: str = """You are a professional resume parser. Your task is to extract all information from the provided resume PDF and structure it into a comprehensive JSON format.

Rules:
1. Use main headings as primary keys (e.g., "Personal Information", "Education", "Experience", "Skills", etc.)
2. Use sub-headings and relevant categories as sub-keys
3. Preserve all information accurately - do not omit any details
4. If a section doesn't have clear sub-headings, create logical sub-categories
5. For dates, preserve the original format but also provide a standardized format when possible
6. For contact information, extract phone, email, address, LinkedIn, portfolio links separately
7. For experience and education, include all details like dates, descriptions, achievements, etc.
8. Return only valid JSON - no additional text or explanations

Expected JSON structure example:
{
  "personal_information": {
    "name": "...",
    "email": "...",
    "phone": "...",
    "address": "...",
    "linkedin": "...",
    "portfolio": "..."
  },
  "professional_summary": "...",
  "experience": [
    {
      "title": "...",
      "company": "...",
      "duration": "...",
      "location": "...",
      "responsibilities": [...],
      "achievements": [...]
    }
  ],
  "education": [...],
  "skills": {...},
  "certifications": [...],
  "projects": [...],
  "additional_sections": {...}
}"""
    
    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, extra='ignore')

settings = Settings()