from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text
from Database.Connection import Base
from datetime import datetime
from sqlalchemy.orm import relationship 

class AdviceHistory(Base): 
    __tablename__ = "AdviceHistory"
    
    AdviceHistoryID = Column(Integer, primary_key=True, index=True)
    UserID = Column(Integer, ForeignKey("Users.UserID"), nullable=False)
    UserQuery= Column(Text, nullable=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("Users", back_populates="advice_history")