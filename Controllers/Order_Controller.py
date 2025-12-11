from http.client import HTTPException
from Models.OrderDetail_Model import OrderDetail
from Models.Order_Model import Order
from Models.Products_Model import Product
from Schemas.Order_Schemas import OrderCreate
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from Models.Users_Model import Users

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
def get_all_orders(db: Session, page: int = 1, limit: int = 10, search: str = None, status: str = None):
    # 1. Query có Join với bảng Users để lấy FullName
    # Dùng outerjoin để lỡ user bị xóa thì đơn hàng vẫn hiện (tên sẽ là None)
    query = db.query(Order, Users.FullName).outerjoin(Users, Order.UserID == Users.UserID)

    # 2. Lọc theo trạng thái
    if status and status != 'all':
        query = query.filter(Order.Status == status)

    # 3. Tìm kiếm
    if search:
        if search.isdigit():
             # Nếu là số -> Tìm theo Mã đơn
             query = query.filter(Order.OrderID == int(search))
        else:
             # Nếu là chữ -> Tìm theo Tên khách hàng
             query = query.filter(Users.FullName.like(f"%{search}%"))
    
    # 4. Sắp xếp mới nhất
    query = query.order_by(desc(Order.OrderDate))

    # 5. Phân trang
    total_records = query.count()
    skip = (page - 1) * limit
    results = query.offset(skip).limit(limit).all()

    # 6. Map dữ liệu trả về (Kết hợp thông tin Order + Tên User)
    final_data = []
    for order_obj, user_name in results:
        final_data.append({
            "OrderID": order_obj.OrderID,
            "UserID": order_obj.UserID,
            "OrderDate": order_obj.OrderDate,
            "TotalAmount": order_obj.TotalAmount,
            "Status": order_obj.Status,
            "UserName": user_name if user_name else "Khách vãng lai" # 👈 Trường mới
        })

    return {
        "data": final_data,
        "total": total_records,
        "page": page,
        "limit": limit
    }

#--------------Hủy đơn phía user------------#
def cancel_order_by_user(db: Session, order_id: int, user_id: int):
    # 1. Tìm đơn hàng của đúng user đó
    order = db.query(Order).filter(Order.OrderID == order_id, Order.UserID == user_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
        
    # 2. Chỉ cho phép hủy nếu đơn còn Pending (Chưa thanh toán/Chưa xử lý)
    if order.Status != 'Pending':
        raise HTTPException(status_code=400, detail="Không thể hủy đơn hàng đã thanh toán hoặc đang giao.")
    
    # 3. Cập nhật trạng thái
    order.Status = 'Cancelled'
    
    # 4. HOÀN LẠI TỒN KHO (Quan trọng)
    # Lấy danh sách sản phẩm trong đơn đó để cộng lại vào kho
    details = db.query(OrderDetail).filter(OrderDetail.OrderID == order_id).all()
    for item in details:
        product = db.query(Product).filter(Product.ProductID == item.ProductID).first()
        if product:
            product.Stock += item.Quantity
            
    db.commit()
    return {"message": "Đã hủy đơn hàng thành công"}

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