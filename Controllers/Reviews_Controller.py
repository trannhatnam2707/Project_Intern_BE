from sqlalchemy.orm import Session
from Models.Reviews_Model import Reviews
from Models.Users_Model import Users
from Schemas.Reviews_Schemas import ReviewCreate
from fastapi import HTTPException

# Tạo đánh giá mới
def create_reviews(db: Session, user_id: int, product_id: int, review_data: ReviewCreate):
    # Kiểm tra xem user đã đánh giá sản phẩm này chưa (nếu muốn mỗi người chỉ đánh giá 1 lần)
    # existing_review = db.query(Review).filter(Review.UserID == user_id, Review.ProductID == product_id).first()
    # if existing_review:
    #     raise HTTPException(status_code=400, detail="Bạn đã đánh giá sản phẩm này rồi")

    new_review = Reviews(
        UserID=user_id,
        ProductID=product_id,
        Rating=review_data.Rating,
        Comment=review_data.Comment
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

# Lấy danh sách đánh giá của 1 sản phẩm
def get_product_reviews(db: Session, product_id: int):
    # Join bảng Review với Users để lấy FullName
    results = db.query(Reviews, Users.FullName)\
        .join(Users, Reviews.UserID == Users.UserID)\
        .filter(Reviews.ProductID == product_id)\
        .order_by(Reviews.CreatedAt.desc())\
        .all()
    
    # Format lại dữ liệu trả về cho đúng Schema ReviewOut
    reviews_list = []
    for review, full_name in results:
        reviews_list.append({
            "ReviewID": review.ReviewID,
            "UserID": review.UserID,
            "FullName": full_name,
            "Rating": review.Rating,
            "Comment": review.Comment,
            "CreatedAt": review.CreatedAt
        })
    return reviews_list