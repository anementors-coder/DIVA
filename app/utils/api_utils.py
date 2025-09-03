import logging
from typing import Dict, Any
import re  # Import the regular expression module

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.errors import OnboardingException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/endpoints.log"),   # write to logs/endpoints.log
        logging.StreamHandler()                # still show in console
    ]
)
logger = logging.getLogger(__name__)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def handle_onboarding_exception(e: OnboardingException):
    """Convert OnboardingException to HTTPException with enhanced logging"""
    status_code_map = {
        "USER_INFO_ALREADY_EXISTS": status.HTTP_409_CONFLICT,
        "QUESTION_CREATION_FAILED": status.HTTP_400_BAD_REQUEST,
        "DATABASE_CONSTRAINT_VIOLATION": status.HTTP_400_BAD_REQUEST,
        "DATABASE_CONNECTION_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "DATABASE_TRANSACTION_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "INVALID_INPUT": status.HTTP_400_BAD_REQUEST,
    }
    
    status_code = status_code_map.get(e.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Enhanced logging based on error severity
    if status_code >= 500:
        logger.error(f"Critical OnboardingException: {e.error_code} - {e.message}")
    elif status_code >= 400:
        logger.warning(f"Client error OnboardingException: {e.error_code} - {e.message}")
    else:
        logger.info(f"OnboardingException: {e.error_code} - {e.message}")
    
    raise HTTPException(status_code=status_code, detail=e.message)

def validate_onboarding_query_structure(onboarding_query: Dict[str, Any]) -> bool:
    """
    Validate the structure of onboarding_query JSONB field.
    Expected structure: {"qX": {"question": str, "answer": str}, ...}
    """
    try:
        logger.debug("Validating onboarding_query structure")

        if not isinstance(onboarding_query, dict):
            logger.warning("onboarding_query is not a dictionary")
            return False

        if not onboarding_query:
            logger.warning("onboarding_query is empty")
            return False

        for key, value in onboarding_query.items():
            if not (key.startswith("q") and key[1:].isdigit()):
                logger.warning(f"Invalid key format: {key}")
                return False

            if not (
                isinstance(value, dict)
                and "question" in value
                and "answer" in value
                and isinstance(value["question"], str)
                and isinstance(value["answer"], str)
                and value["question"].strip()
                and value["answer"].strip()
            ):
                logger.warning(f"Invalid structure for {key}: {value}")
                return False

        logger.debug("onboarding_query structure validation passed")
        return True

    except Exception as e:
        logger.error(f"Error validating onboarding_query structure: {str(e)}")
        return False

def validate_linkedin_url(url: str) -> bool:
    """
    Validate the LinkedIn profile URL format.
    """
    if not url:
        return False
    # Regex to match common LinkedIn profile URL patterns
    pattern = re.compile(r'^(https?://)?(www\.)?linkedin\.com/in/[\w-]+/?$')
    return bool(pattern.match(url))