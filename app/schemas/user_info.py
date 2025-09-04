# app/schemas/user_info.py
from pydantic import BaseModel, HttpUrl, Field, ConfigDict, field_validator, model_validator
from typing import Optional, Dict, Any
from datetime import datetime
from app.utils.api_utils import validate_linkedin_url, normalize_linkedin_url


class UserInfoBase(BaseModel):
    """Base schema for user's onboarding information."""
    referral: str = Field(..., min_length=1, max_length=100, description="The source of user referral")
    onboarding_query: Dict[str, Any] = Field(..., description="User answers to onboarding questions")
    linkedin_url: Optional[str] = Field(None, description="URL to the user's LinkedIn profile")

    @field_validator('onboarding_query')
    @classmethod
    def validate_onboarding_query(cls, v: Dict) -> Dict:
        if not v:
            raise ValueError('onboarding_query cannot be an empty dictionary')
        return v

    @field_validator('referral')
    @classmethod
    def validate_referral(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('referral cannot be empty')
        return v.strip()

    # Normalize and validate LinkedIn before final parsing
    @field_validator('linkedin_url', mode='before')
    @classmethod
    def normalize_linkedin(cls, v: Optional[str]) -> Optional[str]:
        if v is None or (isinstance(v, str) and not v.strip()):
            return v
        normalized = normalize_linkedin_url(str(v))
        if not normalized:
            raise ValueError('Invalid LinkedIn URL format. Must be a profile URL (e.g., linkedin.com/in/...).')
        return normalized

    # Optionally keep a post-validator if you want an extra safety net
    @field_validator('linkedin_url')
    @classmethod
    def validate_linkedin(cls, v: Optional[str]) -> Optional[str]:
        if v and not validate_linkedin_url(v):
            raise ValueError('Invalid LinkedIn URL format')
        return v


class UserInfoCreate(UserInfoBase):
    """Schema for creating a new user info record."""
    pass


class UserInfoUpdate(BaseModel):
    """Schema for updating an existing user info record."""
    referral: Optional[str] = Field(None, min_length=1, max_length=100)
    onboarding_query: Optional[Dict[str, Any]] = None
    resume_url: Optional[str] = None
    linkedin_url: Optional[str] = None

    @field_validator('onboarding_query')
    @classmethod
    def validate_onboarding_query(cls, v: Optional[Dict]) -> Optional[Dict]:
        if v is not None and not v:
            raise ValueError('onboarding_query cannot be an empty dictionary')
        return v

    @field_validator('referral')
    @classmethod
    def validate_referral(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('referral cannot be empty')
        return v.strip() if v else v

    @field_validator('linkedin_url', mode='before')
    @classmethod
    def normalize_linkedin(cls, v: Optional[str]) -> Optional[str]:
        if v is None or (isinstance(v, str) and not v.strip()):
            return v
        normalized = normalize_linkedin_url(str(v))
        if not normalized:
            raise ValueError('Invalid LinkedIn URL format. Must be a profile URL (e.g., linkedin.com/in/...).')
        return normalized

    @field_validator('linkedin_url')
    @classmethod
    def validate_linkedin(cls, v: Optional[str]) -> Optional[str]:
        if v and not validate_linkedin_url(v):
            raise ValueError('Invalid LinkedIn URL format')
        return v


class UserInfoRead(UserInfoBase):
    """Schema for returning a user info record from the API."""
    id: int
    usid: int
    resume_url: Optional[str] = Field(None, description="URL to the user's resume")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class URLUpdate(BaseModel):
    """Schema for updating only the resume or LinkedIn URLs."""
    resume_url: Optional[str] = Field(None, description="URL to the user's resume")
    linkedin_url: Optional[str] = Field(None, description="URL to the user's LinkedIn profile")

    @model_validator(mode='after')
    def check_at_least_one_url_provided(self) -> 'URLUpdate':
        if not self.resume_url and not self.linkedin_url:
            raise ValueError('At least one of resume_url or linkedin_url must be provided.')
        return self

    @field_validator('linkedin_url', mode='before')
    @classmethod
    def normalize_linkedin(cls, v: Optional[str]) -> Optional[str]:
        if v is None or (isinstance(v, str) and not v.strip()):
            return v
        normalized = normalize_linkedin_url(str(v))
        if not normalized:
            raise ValueError('Invalid LinkedIn URL format')
        return normalized

    @field_validator('linkedin_url')
    @classmethod
    def validate_linkedin(cls, v: Optional[str]) -> Optional[str]:
        if v and not validate_linkedin_url(v):
            raise ValueError('Invalid LinkedIn URL format')
        return v


class ResumeURLUpdate(BaseModel):
    resume_url: HttpUrl


class LinkedInURLUpdate(BaseModel):
    linkedin_url: HttpUrl

    @field_validator('linkedin_url', mode='before')
    @classmethod
    def normalize_linkedin(cls, v):
        if v is None:
            return v
        normalized = normalize_linkedin_url(str(v))
        if not normalized:
            raise ValueError('Invalid LinkedIn URL format. Must be a profile URL (e.g., linkedin.com/in/...).')
        return normalized

    @field_validator('linkedin_url')
    @classmethod
    def validate_linkedin(cls, v: HttpUrl) -> HttpUrl:
        if v and not validate_linkedin_url(str(v)):
            raise ValueError('Invalid LinkedIn URL format. Must be a profile URL (e.g., linkedin.com/in/...).')
        return v


class ResumeDownloadURL(BaseModel):
    """Schema for returning a secure, temporary download URL for a resume."""
    download_url: str = Field(..., description="The presigned URL to download the resume.")
    expires_in_seconds: int = Field(..., description="The number of seconds the URL is valid for.")