from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.onboarding import OnboardQuest, UserInfo
from app.schemas.onboarding import UserInfoCreate, UserInfoUpdate


class OnboardQuestCRUD:
    def get_all_questions(self, db: Session) -> List[OnboardQuest]:
        """Get all onboarding questions"""
        return db.query(OnboardQuest).order_by(OnboardQuest.id).all()
    
    def get_question_by_id(self, db: Session, question_id: int) -> Optional[OnboardQuest]:
        """Get a specific question by ID"""
        return db.query(OnboardQuest).filter(OnboardQuest.id == question_id).first()


class UserInfoCRUD:
    def create_user_info(self, db: Session, user_info: UserInfoCreate) -> UserInfo:
        """Create new user info record"""
        db_user_info = UserInfo(**user_info.dict())
        db.add(db_user_info)
        db.commit()
        db.refresh(db_user_info)
        return db_user_info
    
    def get_user_info(self, db: Session, usid: int) -> Optional[UserInfo]:
        """Get user info by user ID"""
        return db.query(UserInfo).filter(UserInfo.usid == usid).first()
    
    def update_user_info(self, db: Session, usid: int, user_info: UserInfoUpdate) -> Optional[UserInfo]:
        """Update user info"""
        db_user_info = db.query(UserInfo).filter(UserInfo.usid == usid).first()
        if db_user_info:
            update_data = user_info.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_user_info, field, value)
            db.commit()
            db.refresh(db_user_info)
        return db_user_info
    
    def delete_user_info(self, db: Session, usid: int) -> bool:
        """Delete user info"""
        db_user_info = db.query(UserInfo).filter(UserInfo.usid == usid).first()
        if db_user_info:
            db.delete(db_user_info)
            db.commit()
            return True
        return False


# Create instances
onboard_quest_crud = OnboardQuestCRUD()
user_info_crud = UserInfoCRUD() 
