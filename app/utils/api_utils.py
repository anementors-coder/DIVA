# app/utils/api_utils.py
import logging
from typing import Dict, Any, Optional
import re
from urllib.parse import urlparse

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.errors import OnboardingException


logger = logging.getLogger(__name__)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# def handle_onboarding_exception(e: OnboardingException):
#     """Convert OnboardingException to HTTPException with enhanced logging"""
#     status_code_map = {
#         "USER_INFO_ALREADY_EXISTS": status.HTTP_409_CONFLICT,
#         "QUESTION_CREATION_FAILED": status.HTTP_400_BAD_REQUEST,
#         "DATABASE_CONSTRAINT_VIOLATION": status.HTTP_400_BAD_REQUEST,
#         "DATABASE_CONNECTION_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
#         "DATABASE_TRANSACTION_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
#         "INVALID_INPUT": status.HTTP_400_BAD_REQUEST,
#     }
    
#     status_code = status_code_map.get(e.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#     # Enhanced logging based on error severity
#     if status_code >= 500:
#         logger.error(f"Critical OnboardingException: {e.error_code} - {e.message}")
#     elif status_code >= 400:
#         logger.warning(f"Client error OnboardingException: {e.error_code} - {e.message}")
#     else:
#         logger.info(f"OnboardingException: {e.error_code} - {e.message}")
    
#     raise HTTPException(status_code=status_code, detail=e.message)

def handle_onboarding_exception(exc: OnboardingException):
    """
    Simply re-raise; global exception handlers will produce a consistent ErrorResponse.
    """
    raise exc


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

import re

def normalize_linkedin_url(url: str) -> Optional[str]:
    """
    Normalize a LinkedIn profile URL to canonical form:
      https://www.linkedin.com/in/<slug>

    Accepts inputs like:
      - linkedin.com/in/--
      - https://linkedin.com/in/--
      - https://www.linkedin.com/in/--
      - Optional trailing slash, query, or fragment
      - Any casing for host or 'in' segment

    Returns:
      Canonical URL string or None if invalid.
    """
    if not url:
        return None

    candidate = url.strip()

    # Ensure a scheme so urlparse works consistently
    if not re.match(r"^[a-z][a-z0-9+.\-]*://", candidate, flags=re.IGNORECASE):
        candidate = f"https://{candidate}"

    try:
        parsed = urlparse(candidate)
    except Exception:
        return None

    host = (parsed.netloc or "").split(":")[0].lower()
    # Allow linkedin.com and subdomains (e.g., www.linkedin.com, fr.linkedin.com)
    if not (host == "linkedin.com" or host.endswith(".linkedin.com")):
        return None

    # Find the 'in' segment and then take the next segment as slug
    segments = [seg for seg in (parsed.path or "").split("/") if seg]
    try:
        in_index = next(i for i, seg in enumerate(segments) if seg.lower() == "in")
    except StopIteration:
        return None

    # Must have a slug after 'in'
    if len(segments) <= in_index + 1:
        return None

    slug = segments[in_index + 1]

    # Slug: letters, digits, underscore, hyphen. Allows "--" as requested.
    if not re.fullmatch(r"[A-Za-z0-9_-]+", slug):
        return None

    # Canonical form: https + www + no trailing slash, no query/fragment
    return f"https://www.linkedin.com/in/{slug}"


def validate_linkedin_url(url: str) -> bool:
    """
    Lenient validator. Accepts schemeless or schemed URLs and validates they
    represent a LinkedIn profile path. Returns True if valid, else False.
    """
    return normalize_linkedin_url(url) is not None