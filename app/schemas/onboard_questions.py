from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

# =============================
# Schemas for OnboardQuest
# =============================

class OnboardQuestBase(BaseModel):
    """Base schema for an onboarding question."""
    question_id: int = Field(..., ge=1, description="A stable identifier for the question, shared across versions")
    title: str = Field(..., min_length=1, max_length=500, description="The question text presented to the user")
    description: Optional[str] = Field(None, max_length=2000, description="Additional context or help text for the question")
    icon: Optional[str] = Field(None, max_length=50, description="An identifier for a frontend icon")


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
    id: int # The primary key from the database
    created_at: datetime

    # Pydantic V2 configuration to read data from ORM models
    model_config = ConfigDict(from_attributes=True)