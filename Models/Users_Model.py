from datetime import datetime
from sqlalchemy import Column, Integer, String,DateTime
from Database.Connection import Base
from sqlalchemy.orm import relationship


class Users(Base):
    __tablename__ = "Users"
    
    UserID = Column(Integer, primary_key=True, index=True)
    FullName = Column(String(100), nullable=False)
    Email = Column(String(100), unique=True, nullable=False)
    Password = Column(String(255), nullable=False)
    Role = Column(String(50), nullable=False, default="user")
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    
    
    
    from Models.AdviceHistory_Model import AdviceHistory
    advice_history = relationship("AdviceHistory", back_populates="user", cascade="all, delete")