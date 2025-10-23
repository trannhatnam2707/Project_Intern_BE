from pydantic import BaseModel
from typing import List

class TopProduct(BaseModel):
    ProductName: str
    Quantity: int

class RecentPayment(BaseModel):
    OrderID: int
    Amount: float
    PaymentDate: str

class UserGrowth(BaseModel):
    month: str
    count: int

class OrderStatusSummary(BaseModel):
    status: str
    count: int

class DashboardStats(BaseModel):
    total_users: int
    total_orders: int
    total_revenue: float
    top_products: List[TopProduct]
    recent_payments: List[RecentPayment]
    user_growth: List[UserGrowth]
    order_status_summary: List[OrderStatusSummary]

    class Config:
        from_attributes = True
