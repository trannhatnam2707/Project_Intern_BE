from datetime import datetime
from decimal import Decimal
from typing import Optional,List
from pydantic import BaseModel

#---------Request----------#
class ProductCreate(BaseModel):
    CategoryID: Optional[int] = None
    ProductName: str
    Price: Decimal
    Description: Optional[str] = None
    MarketingContent: Optional[str] = None
    ImageURL: Optional[str] = None
    Stock: Optional[int] = 0
    
#---------Response----------#
class ProductOut(BaseModel):
    ProductID: int
    ProductName: str
    Price: Decimal
    Description: Optional[str] = None
    MarketingContent: Optional[str] = None
    ImageURL: Optional[str] = None
    Stock: int
    Sold: Optional[int] = 0
    CategoryID: Optional[int] 
    CreatedAt: datetime

    class Config:
        from_attributes = True

# THÊM CLASS NÀY CHO PHÂN TRANG
class ProductListResponse(BaseModel):
    data: List[ProductOut]
    total: int
    page: int
    limit: int