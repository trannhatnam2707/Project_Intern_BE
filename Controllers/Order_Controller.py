from http.client import HTTPException
from Models.OrderDetail_Model import OrderDetail
from Models.Order_Model import Order
from Models.Products_Model import Product
from Schemas.Order_Schemas import OrderCreate
from sqlalchemy.orm import Session

#------tạo đơn hàng mới------#
def create_order(db: Session, user_id: int, order_data: OrderCreate):
    total_amount = 0
    new_order_details = []
    
    for item in order_data.items:
        product = db.query(Product).filter(Product.ProductID == item.product_id).first()
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Sản phẩm ID {item.product_id} không tồn tại")
        
        if product.Stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Sản phẩm '{product.ProductName}' không đủ hàng (Còn: {product.Stock})")
        
        # Tính tiền: Giá DB * Số lượng
        price = product.Price
        line_total = price * item.quantity
        total_amount += line_total
          
        # Trừ tồn kho
        product.Stock -= item.quantity
        
        # Tạo đối tượng chi tiết (chưa lưu)
        new_detail = OrderDetail(
            ProductID=product.ProductID,
            Quantity=item.quantity,
            UnitPrice=price
        )
        new_order_details.append(new_detail)

    # 2. Tạo đơn hàng chính (Master)
    new_order = Order(
        UserID=user_id,          # Lấy từ Token
        TotalAmount=total_amount, # Tính toán ở trên
        Status="Pending"
    )
    
    db.add(new_order)
    db.flush() # Để lấy được new_order.OrderID ngay lập tức

    # 3. Lưu các chi tiết đơn hàng
    for detail in new_order_details:
        detail.OrderID = new_order.OrderID
        db.add(detail)
    
    db.commit()
    db.refresh(new_order)
    
    return {"message": "Tạo đơn hàng thành công", "order_id": new_order.OrderID}

#------User xem đơn hàng------#
def get_my_orders(db: Session, user_id: int):
    orders = db.query(Order).filter(Order.UserID == user_id).all()
    if not orders:
        raise HTTPException(status_code=404, detail="Bạn chưa có đơn hàng nào")
    return orders   

#------Admin xem tất cả đơn hàng------#
def get_all_orders(db: Session):
    orders = db.query(Order).all()
    if not orders:
        raise HTTPException(status_code=404, detail="Chưa có đơn hàng nào")
    return orders

#------Xem chi tiết đơn hàng------#
def get_order_detail(db: Session, order_id: int, user_id: int = None, is_admin: bool = False):
    order = (
        db.query(Order)
        .filter(Order.OrderID == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
    
    if not is_admin and order.UserID != user_id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem đơn hàng này")
    
    return order
# def get_order_detail(db: Session, order_id: int, user_id: int = None, is_admin: bool = False):
#     order = (
#         db.query(Order)
#         .filter(Order.OrderID == order_id)
#         .first()
#     )
#     if not order:
#         raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
    
#     if not is_admin and order.UserID != user_id:
#         raise HTTPException(status_code=403, detail="Bạn không có quyền xem đơn hàng này")
    
#     return {
#         "OrderID": order.OrderID,
#         "UserID": order.UserID,
#         "Status": order.Status,
#         "TotalAmount": float(order.TotalAmount),
#         "CreatedAt": order.CreatedAt,
#         "Details": [
#             {
#                 "ProductName": detail.product.ProductName,
#                 "Quantity": detail.Quantity,
#                 "UnitPrice": float(detail.UnitPrice),
#                 "Total": float(detail.UnitPrice) * detail.Quantity
#             }
#             for detail in order.order_details
#         ]
#     }

#------Cập nhật trạng thái đơn hàng (Admin)------#
def update_order_status(db: Session, order_id: int, new_status: str):
    order = db.query(Order).filter(Order.OrderID == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
    
    order.Status = new_status
    db.commit()
    db.refresh(order)
    return {"message": f"Đã cập nhật trạng thái đơn hàng {order_id} thành {new_status}"}

#------Xoá đơn hàng (Admin)------#
def delete_order(db: Session, order_id: int):
    order = db.query(Order).filter(Order.OrderID == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
    
    db.delete(order)
    db.commit()
    return {"message": f"Đã xoá đơn hàng {order_id} thành công"}