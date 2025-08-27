from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class OnboardingQuestionnaire(Base):
    __tablename__ = "onboarding_questionnaire"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False, index=True)

class UserInfo(Base):
    __tablename__ = "user_info"

    usid = Column(Integer, primary_key=True, index=True)
    q1 = Column(String, nullable=True)
    q2 = Column(String, nullable=True)
    q3 = Column(String, nullable=True)
    q4 = Column(String, nullable=True)
    q5 = Column(String, nullable=True)
    q6 = Column(String, nullable=True)
    q7 = Column(String, nullable=True)
    resume_url = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="user_info")
