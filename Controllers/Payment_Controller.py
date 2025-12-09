import stripe
import os
from fastapi import HTTPException
from sqlalchemy.orm import Session
from Models.Order_Model import Order
from Models.Products_Model import Product

# Cấu hình Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
FRONTEND_DOMAIN = os.getenv("DOMAIN", "http://localhost:5173")

def create_checkout_session(db: Session, order_id: int):
    # 1. Lấy thông tin đơn hàng
    order = db.query(Order).filter(Order.OrderID == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # 2. Tạo danh sách line_items cho Stripe
    line_items = []
    
    # Lấy chi tiết đơn hàng (Join bảng OrderDetails và Products)
    # Lưu ý: Cần chắc chắn bạn đã cấu hình relationship trong Model Order -> OrderDetails
    for detail in order.order_details: 
        product = db.query(Product).filter(Product.ProductID == detail.ProductID).first()
        
        line_items.append({
            'price_data': {
                'currency': 'vnd',
                'product_data': {
                    'name': product.ProductName,
                    'images': [product.ImageURL] if product.ImageURL else [],
                },
                'unit_amount': int(detail.UnitPrice), # Stripe tính tiền theo đơn vị nhỏ nhất (VND là đồng)
            },
            'quantity': detail.Quantity,
        })

    # 3. Tạo phiên thanh toán (Session)
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            # URL khi thanh toán thành công (kèm order_id để FE xử lý)
            success_url=f'{FRONTEND_DOMAIN}/payment/success?order_id={order_id}',
            # URL khi hủy thanh toán
            cancel_url=f'{FRONTEND_DOMAIN}/payment/cancel',
            metadata={
                "order_id": order_id
            }
        )
        
        # Cập nhật Stripe Session ID vào đơn hàng (nếu muốn lưu lại đối chiếu)
        # order.StripeSessionID = checkout_session.id
        # db.commit()

        return {"checkout_url": checkout_session.url}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def confirm_payment_success(db: Session, order_id: int):
    order = db.query(Order).filter(Order.OrderID == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.Status = "Paid" # Cập nhật trạng thái đã thanh toán
    db.commit()
    return {"message": "Payment confirmed"}