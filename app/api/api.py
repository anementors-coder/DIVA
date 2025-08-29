# backend\app\app\api\v1\api.py
from fastapi import APIRouter
from app.api.endpoints import onboarding, auth

api_router = APIRouter()

api_router.include_router(onboarding.router, prefix="/signup", tags=["Onboarding"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
