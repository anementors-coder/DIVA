from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_onboarding_info():
    """
    Simple placeholder for onboarding logic.
    Replace with real onboarding questionnaire/profile setup routes.
    """
    return {"message": "Welcome to the onboarding API!"}
