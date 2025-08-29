from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import SessionLocal
from app.schemas.onboarding import OnboardQuestRead, UserInfoCreate, UserInfoRead, UserInfoUpdate
from app.crud.onboarding import onboard_quest_crud, user_info_crud
from app.core.security import verify_passport_jwt

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/questions", response_model=List[OnboardQuestRead])
def get_onboarding_questions(db: Session = Depends(get_db)):
    """
    Get all onboarding questions.
    """
    questions = onboard_quest_crud.get_all_questions(db)
    return questions


@router.get("/questions/{question_id}", response_model=OnboardQuestRead)
def get_onboarding_question(question_id: int, db: Session = Depends(get_db)):
    """
    Get a specific onboarding question by ID.
    """
    question = onboard_quest_crud.get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Question not found"
        )
    return question


@router.post("/user-info", response_model=UserInfoRead)
def create_user_info(
    user_info: UserInfoCreate,
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt)
):
    """
    Create user info. The user ID is taken from JWT claims.
    """
    # Extract user ID from JWT claims
    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID"
        )
    
    # Override usid with the one from JWT
    user_info.usid = int(user_id)
    
    # Check if user info already exists
    existing_info = user_info_crud.get_user_info(db, user_info.usid)
    if existing_info:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User info already exists"
        )
    
    return user_info_crud.create_user_info(db, user_info)


@router.get("/user-info", response_model=UserInfoRead)
def get_user_info(
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt)
):
    """
    Get user info for the authenticated user.
    """
    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID"
        )
    
    user_info = user_info_crud.get_user_info(db, int(user_id))
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User info not found"
        )
    
    return user_info


@router.put("/user-info", response_model=UserInfoRead)
def update_user_info(
    user_info_update: UserInfoUpdate,
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt)
):
    """
    Update user info for the authenticated user.
    """
    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID"
        )
    
    updated_info = user_info_crud.update_user_info(db, int(user_id), user_info_update)
    if not updated_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User info not found"
        )
    
    return updated_info


@router.delete("/user-info")
def delete_user_info(
    db: Session = Depends(get_db),
    claims: dict = Depends(verify_passport_jwt)
):
    """
    Delete user info for the authenticated user.
    """
    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID"
        )
    
    deleted = user_info_crud.delete_user_info(db, int(user_id))
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User info not found"
        )
    
    return {"message": "User info deleted successfully"}