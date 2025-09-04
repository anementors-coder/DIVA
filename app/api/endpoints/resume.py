# app/api/endpoints/resume.py
import os
import logging
from fastapi import APIRouter, Depends, status, File, UploadFile, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.crud.resume import resume_crud
from app.schemas.user_info import UserInfoRead, ResumeDownloadURL
from app.schemas.general_response import ErrorResponse
from app.core.security import verify_passport_jwt
from app.utils.api_utils import get_db, handle_onboarding_exception
from app.utils.s3_utils import validate_file_size, validate_pdf_content
from app.core.errors import OnboardingException, ErrorCode

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

router = APIRouter()
logger = logging.getLogger(__name__)


# =============================== Authenticated User ("/me") ===============================

@router.put(
    "/user-info/me",
    response_model=UserInfoRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": UserInfoRead, "description": "Resume uploaded and URL updated successfully"},
        400: {"model": ErrorResponse, "description": "Bad request - Invalid file type, size, or content"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "User info not found"},
        413: {"model": ErrorResponse, "description": "Payload too large"},
        415: {"model": ErrorResponse, "description": "Unsupported media type"},
        500: {"model": ErrorResponse, "description": "Internal server error or upload failure"},
    },
)
async def upload_my_resume(
    file: UploadFile = File(..., description="The resume file in PDF format."),
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt),
):
    """Upload or replace the resume for the authenticated user."""
    try:
        if not claims.get("sub"):
            raise OnboardingException(ErrorCode.MISSING_USER_ID)

        user_id = int(claims["sub"])

        if file.content_type != "application/pdf" or not file.filename.lower().endswith(".pdf"):
            raise OnboardingException(ErrorCode.INVALID_FILE_TYPE)

        contents = await file.read()
        if not validate_file_size(contents):
            raise OnboardingException(
                ErrorCode.FILE_TOO_LARGE,
                details={"max_size_mb": 5}
            )
        if not validate_pdf_content(contents):
            raise OnboardingException(ErrorCode.INVALID_FILE_CONTENT)

        return await resume_crud.upload_resume(
            db, user_id=user_id, file_content=contents, content_type=file.content_type
        )
    except OnboardingException as e:
        handle_onboarding_exception(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Endpoint error uploading resume for user {claims.get('sub')}: {str(e)}")
        raise OnboardingException(
            ErrorCode.FILE_UPLOAD_FAILED,
            custom_message="Could not upload resume.",
            details={"error": str(e)},
        )


@router.get(
    "/user-info/me",
    response_model=ResumeDownloadURL,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": ResumeDownloadURL, "description": "Secure download URL generated successfully."},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Resume not found"},
        500: {"model": ErrorResponse, "description": "Failed to generate URL"},
    },
)
def get_my_resume_download_url(
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt),
    expires_in_seconds: int = Query(300, ge=60, le=3600, description="URL expiration in seconds (60-3600)."),
):
    """Get a secure, temporary URL to download the authenticated user's resume."""
    try:
        if not claims.get("sub"):
            raise OnboardingException(ErrorCode.MISSING_USER_ID)
        user_id = int(claims["sub"])

        presigned_url = resume_crud.get_resume_download_url(db, user_id=user_id, expiration=expires_in_seconds)
        if not presigned_url:
            raise OnboardingException(ErrorCode.FILE_NOT_FOUND, custom_message="Resume not found for this user.")

        return ResumeDownloadURL(download_url=presigned_url, expires_in_seconds=expires_in_seconds)
    except OnboardingException as e:
        handle_onboarding_exception(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Endpoint error generating download URL for user {claims.get('sub')}: {str(e)}")
        raise OnboardingException(
            ErrorCode.INTERNAL_SERVER_ERROR,
            custom_message="Could not generate download link.",
            details={"error": str(e)},
        )


@router.delete(
    "/user-info/me",
    response_model=UserInfoRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": UserInfoRead, "description": "Resume deleted successfully"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "User info not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def delete_my_resume(
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt),
):
    """Delete the authenticated user's resume from storage and clear the link."""
    try:
        if not claims.get("sub"):
            raise OnboardingException(ErrorCode.MISSING_USER_ID)

        user_id = int(claims["sub"])
        return await resume_crud.delete_resume(db, user_id=user_id)
    except OnboardingException as e:
        handle_onboarding_exception(e)
    except Exception as e:
        logger.error(f"Endpoint error deleting resume for user {claims.get('sub')}: {str(e)}")
        raise OnboardingException(
            ErrorCode.INTERNAL_SERVER_ERROR,
            custom_message="Could not delete resume.",
            details={"error": str(e)},
        )


# ======================== Admin/Protected Endpoints for a specific User ("/{usid}") ========================

@router.put(
    "/user-info/{usid}",
    response_model=UserInfoRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": UserInfoRead, "description": "Resume uploaded successfully for the specified user."},
        400: {"model": ErrorResponse, "description": "Bad request - Invalid file or user ID."},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "User info not found for the specified user ID."},
        413: {"model": ErrorResponse, "description": "Payload too large"},
        415: {"model": ErrorResponse, "description": "Unsupported media type"},
        500: {"model": ErrorResponse, "description": "Internal server error."},
    },
)
async def upload_resume_for_user(
    usid: int = Path(..., ge=1),
    file: UploadFile = File(..., description="The resume file in PDF format."),
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt),
):
    """Upload or replace a resume for a specific user by their ID. (Admin/protected)"""
    try:
        admin_id = claims.get("sub")
        logger.info(f"Admin {admin_id} is uploading resume for user {usid}")

        if file.content_type != "application/pdf" or not file.filename.lower().endswith(".pdf"):
            raise OnboardingException(ErrorCode.INVALID_FILE_TYPE)

        contents = await file.read()
        if not validate_file_size(contents):
            raise OnboardingException(ErrorCode.FILE_TOO_LARGE, details={"max_size_mb": 5})
        if not validate_pdf_content(contents):
            raise OnboardingException(ErrorCode.INVALID_FILE_CONTENT)

        return await resume_crud.upload_resume(
            db, user_id=usid, file_content=contents, content_type=file.content_type
        )
    except OnboardingException as e:
        handle_onboarding_exception(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Endpoint error for admin {claims.get('sub')} uploading resume for user {usid}: {str(e)}")
        raise OnboardingException(
            ErrorCode.FILE_UPLOAD_FAILED,
            custom_message="Could not upload resume for the specified user.",
            details={"user_id": usid, "error": str(e)},
        )


@router.get(
    "/user-info/{usid}",
    response_model=ResumeDownloadURL,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": ResumeDownloadURL, "description": "Secure download URL generated successfully."},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Resume not found for the specified user."},
        500: {"model": ErrorResponse, "description": "Failed to generate URL"},
    },
)
def get_resume_download_url_for_user(
    usid: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt),
    expires_in_seconds: int = Query(300, ge=60, le=3600, description="URL expiration in seconds (60-3600)."),
):
    """Get a secure, temporary URL for a specific user's resume. (Admin/protected)"""
    try:
        admin_id = claims.get("sub")
        logger.info(f"Admin {admin_id} is requesting download URL for user {usid}'s resume")

        presigned_url = resume_crud.get_resume_download_url(db, user_id=usid, expiration=expires_in_seconds)
        if not presigned_url:
            raise OnboardingException(
                ErrorCode.FILE_NOT_FOUND,
                custom_message="Resume not found for the specified user.",
                details={"user_id": usid},
            )

        return ResumeDownloadURL(download_url=presigned_url, expires_in_seconds=expires_in_seconds)
    except OnboardingException as e:
        handle_onboarding_exception(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Endpoint error for admin {claims.get('sub')} getting download URL for user {usid}: {str(e)}")
        raise OnboardingException(
            ErrorCode.INTERNAL_SERVER_ERROR,
            custom_message="Could not generate download link for the specified user.",
            details={"user_id": usid, "error": str(e)},
        )


@router.delete(
    "/user-info/{usid}",
    response_model=UserInfoRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": UserInfoRead, "description": "Resume deleted successfully for the specified user."},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "User info not found for the specified user."},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def delete_resume_for_user(
    usid: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt),
):
    """Delete a specific user's resume from storage. (Admin/protected)"""
    try:
        admin_id = claims.get("sub")
        logger.info(f"Admin {admin_id} is deleting resume for user {usid}")
        return await resume_crud.delete_resume(db, user_id=usid)
    except OnboardingException as e:
        handle_onboarding_exception(e)
    except Exception as e:
        logger.error(f"Endpoint error for admin {claims.get('sub')} deleting resume for user {usid}: {str(e)}")
        raise OnboardingException(
            ErrorCode.INTERNAL_SERVER_ERROR,
            custom_message="Could not delete resume for the specified user.",
            details={"user_id": usid, "error": str(e)},
        )