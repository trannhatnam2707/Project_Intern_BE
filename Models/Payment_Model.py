from Database.Connection import Base
from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime


class Payment(Base):
    __tablename__ = "Payments"
    
    PaymentID = Column(Integer, primary_key=True, index=True)
    OrderID = Column(Integer, ForeignKey("Orders.OrderID", ondelete="CASCADE"), nullable=False)
    Amount = Column(Numeric(10, 2), nullable=False)
    PaymentMethod = Column(String(50), nullable="Stripe")
    PaymentStatus = Column(String(20), default="Success")
    PaymentDate = Column(DateTime, default=datetime.utcnow)
    StripeSessionID = Column(String(255))
    
    order = relationship("Orders", back_populates="payments")