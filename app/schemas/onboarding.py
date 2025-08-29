from pydantic import BaseModel, HttpUrl
from typing import Optional, List

# -----------------------------
# Schema for OnboardQuest
# -----------------------------
class OnboardQuestRead(BaseModel):
    id: int
    question: str

    class Config:
        from_attributes = True


# -----------------------------
# Schemas for UserInfo
# -----------------------------
class UserInfoBase(BaseModel):
    q1: str
    q2: str
    q3: str
    q4: str
    q5: str
    q6: str
    q7: str
    resume_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None


class UserInfoCreate(UserInfoBase):
    usid: int  # user id decoded from JWT


class UserInfoRead(UserInfoBase):
    usid: int

    class Config:
        from_attributes = True


class UserInfoUpdate(BaseModel):
    q1: Optional[str] = None
    q2: Optional[str] = None
    q3: Optional[str] = None
    q4: Optional[str] = None
    q5: Optional[str] = None
    q6: Optional[str] = None
    q7: Optional[str] = None
    resume_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None