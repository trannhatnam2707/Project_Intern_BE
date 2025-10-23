from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from Database.Connection import Base
from sqlalchemy.orm import relationship


class Order(Base):
    __tablename__ = "Orders"
    
    OrderID = Column(Integer, primary_key=True, index=True)
    UserID = Column(Integer, ForeignKey("Users.UserID"), nullable=False)
    OrderDate = Column(DateTime, default=datetime.utcnow)
    TotalAmount = Column(Numeric(10, 2), nullable=False)
    Status = Column(String(20), default="Pending")
    
    
    user = relationship("Users", back_populates="orders")
    order_details = relationship("OrdersDetails", back_populates="order", cascade="all, delete")
    payments = relationship("Payments", back_populates="order", cascade="all, delete")