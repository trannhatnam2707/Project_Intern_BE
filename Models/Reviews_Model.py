from sqlalchemy import Column, Integer, UnicodeText, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from Database.Connection import Base

class Reviews(Base):
    __tablename__ = "Reviews"

    ReviewID = Column(Integer, primary_key=True, index=True)
    UserID = Column(Integer, ForeignKey("Users.UserID"), nullable=False)
    ProductID = Column(Integer, ForeignKey("Products.ProductID"), nullable=False)
    Rating = Column(Integer, nullable=False)
    Comment = Column(UnicodeText, nullable=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    user = relationship("Users", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")