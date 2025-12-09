import stripe
import os
from fastapi import HTTPException
from sqlalchemy.orm import Session
from Models.Order_Model import Order
from Models.Products_Model import Product
from Models.OrderDetail_Model import OrderDetail 
from Models.Payment_Model import Payment
from dotenv import load_dotenv

load_dotenv()

# Cấu hình Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# 👇 Lấy FRONTEND_URL từ file .env
FRONTEND_DOMAIN = os.getenv("FRONTEND_URL", "http://localhost:5173")

def create_checkout_session(db: Session, order_id: int):
    # 1. Lấy thông tin đơn hàng
    order = db.query(Order).filter(Order.OrderID == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # 2. Tạo danh sách line_items cho Stripe
    line_items = []
    
    # Lấy chi tiết đơn hàng
    order_details = db.query(OrderDetail).filter(OrderDetail.OrderID == order_id).all()
    
    for detail in order_details:
        product = db.query(Product).filter(Product.ProductID == detail.ProductID).first()
        
        line_items.append({
            'price_data': {
                'currency': 'vnd',
                'product_data': {
                    'name': product.ProductName,
                    # 👇 QUAN TRỌNG: Để mảng rỗng [] để tránh lỗi URL ảnh "localhost"
                    'images': [], 
                },
                'unit_amount': int(detail.UnitPrice), 
            },
            'quantity': detail.Quantity,
        })

    # 3. Tạo phiên thanh toán (Session)
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            # URL chuyển hướng khi thành công/thất bại
            success_url=f'{FRONTEND_DOMAIN}/payment/success?order_id={order_id}',
            cancel_url=f'{FRONTEND_DOMAIN}/payment/cancel',
            metadata={
                "order_id": order_id
            }
        )

        return {"checkout_url": checkout_session.url}
    
    except Exception as e:
        print(f"Stripe Error: {str(e)}") # In lỗi ra terminal để debug
        raise HTTPException(status_code=400, detail=str(e))

def confirm_payment_success(db: Session, order_id: int):
    # 1. Tìm đơn hàng
    order = db.query(Order).filter(Order.OrderID == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # 2. Cập nhật trạng thái Order
    order.Status = "Paid" 
    
    # 3. 👇 Thêm logic lưu vào bảng Payment
    # Kiểm tra xem đã có payment cho order này chưa để tránh duplicate (nếu user reload trang success)
    existing_payment = db.query(Payment).filter(Payment.OrderID == order_id).first()
    
    if not existing_payment:
        new_payment = Payment(
            OrderID=order.OrderID,
            Amount=order.TotalAmount, # Lấy số tiền từ đơn hàng
            PaymentMethod="Stripe",
            PaymentStatus="Success",
            PaymentDate=datetime.utcnow(),
            # StripeSessionID="..." (Nếu bạn muốn lưu session ID thì cần truyền từ tham số vào, tạm thời để trống cũng được)
        )
        db.add(new_payment)

    db.commit()
    return {"message": "Payment confirmed"}