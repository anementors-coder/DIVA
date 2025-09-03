import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud.onboard_questions import onboard_quest_crud
from app.schemas.onboard_questions import OnboardQuestCreate, OnboardQuestRead, OnboardQuestUpdate
from app.schemas.general_response import ErrorResponse  # Import the new ErrorResponse
from app.core.security import verify_passport_jwt
from app.core.errors import OnboardingException
from app.utils.api_utils import get_db, handle_onboarding_exception

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/endpoints.log"),   # write to logs/endpoints.log
        logging.StreamHandler()                # still show in console
    ]
)
router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/questions",
    response_model=OnboardQuestRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": OnboardQuestRead, "description": "Question created successfully"},
        400: {"model": ErrorResponse, "description": "Bad request - Invalid input or empty title"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing authentication"},
        403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
        422: {"model": ErrorResponse, "description": "Validation error - Invalid request body"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def create_onboarding_question(
    question: OnboardQuestCreate,
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt)
):
    """Create a new onboarding question."""
    try:
        if not question.title.strip():
            logger.warning(f"Attempt to create question with empty title by user {claims.get('sub')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question title cannot be empty"
            )
        logger.info(f"Creating question with title: {question.title[:50]}... by user {claims.get('sub')}")
        result = onboard_quest_crud.create_question(db, question)
        logger.info(f"Successfully created question with ID: {result.id}")
        return result
    except OnboardingException as e:
        logger.error(f"OnboardingException creating question: {e.error_code} - {e.message}")
        handle_onboarding_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error creating question: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not create question.")

@router.get(
    "/questions", 
    response_model=List[OnboardQuestRead],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": List[OnboardQuestRead], "description": "Questions retrieved successfully"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing authentication"},
        403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def get_all_onboarding_questions(db: Session = Depends(get_db)):
    """Get all onboarding questions."""
    try:
        logger.info("Retrieving all onboarding questions")
        questions = onboard_quest_crud.get_all_questions(db)
        logger.info(f"Successfully retrieved {len(questions)} questions")
        return questions
    except OnboardingException as e:
        logger.error(f"OnboardingException retrieving all questions: {e.error_code} - {e.message}")
        handle_onboarding_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error retrieving all questions: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve questions.")

@router.get(
    "/questions/{question_id}",
    response_model=OnboardQuestRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": OnboardQuestRead, "description": "Question retrieved successfully"},
        400: {"model": ErrorResponse, "description": "Bad request - Invalid question ID"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing authentication"},
        403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "Question not found"},
        422: {"model": ErrorResponse, "description": "Validation error - Invalid path parameter"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def get_onboarding_question(question_id: int, db: Session = Depends(get_db)):
    """Get a specific onboarding question by its primary ID."""
    try:
        logger.info(f"Retrieving question with ID: {question_id}")
        question = onboard_quest_crud.get_question_by_id(db, question_id)
        if not question:
            logger.warning(f"Question not found with ID: {question_id}")
            raise HTTPException(status_code=404, detail="Question not found")
        logger.info(f"Successfully retrieved question: {question.id}")
        return question
    except OnboardingException as e:
        logger.error(f"OnboardingException retrieving question {question_id}: {e.error_code} - {e.message}")
        handle_onboarding_exception(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving question {question_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve question.")

@router.get(
    "/questions/by-question-id/{question_id}",
    response_model=List[OnboardQuestRead],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": List[OnboardQuestRead], "description": "Question versions retrieved successfully"},
        400: {"model": ErrorResponse, "description": "Bad request - Invalid question ID"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing authentication"},
        403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "No questions found with the specified question_id"},
        422: {"model": ErrorResponse, "description": "Validation error - Invalid path parameter"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def get_questions_by_question_id(question_id: int, db: Session = Depends(get_db)):
    """Get all question versions by the shared question_id."""
    try:
        logger.info(f"Retrieving questions by question_id: {question_id}")
        questions = onboard_quest_crud.get_questions_by_question_id(db, question_id)
        if not questions:
            logger.warning(f"No questions found with question_id: {question_id}")
            raise HTTPException(status_code=404, detail=f"No questions found with question_id {question_id}")
        logger.info(f"Successfully retrieved {len(questions)} question versions for question_id: {question_id}")
        return questions
    except OnboardingException as e:
        logger.error(f"OnboardingException retrieving questions by question_id {question_id}: {e.error_code} - {e.message}")
        handle_onboarding_exception(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving questions by question_id {question_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve question versions.")

@router.put(
    "/questions/{question_id}",
    response_model=OnboardQuestRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": OnboardQuestRead, "description": "Question updated successfully"},
        400: {"model": ErrorResponse, "description": "Bad request - Invalid input or empty title"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing authentication"},
        403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "Question not found"},
        422: {"model": ErrorResponse, "description": "Validation error - Invalid request body or path parameter"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def update_onboarding_question(
    question_id: int,
    question_update: OnboardQuestUpdate,
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt)
):
    """Update a specific onboarding question."""
    try:
        logger.info(f"Updating question {question_id} by user {claims.get('sub')}")
        update_data = question_update.model_dump(exclude_unset=True)
        if 'title' in update_data and not update_data['title'].strip():
            logger.warning(f"Attempt to update question {question_id} with empty title by user {claims.get('sub')}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question title cannot be empty")
        
        updated_question = onboard_quest_crud.update_question(db, question_id, question_update)
        if not updated_question:
            logger.warning(f"Question not found for update: {question_id}")
            raise HTTPException(status_code=404, detail="Question not found")
        logger.info(f"Successfully updated question {question_id}")
        return updated_question
    except OnboardingException as e:
        logger.error(f"OnboardingException updating question {question_id}: {e.error_code} - {e.message}")
        handle_onboarding_exception(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating question {question_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not update question.")

@router.delete(
    "/questions/{question_id}",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Question deleted successfully"},
        400: {"model": ErrorResponse, "description": "Bad request - Invalid question ID"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing authentication"},
        403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "Question not found"},
        422: {"model": ErrorResponse, "description": "Validation error - Invalid path parameter"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def delete_onboarding_question(
    question_id: int,
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt)
):
    """Delete a specific onboarding question."""
    try:
        logger.info(f"Deleting question {question_id} by user {claims.get('sub')}")
        deleted = onboard_quest_crud.delete_question(db, question_id)
        if not deleted:
            logger.warning(f"Question not found for deletion: {question_id}")
            raise HTTPException(status_code=404, detail="Question not found")
        logger.info(f"Successfully deleted question {question_id}")
        return None
    except OnboardingException as e:
        logger.error(f"OnboardingException deleting question {question_id}: {e.error_code} - {e.message}")
        handle_onboarding_exception(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting question {question_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not delete question.")