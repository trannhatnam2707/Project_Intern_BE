# Models/Product_Model.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from Database.Connection import Base

class Product(Base):
    __tablename__ = "Products"

    ProductID = Column(Integer, primary_key=True, index=True)
    CategoryID = Column(Integer, ForeignKey("Categories.CategoryID", ondelete="SET NULL"), nullable=False)
    ProductName = Column(String(250), nullable=False)
    Price = Column(Numeric(10, 2), nullable=False)
    Description = Column(Text)
    Image = Column(String(250))
    Stock = Column(Integer, default=0)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="products")

    order_items = relationship("OrderDetail", back_populates="product", cascade="all, delete-orphan")
