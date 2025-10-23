
from sqlalchemy import Column, ForeignKey, Integer, Numeric
from Database.Connection import Base
from sqlalchemy.orm import relationship


class OrderDetail(Base):
    __tablename__ = "OrdersDetails"
    
    OrderDetailID = Column(Integer, primary_key=True, index=True)
    OrderID = Column(Integer, ForeignKey("Orders.OrderID", ondelete="CASCADE"), nullable=False)
    ProductID = Column(Integer, ForeignKey("Products.ProductID"), nullable=False)
    Quantity = Column(Integer, nullable=False)
    UnitPrice = Column(Numeric(10, 2), nullable=False)
    
    order = relationship("Orders", back_populates="order_details")
    product = relationship("Products", back_populates="order_items")