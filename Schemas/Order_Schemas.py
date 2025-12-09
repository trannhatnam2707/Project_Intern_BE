from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel

# ==========================================
# PHẦN 1: DÙNG ĐỂ TẠO ĐƠN HÀNG (FE gửi lên)
# ==========================================

# Item user chọn mua (Chỉ cần ID và số lượng)
class OrderItemRequest(BaseModel):
    product_id: int
    quantity: int

# Body gửi lên API (Không cần UserID, không cần giá)
class OrderCreate(BaseModel):
    items: List[OrderItemRequest]

# ==========================================
# PHẦN 2: DÙNG ĐỂ TRẢ VỀ (BE trả về)
# ==========================================

# Chi tiết từng dòng trong đơn hàng (khi xem lại mới cần giá)
class OrderDetailOut(BaseModel):
    ProductID: int
    # ProductName: str # (Có thể thêm nếu muốn join bảng)
    Quantity: int
    UnitPrice: Decimal

    class Config:
        from_attributes = True

# Thông tin tổng quan đơn hàng
class OrderOut(BaseModel):
    OrderID: int
    UserID: int
    TotalAmount: Decimal
    Status: str 
    OrderDate: datetime
    order_details: List[OrderDetailOut] = [] # (Optional: Nếu muốn trả về luôn chi tiết)

    class Config:
        from_attributes = True