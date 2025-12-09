from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List 
from Database.Connection import get_db
from Schemas.Order_Schemas import OrderCreate, OrderOut 
from Controllers.Order_Controller import (
    create_order,
    get_my_orders,
    get_all_orders,
    get_order_detail,
    update_order_status,
    delete_order
)
from Utils.Dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api/orders", tags=["Orders"])

# User: Tạo đơn hàng
# Không để response_model=OrderOut vì controller trả về message {"message": "...", "order_id": ...}
@router.post("/")
def create_new_order(
    order_data: OrderCreate, 
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    return create_order(db, current_user.UserID, order_data)

# User: Xem đơn hàng của chính mình
# Thêm response_model để format dữ liệu đầu ra chuẩn đẹp
@router.get("/my", response_model=List[OrderOut]) 
def get_user_orders(
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    return get_my_orders(db, current_user.UserID)

# Admin: Xem tất cả đơn hàng
@router.get("/", dependencies=[Depends(require_admin)], response_model=List[OrderOut])
def get_all_orders_admin(db: Session = Depends(get_db)):
    return get_all_orders(db)

# Admin: Xem chi tiết đơn hàng
@router.get("/{order_id}", dependencies=[Depends(require_admin)], response_model=OrderOut)
def get_order_detail_admin(order_id: int, db: Session = Depends(get_db)):
    return get_order_detail(db, order_id, is_admin=True)

# Admin: Cập nhật trạng thái đơn hàng
@router.put("/{order_id}/{status}", dependencies=[Depends(require_admin)])
def update_order_status_admin(order_id: int, status: str, db: Session = Depends(get_db)):
    return update_order_status(db, order_id, status)

# Admin: Xóa đơn hàng
@router.delete("/{order_id}", dependencies=[Depends(require_admin)])
def delete_order_admin(order_id: int, db: Session = Depends(get_db)):
    return delete_order(db, order_id)