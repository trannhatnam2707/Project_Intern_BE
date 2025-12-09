from datetime import datetime
from sqlalchemy import Column, Integer, Unicode,DateTime
from Database.Connection import Base
from sqlalchemy.orm import relationship


class Users(Base):
    __tablename__ = "Users"
    
    UserID = Column(Integer, primary_key=True, index=True)
    FullName = Column(Unicode(100), nullable=False)
    Email = Column(Unicode(100), unique=True, nullable=False)
    Password = Column(Unicode(255), nullable=False)
    PhoneNumber = Column(Unicode(20), nullable=True)
    Address = Column(Unicode(500), nullable=True)
    Role = Column(Unicode(50), nullable=False, default="user")
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    
    
    
    advice_history = relationship("AdviceHistory", back_populates="user", cascade="all, delete")
    orders = relationship("Order", back_populates="user", cascade="all, delete")
    reviews = relationship("Reviews", back_populates="user", cascade="all, delete")