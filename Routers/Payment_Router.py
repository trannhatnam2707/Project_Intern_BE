from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from Database.Connection import get_db
from Utils.Dependencies import get_current_user
from Controllers.Payment_Controller import create_checkout_session, confirm_payment_success

router = APIRouter(prefix="/api/payment", tags=["Payment"])

# API tạo link thanh toán (User gọi sau khi tạo đơn hàng)
@router.post("/create-checkout-session/{order_id}")
def create_payment_link(order_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Có thể thêm check: Order này có phải của current_user không?
    return create_checkout_session(db, order_id)

# API xác nhận thanh toán thành công (Gọi từ trang Success của FE)
@router.put("/success/{order_id}")
def payment_success(order_id: int, db: Session = Depends(get_db)):
    # Lưu ý: Thực tế nên dùng Webhook để bảo mật hơn, 
    # nhưng với dự án intern, gọi API này từ trang Success là chấp nhận được.
    return confirm_payment_success(db, order_id)