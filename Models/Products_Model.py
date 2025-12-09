# Models/Product_Model.py
from datetime import datetime
from sqlalchemy import Column, Integer, Unicode, Numeric, UnicodeText, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from Database.Connection import Base

class Product(Base):
    __tablename__ = "Products"

    ProductID = Column(Integer, primary_key=True, index=True)
    CategoryID = Column(Integer, ForeignKey("Categories.CategoryID", ondelete="SET NULL"), nullable=False)
    ProductName = Column(Unicode(250), nullable=False)
    Price = Column(Numeric(10, 2), nullable=False)
    Description = Column(UnicodeText)
    MarketingContent = Column(UnicodeText, nullable=True) # Nội dung marketing (sau này AI sinh)
    ImageURL = Column(Unicode(250))
    Stock = Column(Integer, default=0)
    Sold = Column(Integer, default=0)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="products")
    reviews = relationship("Reviews", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderDetail", back_populates="product", cascade="all, delete-orphan")
