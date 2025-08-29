from sqlalchemy import Column, Integer, String

from app.db.base import Base
target_metadata = Base.metadata

# -----------------------------
# Table 1: OnboardQuest
# -----------------------------
class OnboardQuest(Base):
    __tablename__ = "onboard_quest"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False, unique=True)


# -----------------------------
# Table 2: UserInfo
# -----------------------------
class UserInfo(Base):
    __tablename__ = "user_info"

    usid = Column(Integer, primary_key=True, index=True)
    q1 = Column(String, nullable=False)
    q2 = Column(String, nullable=False)
    q3 = Column(String, nullable=False)
    q4 = Column(String, nullable=False)
    q5 = Column(String, nullable=False)
    q6 = Column(String, nullable=False)
    q7 = Column(String, nullable=False)
    resume_url = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)