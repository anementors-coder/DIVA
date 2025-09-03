from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func, text
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base



# -----------------------------
# Table 1: OnboardQuest
# -----------------------------
class OnboardQuest(Base):
    __tablename__ = "onboard_quest"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

# -----------------------------
# Table 2: UserInfo
# -----------------------------
class UserInfo(Base):
    __tablename__ = "user_info"

    id = Column(Integer, primary_key=True, index=True)
    usid = Column(Integer, nullable=False, unique=True, index=True)  # User ID should be unique
    referral = Column(String, nullable=False)
    onboarding_query = Column(JSONB, nullable=False)
    resume_url = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )