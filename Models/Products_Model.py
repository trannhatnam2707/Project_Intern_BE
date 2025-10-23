
from datetime import datetime
from sqlalchemy.orm import relationship
from Database.Connection import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text


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

    category = relationship("Categories", back_populates="products")
    order_items = relationship("OrdersDetails", back_populates="product")