import logging
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.onboarding import UserInfo
from app.schemas.user_info import UserInfoCreate, UserInfoUpdate, URLUpdate
from app.core.errors import ErrorCode, OnboardingException

logger = logging.getLogger(__name__)


class UserInfoCRUD:
    """CRUD operations for UserInfo model"""

    def create_user_info(self, db: Session, user_info: UserInfoCreate, usid: int) -> UserInfo:
        """Create new user info record"""
        try:
            if db.query(UserInfo).filter(UserInfo.usid == usid).first():
                raise OnboardingException(
                    ErrorCode.USER_INFO_ALREADY_EXISTS, details={"user_id": usid}
                )

            user_info_dict = user_info.model_dump()
            user_info_dict['usid'] = usid

            db_user_info = UserInfo(**user_info_dict)
            db.add(db_user_info)
            db.commit()
            db.refresh(db_user_info)
            logger.info(f"Created user info for user ID: {usid}")
            return db_user_info
        except OnboardingException:
            db.rollback()
            raise
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error creating user info for user {usid}: {str(e)}")
            raise OnboardingException(
                ErrorCode.DATABASE_CONSTRAINT_VIOLATION,
                details={"user_id": usid, "error": str(e)}
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating user info for user {usid}: {str(e)}")
            raise OnboardingException(
                ErrorCode.DATABASE_TRANSACTION_ERROR,
                details={"user_id": usid, "error": str(e)}
            )

    def get_user_info(self, db: Session, usid: int) -> Optional[UserInfo]:
        """Get user info by user ID"""
        try:
            user_info = db.query(UserInfo).filter(UserInfo.usid == usid).first()
            if not user_info:
                logger.warning(f"User info for user {usid} not found")
            return user_info
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching user info for user {usid}: {str(e)}")
            raise OnboardingException(
                ErrorCode.DATABASE_CONNECTION_ERROR,
                details={"user_id": usid, "error": str(e)}
            )

    def get_all_user_info(self, db: Session) -> List[UserInfo]:
        """Get all user info records"""
        try:
            user_infos = (
                db.query(UserInfo)
                .order_by(UserInfo.created_at.desc())
                .all()
            )
            return user_infos
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching all user infos: {str(e)}")
            raise OnboardingException(
                ErrorCode.DATABASE_CONNECTION_ERROR,
                details={"error": str(e)}
            )

    def update_user_info(self, db: Session, usid: int, user_info: UserInfoUpdate) -> Optional[UserInfo]:
        """Update user info"""
        try:
            db_user_info = db.query(UserInfo).filter(UserInfo.usid == usid).first()
            if not db_user_info:
                return None

            update_data = user_info.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_user_info, field, value)

            db.commit()
            db.refresh(db_user_info)
            logger.info(f"Updated user info for user ID: {usid}")
            return db_user_info
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating user info for user {usid}: {str(e)}")
            raise OnboardingException(
                ErrorCode.DATABASE_TRANSACTION_ERROR,
                details={"user_id": usid, "error": str(e)}
            )

    def update_user_urls(self, db: Session, usid: int, url_update: URLUpdate) -> Optional[UserInfo]:
        """Update user resume and LinkedIn URLs"""
        try:
            db_user_info = db.query(UserInfo).filter(UserInfo.usid == usid).first()
            if not db_user_info:
                return None

            update_data = url_update.model_dump(exclude_unset=True)
            if not update_data:
                raise OnboardingException(
                    ErrorCode.INVALID_INPUT, "At least one URL must be provided."
                )

            for field, value in update_data.items():
                setattr(db_user_info, field, str(value) if value else None)

            db.commit()
            db.refresh(db_user_info)
            logger.info(f"Updated URLs for user ID: {usid}")
            return db_user_info
        except OnboardingException:
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating URLs for user {usid}: {str(e)}")
            raise OnboardingException(
                ErrorCode.DATABASE_TRANSACTION_ERROR,
                details={"user_id": usid, "error": str(e)}
            )

    def delete_user_info(self, db: Session, usid: int) -> bool:
        """Delete user info"""
        try:
            db_user_info = db.query(UserInfo).filter(UserInfo.usid == usid).first()
            if not db_user_info:
                return False

            db.delete(db_user_info)
            db.commit()
            logger.info(f"Deleted user info for user ID: {usid}")
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error deleting user info for user {usid}: {str(e)}")
            raise OnboardingException(
                ErrorCode.DATABASE_TRANSACTION_ERROR,
                details={"user_id": usid, "error": str(e)}
            )


# Create instance to be imported by endpoints
user_info_crud = UserInfoCRUD()