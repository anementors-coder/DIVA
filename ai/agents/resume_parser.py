import json
import logging
from typing import Dict, Any, Union, Optional
from pathlib import Path

from ..llms.model import gemini_client
from ..llms.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class ResumeParserAgent:
    """
    Professional resume parser agent that extracts structured information from resume PDFs
    using Google's Gemini 2.5 Flash model.
    """
    
    def __init__(self):
        """Initialize the resume parser agent."""
        self.client = gemini_client
        self.system_prompt = settings.RESUME_PARSER_SYSTEM_PROMPT
        logger.info("Resume Parser Agent initialized")
    
    def parse_resume_from_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Parse a resume from a PDF file path.
        
        Args:
            file_path: Path to the PDF resume file
            
        Returns:
            Dictionary containing structured resume information
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a PDF
            Exception: For parsing errors
        """
        file_path = Path(file_path)
        
        # Validate file
        if not file_path.exists():
            raise FileNotFoundError(f"Resume file not found: {file_path}")
        
        if file_path.suffix.lower() != '.pdf':
            raise ValueError(f"Only PDF files are supported. Got: {file_path.suffix}")
        
        logger.info(f"Starting resume parsing for: {file_path.name}")
        
        try:
            # Generate content using Gemini with PDF input
            response = self.client.generate_content_with_file(
                prompt=self.system_prompt,
                file_path=file_path,
                mime_type="application/pdf"
            )
            
            # Parse the JSON response
            parsed_resume = self.client.parse_json_response(response)
            
            # Validate and enhance the parsed data
            validated_resume = self._validate_and_enhance_resume_data(parsed_resume)
            
            logger.info(f"Resume parsing completed successfully for: {file_path.name}")
            return validated_resume
            
        except Exception as e:
            logger.error(f"Failed to parse resume from file {file_path}: {str(e)}")
            raise
    
    def parse_resume_from_bytes(self, file_data: bytes, filename: str = "resume.pdf") -> Dict[str, Any]:
        """
        Parse a resume from PDF bytes data.
        
        Args:
            file_data: PDF file data as bytes
            filename: Optional filename for logging purposes
            
        Returns:
            Dictionary containing structured resume information
            
        Raises:
            ValueError: If file_data is empty or invalid
            Exception: For parsing errors
        """
        if not file_data:
            raise ValueError("Empty file data provided")
        
        logger.info(f"Starting resume parsing for: {filename}")
        
        try:
            # Generate content using Gemini with PDF bytes
            response = self.client.generate_content_with_file(
                prompt=self.system_prompt,
                file_data=file_data,
                mime_type="application/pdf"
            )
            
            # Parse the JSON response
            parsed_resume = self.client.parse_json_response(response)
            
            # Validate and enhance the parsed data
            validated_resume = self._validate_and_enhance_resume_data(parsed_resume)
            
            logger.info(f"Resume parsing completed successfully for: {filename}")
            return validated_resume
            
        except Exception as e:
            logger.error(f"Failed to parse resume from bytes {filename}: {str(e)}")
            raise
    
    def _validate_and_enhance_resume_data(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and enhance the parsed resume data with additional processing.
        
        Args:
            resume_data: Raw parsed resume data
            
        Returns:
            Enhanced and validated resume data
        """
        try:
            # Ensure basic structure exists
            validated_data = {
                "personal_information": resume_data.get("personal_information", {}),
                "professional_summary": resume_data.get("professional_summary", ""),
                "experience": resume_data.get("experience", []),
                "education": resume_data.get("education", []),
                "skills": resume_data.get("skills", {}),
                "certifications": resume_data.get("certifications", []),
                "projects": resume_data.get("projects", []),
                "additional_sections": resume_data.get("additional_sections", {}),
                "parsing_metadata": {
                    "model_used": settings.GEMINI_MODEL_NAME,
                    "parser_version": "1.0.0",
                    "total_sections_found": len(resume_data.keys())
                }
            }
            
            # Add any additional sections that weren't in the standard structure
            for key, value in resume_data.items():
                if key not in validated_data:
                    validated_data["additional_sections"][key] = value
            
            # Validate critical fields
            personal_info = validated_data["personal_information"]
            if not personal_info.get("name"):
                logger.warning("No name found in personal information")
            
            if not personal_info.get("email"):
                logger.warning("No email found in personal information")
            
            logger.info("Resume data validated and enhanced successfully")
            return validated_data
            
        except Exception as e:
            logger.error(f"Failed to validate resume data: {str(e)}")
            # Return original data if validation fails
            return resume_data
    
    def get_resume_summary(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of the parsed resume data.
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Dictionary containing resume summary information
        """
        try:
            personal_info = resume_data.get("personal_information", {})
            experience = resume_data.get("experience", [])
            education = resume_data.get("education", [])
            skills = resume_data.get("skills", {})
            
            summary = {
                "candidate_name": personal_info.get("name", "Unknown"),
                "contact_email": personal_info.get("email", "Not provided"),
                "total_experience_entries": len(experience),
                "total_education_entries": len(education),
                "skills_categories": len(skills) if isinstance(skills, dict) else 1,
                "has_professional_summary": bool(resume_data.get("professional_summary")),
                "total_projects": len(resume_data.get("projects", [])),
                "total_certifications": len(resume_data.get("certifications", [])),
                "additional_sections_count": len(resume_data.get("additional_sections", {})),
            }
            
            # Try to extract years of experience from the most recent job
            if experience and isinstance(experience, list) and len(experience) > 0:
                recent_job = experience[0]
                if isinstance(recent_job, dict) and "duration" in recent_job:
                    summary["most_recent_position"] = recent_job.get("title", "Unknown")
                    summary["most_recent_company"] = recent_job.get("company", "Unknown")
            
            logger.info("Resume summary generated successfully")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate resume summary: {str(e)}")
            return {"error": "Failed to generate summary"}
    
    def validate_client_connection(self) -> bool:
        """
        Validate that the Gemini client is working properly.
        
        Returns:
            True if connection is valid, False otherwise
        """
        return self.client.validate_connection()

# Global agent instance
resume_parser_agent = ResumeParserAgent()