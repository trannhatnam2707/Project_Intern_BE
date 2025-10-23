from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel

#---------Request----------#
class ProductCreate(BaseModel):
    CategoryID: Optional[int] = None
    ProductName: str
    Price: Decimal
    Description: Optional[str] = None
    ImageURL: Optional[str] = None
    Stock: Optional[int] = 0
    
#---------Response----------#
class ProductOut(BaseModel):
    ProductID: int
    ProductName: str
    Price: Decimal
    Description: Optional[str] = None
    ImageURL: Optional[str] = None
    Stock: int
    CategoryID: Optional[int] 
    CreateAt: datetime

    class Config:
        from_attributes = True