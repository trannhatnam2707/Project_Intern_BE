from pydantic import BaseModel
from typing import Optional, Any

# Cấu trúc dữ liệu sản phẩm cần đồng bộ
class ProductSyncData(BaseModel):
    ProductID: int
    ProductName: str
    Description: Optional[str] = ""
    MarketingContent : Optional[str]
    Price: float
    Stock: int
    CategoryID: Optional[int] = None
    ImageURL: Optional[str] = ""

# Cấu trúc Payload gửi lên (Action + Data)
class PineconePayload(BaseModel):
    action: str  # "UPSERT" hoặc "DELETE"
    id: int      # ProductID
    data: Optional[ProductSyncData] = None