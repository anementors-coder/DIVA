import logging
import uuid
from typing import Optional

from sqlalchemy.orm import Session
from app.crud.user_info import user_info_crud
from app.schemas.user_info import UserInfoUpdate
from app.models.onboarding import UserInfo
from app.utils.s3_utils import (
    upload_resume_to_s3,
    delete_resume_from_s3,
    extract_file_key_from_url,
    generate_presigned_url,
)
from app.core.errors import OnboardingException

logger = logging.getLogger(__name__)

class ResumeCRUD:
    async def upload_resume(
        self, db: Session, *, user_id: int, file_content: bytes, content_type: str
    ) -> UserInfo:
        """
        Orchestrates uploading a resume, deleting the old one, and updating the user's record.
        """
        logger.info(f"Processing resume upload for user {user_id}")
        
        user_info = user_info_crud.get_user_info(db, user_id)
        if not user_info:
            logger.warning(f"User info not found for user {user_id} during resume upload")
            raise OnboardingException(error_code="USER_INFO_NOT_FOUND", message="User info not found. Please submit onboarding info first.")

        if user_info.resume_url:
            old_key = extract_file_key_from_url(user_info.resume_url)
            if old_key:
                logger.info(f"Deleting old resume for user {user_id}: {old_key}")
                await delete_resume_from_s3(old_key)

        file_key = f"resumes/{user_id}/resume_{uuid.uuid4()}.pdf"
        try:
            s3_url = await upload_resume_to_s3(file_content, file_key, content_type)
        except Exception as e:
            logger.error(f"Failed to upload resume to S3 for user {user_id}: {str(e)}")
            raise OnboardingException(error_code="S3_UPLOAD_FAILED", message="Failed to upload resume to storage.")

        updated_info = user_info_crud.update_user_info(db, user_id, UserInfoUpdate(resume_url=s3_url))
        
        if not updated_info:
            logger.error(f"Failed to update resume URL for user {user_id} after S3 upload.")
            raise OnboardingException(error_code="DATABASE_ERROR", message="Could not update user info with new resume URL.")

        logger.info(f"Successfully uploaded resume and updated URL for user {user_id}")
        return updated_info

    def get_resume_download_url(self, db: Session, *, user_id: int, expiration: int = 300) -> Optional[str]:
        """
        Generates a presigned URL for a user's resume.
        """
        logger.info(f"Generating resume download URL for user {user_id}")
        
        user_info = user_info_crud.get_user_info(db, user_id)
        if not user_info or not user_info.resume_url:
            return None

        file_key = extract_file_key_from_url(user_info.resume_url)
        if not file_key:
            logger.error(f"Could not extract S3 key from URL for user {user_id}: {user_info.resume_url}")
            return None

        return generate_presigned_url(file_key, expiration=expiration)

    async def delete_resume(self, db: Session, *, user_id: int) -> UserInfo:
        """
        Deletes a user's resume from S3 and clears the URL from their record.
        """
        logger.info(f"Processing resume deletion for user {user_id}")
        
        user_info = user_info_crud.get_user_info(db, user_id)
        if not user_info:
            raise OnboardingException(error_code="USER_INFO_NOT_FOUND", message="User info not found.")

        if not user_info.resume_url:
            logger.warning(f"User {user_id} attempted to delete a resume, but none exists.")
            return user_info

        file_key = extract_file_key_from_url(user_info.resume_url)
        if file_key:
            await delete_resume_from_s3(file_key)
        
        updated_info = user_info_crud.update_user_info(db, user_id, UserInfoUpdate(resume_url=None))

        if not updated_info:
            logger.error(f"Failed to clear resume URL for user {user_id} after S3 deletion.")
            raise OnboardingException(error_code="DATABASE_ERROR", message="Could not update user info after deleting resume.")

        logger.info(f"Successfully deleted resume and cleared URL for user {user_id}")
        return updated_info

resume_crud = ResumeCRUD()