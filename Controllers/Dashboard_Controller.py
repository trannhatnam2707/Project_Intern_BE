from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from Models.Order_Model import Order
from Models.Users_Model import Users

def get_dashboard_stats(db: Session, time_range: str = 'month'):
    now = datetime.now()
    
    # 1. CHUẨN HÓA THỜI GIAN (Giữ nguyên như cũ)
    if time_range == 'day':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        previous_start = start_date - timedelta(days=1)
    elif time_range == 'week':
        start_date = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        previous_start = start_date - timedelta(days=7)
    else: 
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month = (start_date - timedelta(days=1)).replace(day=1)
        previous_start = last_month

    # 2. DANH SÁCH TRẠNG THÁI ĐƯỢC TÍNH DOANH THU
    # Pending = Chưa trả tiền (Không tính)
    # Cancelled = Đã hủy (Không tính)
    REVENUE_STATUSES = ['Paid', 'Shipping', 'Completed']

    # 3. QUERY DỮ LIỆU
    # Doanh thu hiện tại
    current_revenue = db.query(func.sum(Order.TotalAmount)).filter(
        Order.Status.in_(REVENUE_STATUSES), # 👈 Chỉ tính đơn đã trả tiền
        Order.OrderDate >= start_date
    ).scalar() or 0

    # Tổng số đơn (Đếm tất cả để biết traffic, trừ đơn hủy)
    total_orders = db.query(Order).filter(
        Order.OrderDate >= start_date,
        Order.Status != 'Cancelled'
    ).count()
    
    # Doanh thu kỳ trước
    prev_revenue = db.query(func.sum(Order.TotalAmount)).filter(
        Order.Status.in_(REVENUE_STATUSES),
        Order.OrderDate >= previous_start,
        Order.OrderDate < start_date
    ).scalar() or 0

    # Tăng trưởng
    growth = 0
    if prev_revenue > 0:
        growth = ((current_revenue - prev_revenue) / prev_revenue) * 100
    else:
        growth = 100 if current_revenue > 0 else 0

    total_users = db.query(Users).filter(Users.Role != 'admin').count()
    
    # AOV (Chỉ tính trên số đơn sinh ra tiền)
    paid_orders_count = db.query(Order).filter(
        Order.Status.in_(REVENUE_STATUSES),
        Order.OrderDate >= start_date
    ).count()
    avg_order_value = current_revenue / paid_orders_count if paid_orders_count > 0 else 0

    # 4. BIỂU ĐỒ
    chart_data = []
    raw_orders = db.query(Order).filter(
        Order.OrderDate >= start_date, 
        Order.Status.in_(REVENUE_STATUSES) # 👈 Chỉ vẽ đơn đã trả tiền
    ).all()

    date_map = {}
    if time_range == 'day':
        for i in range(24): date_map[i] = 0
        for o in raw_orders: date_map[o.OrderDate.hour] += float(o.TotalAmount)
        chart_data = [{"name": f"{k}h", "value": v} for k, v in date_map.items()]
    else: 
        temp = start_date
        while temp <= now:
            k = temp.strftime("%d/%m")
            date_map[k] = 0
            temp += timedelta(days=1)
        for o in raw_orders:
            k = o.OrderDate.strftime("%d/%m")
            if k in date_map: date_map[k] += float(o.TotalAmount)
        chart_data = [{"name": k, "value": v} for k, v in date_map.items()]

    return {
        "revenue": float(current_revenue),
        "growth": round(growth, 1),
        "totalOrders": total_orders,
        "totalUsers": total_users,
        "avgOrderValue": float(avg_order_value),
        "chartData": chart_data
    }