from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    # Add other user fields here later, like email, hashed_password, etc.
    email = Column(String, unique=True, index=True, nullable=False)
    
    user_info = relationship("UserInfo", back_populates="user", uselist=False)
