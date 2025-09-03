import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user_info import user_info_crud
from app.schemas.user_info import (
    UserInfoCreate,
    UserInfoRead,
    UserInfoUpdate,
    URLUpdate,
    ResumeURLUpdate,
    LinkedInURLUpdate,
)
from app.schemas.general_response import ErrorResponse
from app.core.security import verify_passport_jwt
from app.core.errors import OnboardingException
from app.utils.api_utils import (
    get_db,
    handle_onboarding_exception,
    validate_onboarding_query_structure,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/endpoints.log"),
        logging.StreamHandler(),
    ],
)
router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/submit/response",
    response_model=UserInfoRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": UserInfoRead, "description": "User info created successfully"},
        400: {"model": ErrorResponse, "description": "Bad request - Invalid input, empty referral, or invalid onboarding query structure"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing authentication"},
        403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
        409: {"model": ErrorResponse, "description": "Conflict - User info already exists"},
        422: {"model": ErrorResponse, "description": "Validation error - Invalid request body"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
)
def create_user_info(
    user_info: UserInfoCreate,
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt),
):
    """Create onboarding info for the authenticated user."""
    try:
        user_id = int(claims.get("sub"))
        logger.info(f"Creating user info for user {user_id}")

        if not validate_onboarding_query_structure(user_info.onboarding_query):
            logger.warning(f"Invalid onboarding_query structure for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid onboarding_query structure.",
            )

        if not user_info.referral or not user_info.referral.strip():
            logger.warning(f"Empty referral source for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Referral source cannot be empty",
            )

        if user_info_crud.get_user_info(db, user_id):
            logger.warning(f"User info already exists for user {user_id}")
            raise HTTPException(status_code=409, detail="User info already exists")

        result = user_info_crud.create_user_info(db, user_info, user_id)
        logger.info(f"Successfully created user info for user {user_id}")
        return result
    except OnboardingException as e:
        logger.error(
            f"OnboardingException creating user info for user {user_id}: {e.error_code} - {e.message}"
        )
        handle_onboarding_exception(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error creating user info for user {user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Could not create user info.")


@router.get(
    "/user-info/me",
    response_model=UserInfoRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": UserInfoRead, "description": "User info retrieved successfully"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing authentication"},
        403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "User info not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
)
def get_my_user_info(
    db: Session = Depends(get_db), claims: dict = Depends(verify_passport_jwt)
):
    """Get onboarding info for the authenticated user."""
    try:
        user_id = int(claims.get("sub"))
        logger.info(f"Retrieving user info for user {user_id}")
        user_info = user_info_crud.get_user_info(db, user_id)
        if not user_info:
            logger.warning(f"User info not found for user {user_id}")
            raise HTTPException(status_code=404, detail="User info not found")
        logger.info(f"Successfully retrieved user info for user {user_id}")
        return user_info
    except OnboardingException as e:
        logger.error(
            f"OnboardingException retrieving user info for user {user_id}: {e.error_code} - {e.message}"
        )
        handle_onboarding_exception(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error retrieving user info for user {user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Could not retrieve user info.")


@router.get(
    "/user-info/{usid}",
    response_model=UserInfoRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": UserInfoRead, "description": "User info retrieved successfully"},
        400: {"model": ErrorResponse, "description": "Bad request - Invalid user ID"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing authentication"},
        403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "User info not found"},
        422: {"model": ErrorResponse, "description": "Validation error - Invalid path parameter"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
)
def get_user_info_by_usid(
    usid: int,
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt),
):
    """Get user info by user ID (usid). (Admin/protected)"""
    try:
        logger.info(f"Retrieving user info for usid {usid} by admin {claims.get('sub')}")
        user_info = user_info_crud.get_user_info(db, usid)
        if not user_info:
            logger.warning(f"User info not found for usid {usid}")
            raise HTTPException(status_code=404, detail="User info not found")
        logger.info(f"Successfully retrieved user info for usid {usid}")
        return user_info
    except OnboardingException as e:
        logger.error(
            f"OnboardingException retrieving user info for usid {usid}: {e.error_code} - {e.message}"
        )
        handle_onboarding_exception(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error retrieving user info for usid {usid}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Could not retrieve user info.")


@router.get(
    "/user-info",
    response_model=List[UserInfoRead],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": List[UserInfoRead], "description": "All user info records retrieved successfully"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing authentication"},
        403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
)
def get_all_user_info(
    db: Session = Depends(get_db), claims: dict = Depends(verify_passport_jwt)
):
    """Get all user info records. (Admin/protected)"""
    try:
        logger.info(f"Retrieving all user info by admin {claims.get('sub')}")
        user_infos = user_info_crud.get_all_user_info(db)
        logger.info(f"Successfully retrieved {len(user_infos)} user info records")
        return user_infos
    except OnboardingException as e:
        logger.error(
            f"OnboardingException retrieving all user info: {e.error_code} - {e.message}"
        )
        handle_onboarding_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error retrieving all user info: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve user info.")


@router.put(
    "/user-info/me",
    response_model=UserInfoRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": UserInfoRead, "description": "User info updated successfully"},
        400: {"model": ErrorResponse, "description": "Bad request - Invalid input, empty referral, or invalid onboarding query structure"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing authentication"},
        403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "User info not found"},
        422: {"model": ErrorResponse, "description": "Validation error - Invalid request body"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
)
def update_my_user_info(
    user_info_update: UserInfoUpdate,
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt),
):
    """Update onboarding info for the authenticated user."""
    try:
        user_id = int(claims.get("sub"))
        logger.info(f"Updating user info for user {user_id}")
        update_data = user_info_update.model_dump(exclude_unset=True)

        if "onboarding_query" in update_data and not validate_onboarding_query_structure(
            update_data["onboarding_query"]
        ):
            logger.warning(
                f"Invalid onboarding_query structure in update for user {user_id}"
            )
            raise HTTPException(
                status_code=400, detail="Invalid onboarding_query structure"
            )

        if "referral" in update_data and (
            not update_data["referral"] or not update_data["referral"].strip()
        ):
            logger.warning(f"Empty referral source in update for user {user_id}")
            raise HTTPException(status_code=400, detail="Referral source cannot be empty")

        updated_info = user_info_crud.update_user_info(db, user_id, user_info_update)
        if not updated_info:
            logger.warning(f"User info not found for update: user {user_id}")
            raise HTTPException(status_code=404, detail="User info not found")
        logger.info(f"Successfully updated user info for user {user_id}")
        return updated_info
    except OnboardingException as e:
        logger.error(
            f"OnboardingException updating user info for user {user_id}: {e.error_code} - {e.message}"
        )
        handle_onboarding_exception(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error updating user info for user {user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Could not update user info.")


@router.patch(
    "/user-info/me/resume-url",
    response_model=UserInfoRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": UserInfoRead, "description": "Resume URL updated successfully"},
        400: {"model": ErrorResponse, "description": "Bad request - Invalid URL format"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing authentication"},
        403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "User info not found"},
        422: {"model": ErrorResponse, "description": "Validation error - Invalid request body"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
)
def update_my_resume_url(
    resume_data: ResumeURLUpdate,
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt),
):
    """
    Update only the resume URL for the authenticated user. 
    Note: This is for manually setting a URL, not for uploading a file.
    """
    try:
        user_id = int(claims.get("sub"))
        logger.info(f"Updating resume URL for user {user_id}")
        url_update = URLUpdate(resume_url=str(resume_data.resume_url))
        updated_info = user_info_crud.update_user_urls(db, user_id, url_update)
        if not updated_info:
            logger.warning(f"User info not found for resume URL update: user {user_id}")
            raise HTTPException(status_code=404, detail="User info not found")
        logger.info(f"Successfully updated resume URL for user {user_id}")
        return updated_info
    except OnboardingException as e:
        logger.error(
            f"OnboardingException updating resume URL for user {user_id}: {e.error_code} - {e.message}"
        )
        handle_onboarding_exception(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error updating resume URL for user {user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Could not update resume URL.")


@router.patch(
    "/user-info/me/linkedin-url",
    response_model=UserInfoRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": UserInfoRead, "description": "LinkedIn URL updated successfully"},
        400: {"model": ErrorResponse, "description": "Bad request - Invalid URL format"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing authentication"},
        403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "User info not found"},
        422: {"model": ErrorResponse, "description": "Validation error - Invalid request body"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
)
def update_my_linkedin_url(
    linkedin_data: LinkedInURLUpdate,
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt),
):
    """Update only the LinkedIn URL for the authenticated user."""
    try:
        user_id = int(claims.get("sub"))
        logger.info(f"Updating LinkedIn URL for user {user_id}")
        url_update = URLUpdate(linkedin_url=str(linkedin_data.linkedin_url))
        updated_info = user_info_crud.update_user_urls(db, user_id, url_update)
        if not updated_info:
            logger.warning(
                f"User info not found for LinkedIn URL update: user {user_id}"
            )
            raise HTTPException(status_code=404, detail="User info not found")
        logger.info(f"Successfully updated LinkedIn URL for user {user_id}")
        return updated_info
    except OnboardingException as e:
        logger.error(
            f"OnboardingException updating LinkedIn URL for user {user_id}: {e.error_code} - {e.message}"
        )
        handle_onboarding_exception(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error updating LinkedIn URL for user {user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Could not update LinkedIn URL.")


@router.delete(
    "/user-info/{usid}",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User info deleted successfully"},
        400: {"model": ErrorResponse, "description": "Bad request - Invalid user ID"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing authentication"},
        403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "User info not found"},
        422: {"model": ErrorResponse, "description": "Validation error - Invalid path parameter"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
)
def delete_user_info_by_usid(
    usid: int,
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt),
):
    """Delete user info by user ID (usid). (Admin/protected)"""
    try:
        logger.info(f"Deleting user info for usid {usid} by admin {claims.get('sub')}")
        if not user_info_crud.delete_user_info(db, usid):
            logger.warning(f"User info not found for deletion: usid {usid}")
            raise HTTPException(status_code=404, detail="User info not found")
        logger.info(f"Successfully deleted user info for usid {usid}")
        return None # Corresponds to status 204 No Content, but FastAPI handles 200 with no body
    except OnboardingException as e:
        logger.error(
            f"OnboardingException deleting user info for usid {usid}: {e.error_code} - {e.message}"
        )
        handle_onboarding_exception(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting user info for usid {usid}: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not delete user info.")