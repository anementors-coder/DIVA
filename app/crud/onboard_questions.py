import logging
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.onboarding import OnboardQuest
from app.schemas.onboard_questions import OnboardQuestCreate, OnboardQuestUpdate
from app.core.errors import ErrorCode, OnboardingException

logger = logging.getLogger(__name__)


class OnboardQuestCRUD:
    """CRUD operations for OnboardQuest model"""

    def create_question(self, db: Session, question_data: OnboardQuestCreate) -> OnboardQuest:
        """Create a new onboarding question"""
        try:
            db_question = OnboardQuest(**question_data.model_dump())
            db.add(db_question)
            db.commit()
            db.refresh(db_question)
            logger.info(f"Created onboarding question with ID: {db_question.id}")
            return db_question
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error creating question: {str(e)}")
            raise OnboardingException(
                ErrorCode.DATABASE_CONSTRAINT_VIOLATION,
                "Failed to create question due to constraint violation",
                {"error": str(e)}
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating question: {str(e)}")
            raise OnboardingException(
                ErrorCode.QUESTION_CREATION_FAILED,
                details={"error": str(e)}
            )

    def get_all_questions(self, db: Session) -> List[OnboardQuest]:
        """Get all onboarding questions"""
        try:
            questions = (
                db.query(OnboardQuest)
                .order_by(OnboardQuest.question_id, OnboardQuest.created_at)
                .all()
            )
            return questions
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching questions: {str(e)}")
            raise OnboardingException(
                ErrorCode.DATABASE_CONNECTION_ERROR,
                details={"error": str(e)}
            )

    def get_question_by_id(self, db: Session, question_id: int) -> Optional[OnboardQuest]:
        """Get a specific question by ID"""
        try:
            question = db.query(OnboardQuest).filter(OnboardQuest.id == question_id).first()
            if not question:
                logger.warning(f"Question with ID {question_id} not found")
            return question
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching question {question_id}: {str(e)}")
            raise OnboardingException(
                ErrorCode.DATABASE_CONNECTION_ERROR,
                details={"error": str(e)}
            )

    def get_questions_by_question_id(self, db: Session, question_id: int) -> List[OnboardQuest]:
        """Get questions by question_id field"""
        try:
            return (
                db.query(OnboardQuest)
                .filter(OnboardQuest.question_id == question_id)
                .order_by(OnboardQuest.created_at)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching questions by question_id {question_id}: {str(e)}")
            raise OnboardingException(
                ErrorCode.DATABASE_CONNECTION_ERROR,
                details={"error": str(e)}
            )

    def update_question(self, db: Session, question_id: int, question_update: OnboardQuestUpdate) -> Optional[OnboardQuest]:
        """Update a question"""
        try:
            db_question = db.query(OnboardQuest).filter(OnboardQuest.id == question_id).first()
            if not db_question:
                return None

            update_data = question_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_question, field, value)

            db.commit()
            db.refresh(db_question)
            logger.info(f"Updated question with ID: {question_id}")
            return db_question
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error updating question {question_id}: {str(e)}")
            raise OnboardingException(
                ErrorCode.DATABASE_CONSTRAINT_VIOLATION,
                details={"error": str(e)}
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating question {question_id}: {str(e)}")
            raise OnboardingException(
                ErrorCode.DATABASE_TRANSACTION_ERROR,
                details={"error": str(e)}
            )

    def delete_question(self, db: Session, question_id: int) -> bool:
        """Delete a question"""
        try:
            db_question = db.query(OnboardQuest).filter(OnboardQuest.id == question_id).first()
            if not db_question:
                return False

            db.delete(db_question)
            db.commit()
            logger.info(f"Deleted question with ID: {question_id}")
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error deleting question {question_id}: {str(e)}")
            raise OnboardingException(
                ErrorCode.DATABASE_TRANSACTION_ERROR,
                details={"error": str(e)}
            )

# Create instance to be imported by endpoints
onboard_quest_crud = OnboardQuestCRUD()