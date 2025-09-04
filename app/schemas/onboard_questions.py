# app/schemas/onboard_questions.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class OnboardQuestBase(BaseModel):
    """Base schema for an onboarding question."""
    question_id: int = Field(..., ge=1, description="Stable identifier shared across versions.")
    title: str = Field(..., min_length=1, max_length=500, description="The question text presented to the user.")
    description: Optional[str] = Field(None, max_length=2000, description="Additional context/help text.")
    icon: Optional[str] = Field(None, max_length=50, description="Frontend icon identifier.")


class OnboardQuestCreate(OnboardQuestBase):
    """Schema used for creating a new onboarding question."""
    pass


class OnboardQuestUpdate(BaseModel):
    """Schema used for updating an existing onboarding question."""
    question_id: Optional[int] = Field(None, ge=1)
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    icon: Optional[str] = Field(None, max_length=50)


class OnboardQuestRead(OnboardQuestBase):
    """Schema for returning an onboarding question from the API."""
    id: int  # DB primary key
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)