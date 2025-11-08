# Models/Category_Model.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from Database.Connection import Base

class Category(Base):
    __tablename__ = "Categories"
    
    CategoryID = Column(Integer, primary_key=True, index=True)
    CategoryName = Column(String(100), unique=True, nullable=False)
    
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")
