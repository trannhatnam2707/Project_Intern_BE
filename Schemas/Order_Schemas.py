from datetime import datetime
from decimal import Decimal
from typing import List
from pydantic import BaseModel

#-------Chi tiết đơn hà ng--------#

class OrderDetailItem(BaseModel):
    productID: int
    Quantity: int
    UnitPrice: Decimal

    class Config:
       from_attributes = True

#-------Tạo đơn hàng--------#
class OrderCreate(BaseModel):
    UserID: int
    TotalAmount: Decimal
    order_details: List[OrderDetailItem]
    
#-------Thông tin đơn hàng trả về--------#
class OrderOut(BaseModel):
    OrderID: int
    UserID: int
    TotalAmount: Decimal
    Status: str 
    OrderDate: datetime
    order_details: List[OrderDetailItem]

    class Config:
        from_attributes = True