# app/api/endpoints/onboard_questions.py
import os
import logging
from typing import List

from fastapi import APIRouter, Depends, status, Path, HTTPException
from sqlalchemy.orm import Session

from app.crud.onboard_questions import onboard_quest_crud
from app.schemas.onboard_questions import (
    OnboardQuestCreate,
    OnboardQuestRead,
    OnboardQuestUpdate,
)
from app.schemas.general_response import ErrorResponse, SuccessResponse
from app.core.security import verify_passport_jwt
from app.core.errors import OnboardingException, ErrorCode
from app.utils.api_utils import get_db, handle_onboarding_exception

# # Ensure logs directory exists
# os.makedirs("logs", exist_ok=True)

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
#     handlers=[
#         # logging.FileHandler("logs/endpoints.log"),
#         logging.StreamHandler(),
#     ],
# )
router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/questions",
    response_model=OnboardQuestRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"model": OnboardQuestRead, "description": "Question created successfully"},
        400: {"model": ErrorResponse, "description": "Bad request - Invalid input or empty title"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing authentication"},
        403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
        409: {"model": ErrorResponse, "description": "Conflict - Question already exists"},
        422: {"model": ErrorResponse, "description": "Validation error - Invalid request body"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def create_onboarding_question(
    question: OnboardQuestCreate,
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt),
):
    """Create a new onboarding question."""
    try:
        user_id = claims.get("sub")
        if not user_id:
            raise OnboardingException(ErrorCode.MISSING_USER_ID)

        if not question.title or not question.title.strip():
            raise OnboardingException(
                ErrorCode.MISSING_REQUIRED_FIELD,
                custom_message="Question title cannot be empty",
                details={"field": "title"},
            )

        logger.info(f"Creating question '{question.title[:50]}...' by user {user_id}")
        result = onboard_quest_crud.create_question(db, question)

        if not result:
            raise OnboardingException(ErrorCode.QUESTION_CREATION_FAILED)

        logger.info(f"Successfully created question with ID: {result.id}")
        return result
    except OnboardingException as e:
        handle_onboarding_exception(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error creating question")
        raise OnboardingException(
            ErrorCode.INTERNAL_SERVER_ERROR,
            custom_message="Could not create question.",
            details={"error": str(e)},
        )


@router.get(
    "/questions",
    response_model=List[OnboardQuestRead],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": List[OnboardQuestRead], "description": "Questions retrieved successfully"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing authentication"},
        403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def get_all_onboarding_questions(
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt),
):
    """Get all onboarding questions."""
    try:
        logger.info("Retrieving all onboarding questions")
        questions = onboard_quest_crud.get_all_questions(db)
        logger.info(f"Successfully retrieved {len(questions)} questions")
        return questions
    except OnboardingException as e:
        handle_onboarding_exception(e)
    except Exception as e:
        logger.exception("Unexpected error retrieving all questions")
        raise OnboardingException(
            ErrorCode.INTERNAL_SERVER_ERROR,
            custom_message="Could not retrieve questions.",
            details={"error": str(e)},
        )


@router.get(
    "/questions/{question_pk}",
    response_model=OnboardQuestRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": OnboardQuestRead, "description": "Question retrieved successfully"},
        400: {"model": ErrorResponse, "description": "Bad request - Invalid question ID"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing authentication"},
        403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "Question not found"},
        422: {"model": ErrorResponse, "description": "Validation error - Invalid path parameter"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def get_onboarding_question(
    question_pk: int = Path(..., ge=1, description="Primary key of the question"),
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt),
):
    """Get a specific onboarding question by its primary ID."""
    try:
        logger.info(f"Retrieving question with ID: {question_pk}")
        question = onboard_quest_crud.get_question_by_id(db, question_pk)
        if not question:
            raise OnboardingException(
                ErrorCode.QUESTION_NOT_FOUND,
                details={"id": question_pk},
            )
        logger.info(f"Successfully retrieved question: {question.id}")
        return question
    except OnboardingException as e:
        handle_onboarding_exception(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error retrieving question {question_pk}")
        raise OnboardingException(
            ErrorCode.INTERNAL_SERVER_ERROR,
            custom_message="Could not retrieve question.",
            details={"id": question_pk, "error": str(e)},
        )


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
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def get_questions_by_question_id(
    question_id: int = Path(..., ge=1, description="Shared question_id across versions"),
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt),
):
    """Get all question versions by the shared question_id."""
    try:
        logger.info(f"Retrieving questions by question_id: {question_id}")
        questions = onboard_quest_crud.get_questions_by_question_id(db, question_id)
        if not questions:
            raise OnboardingException(
                ErrorCode.QUESTION_NOT_FOUND,
                custom_message=f"No questions found with question_id {question_id}",
                details={"question_id": question_id},
            )
        logger.info(f"Successfully retrieved {len(questions)} version(s) for question_id {question_id}")
        return questions
    except OnboardingException as e:
        handle_onboarding_exception(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error retrieving questions by question_id {question_id}")
        raise OnboardingException(
            ErrorCode.INTERNAL_SERVER_ERROR,
            custom_message="Could not retrieve question versions.",
            details={"question_id": question_id, "error": str(e)},
        )


@router.put(
    "/questions/{question_pk}",
    response_model=OnboardQuestRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": OnboardQuestRead, "description": "Question updated successfully"},
        400: {"model": ErrorResponse, "description": "Bad request - Invalid input or empty title"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing authentication"},
        403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "Question not found"},
        422: {"model": ErrorResponse, "description": "Validation error - Invalid request body or path parameter"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def update_onboarding_question(
    question_pk: int = Path(..., ge=1, description="Primary key of the question"),
    question_update: OnboardQuestUpdate = ...,
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt),
):
    """Update a specific onboarding question."""
    try:
        user_id = claims.get("sub")
        if not user_id:
            raise OnboardingException(ErrorCode.MISSING_USER_ID)

        update_data = question_update.model_dump(exclude_unset=True)
        if not update_data:
            raise OnboardingException(
                ErrorCode.MISSING_REQUIRED_FIELD,
                custom_message="No fields provided to update.",
            )

        if 'title' in update_data and not update_data['title'].strip():
            raise OnboardingException(
                ErrorCode.MISSING_REQUIRED_FIELD,
                custom_message="Question title cannot be empty",
                details={"field": "title"},
            )

        logger.info(f"Updating question {question_pk} by user {user_id}")
        updated_question = onboard_quest_crud.update_question(db, question_pk, question_update)
        if not updated_question:
            raise OnboardingException(
                ErrorCode.QUESTION_NOT_FOUND,
                details={"id": question_pk},
            )

        logger.info(f"Successfully updated question {question_pk}")
        return updated_question
    except OnboardingException as e:
        handle_onboarding_exception(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error updating question {question_pk}")
        raise OnboardingException(
            ErrorCode.INTERNAL_SERVER_ERROR,
            custom_message="Could not update question.",
            details={"id": question_pk, "error": str(e)},
        )


@router.delete(
    "/questions/{question_pk}",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": SuccessResponse, "description": "Question deleted successfully"},
        400: {"model": ErrorResponse, "description": "Bad request - Invalid question ID"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing authentication"},
        403: {"model": ErrorResponse, "description": "Forbidden - Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "Question not found"},
        422: {"model": ErrorResponse, "description": "Validation error - Invalid path parameter"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def delete_onboarding_question(
    question_pk: int = Path(..., ge=1, description="Primary key of the question"),
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt),
):
    """Delete a specific onboarding question."""
    try:
        user_id = claims.get("sub")
        if not user_id:
            raise OnboardingException(ErrorCode.MISSING_USER_ID)

        logger.info(f"Deleting question {question_pk} by user {user_id}")
        deleted = onboard_quest_crud.delete_question(db, question_pk)
        if not deleted:
            raise OnboardingException(
                ErrorCode.QUESTION_NOT_FOUND,
                details={"id": question_pk},
            )

        logger.info(f"Successfully deleted question {question_pk}")
        return SuccessResponse(message="Question deleted successfully", data={"id": question_pk})
    except OnboardingException as e:
        handle_onboarding_exception(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error deleting question {question_pk}")
        raise OnboardingException(
            ErrorCode.INTERNAL_SERVER_ERROR,
            custom_message="Could not delete question.",
            details={"id": question_pk, "error": str(e)},
        )