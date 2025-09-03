# backend\app\app\api\v1\api.py
from fastapi import APIRouter
from app.api.endpoints import auth, onboard_questions,  user_info, resume

api_router = APIRouter()

# api_router.include_router(onboarding.router, prefix="/onboard", tags=["Onboarding"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(onboard_questions.router, prefix="/onboarding", tags=["Questions"])
api_router.include_router(user_info.router, prefix="/user-info", tags=["User Info"])
api_router.include_router(resume.router, prefix="/resume", tags=["Resume"])
