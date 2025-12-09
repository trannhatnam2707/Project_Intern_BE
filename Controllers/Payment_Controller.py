import stripe
import os
from fastapi import HTTPException
from sqlalchemy.orm import Session
from Models.Order_Model import Order
from Models.Products_Model import Product
from Models.OrderDetail_Model import OrderDetail
from Models.Payment_Model import Payment 
from datetime import datetime            
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
FRONTEND_DOMAIN = os.getenv("FRONTEND_URL", "http://localhost:5173")

def create_checkout_session(db: Session, order_id: int):
    # ... (Phần code tạo session này giữ nguyên như cũ) ...
    # Để tiết kiệm diện tích tôi không paste lại đoạn tạo session, 
    # bạn giữ nguyên logic tạo session, chỉ lưu ý phần images: [] để tránh lỗi
    
    # --- Code cũ ---
    order = db.query(Order).filter(Order.OrderID == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    line_items = []
    order_details = db.query(OrderDetail).filter(OrderDetail.OrderID == order_id).all()
    
    for detail in order_details:
        product = db.query(Product).filter(Product.ProductID == detail.ProductID).first()
        
        line_items.append({
            'price_data': {
                'currency': 'vnd',
                'product_data': {
                    'name': product.ProductName,
                    'images': [], # Để rỗng để tránh lỗi ảnh localhost
                },
                'unit_amount': int(detail.UnitPrice), 
            },
            'quantity': detail.Quantity,
        })

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f'{FRONTEND_DOMAIN}/payment/success?order_id={order_id}',
            cancel_url=f'{FRONTEND_DOMAIN}/payment/cancel',
            metadata={
                "order_id": order_id
            }
        )
        return {"checkout_url": checkout_session.url}
    except Exception as e:
        print(f"Stripe Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    # --- Hết phần code cũ ---


# 👇 SỬA LẠI HÀM NÀY ĐỂ LƯU PAYMENT
def confirm_payment_success(db: Session, order_id: int):
    # 1. Tìm đơn hàng
    order = db.query(Order).filter(Order.OrderID == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # 2. Cập nhật trạng thái Order
    order.Status = "Paid" 
    
    # 3. 👇 TĂNG SỐ LƯỢNG ĐÃ BÁN (SOLD) CHO SẢN PHẨM
    # Lấy chi tiết đơn hàng
    order_details = db.query(OrderDetail).filter(OrderDetail.OrderID == order_id).all()
    for detail in order_details:
        product = db.query(Product).filter(Product.ProductID == detail.ProductID).first()
        if product:
            product.Sold = (product.Sold or 0) + detail.Quantity
            # product.Stock -= detail.Quantity (Nếu muốn trừ kho ở đây luôn cũng được)

    # 4. Lưu Payment (Giữ nguyên logic cũ của bạn)
    # ... (đoạn code lưu Payment giữ nguyên)

    db.commit()
    return {"message": "Thanh toán thành công"}