from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from Database.Connection import get_db
from Schemas.Reviews_Schemas import ReviewCreate, ReviewOut
from Controllers.Reviews_Controller import create_reviews, get_product_reviews
from Utils.Dependencies import get_current_user

router = APIRouter(
    prefix="/api/reviews",
    tags=["Reviews"]
)

# Lấy danh sách review của sản phẩm
@router.get("/{product_id}", response_model=List[ReviewOut])
def get_reviews(product_id: int, db: Session = Depends(get_db)):
    return get_product_reviews(db, product_id)

# Viết review mới (Cần đăng nhập)
@router.post("/{product_id}", response_model=ReviewOut)
def post_review(
    product_id: int, 
    review: ReviewCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Kết quả trả về từ controller là object Review, chưa có FullName
    # Ta tự điền FullName của người đang đăng nhập vào để trả về ngay cho Frontend đỡ phải query lại
    new_review = create_reviews(db, current_user.UserID, product_id, review)
    
    return {
        "ReviewID": new_review.ReviewID,
        "UserID": new_review.UserID,
        "FullName": current_user.FullName,
        "Rating": new_review.Rating,
        "Comment": new_review.Comment,
        "CreatedAt": new_review.CreatedAt
    }