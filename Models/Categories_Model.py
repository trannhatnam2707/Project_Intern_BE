from sqlalchemy import Column, Integer, String
from Database.Connection import Base
from sqlalchemy.orm import relationship


class Category(Base):
    __tablename__ = "Categories"
    
    CategoryID = Column(Integer, primary_key=True, index=True)
    CategoryName = Column(String(100), unique=True, nullable=False)
    
    products = relationship("Products", back_populates="category")