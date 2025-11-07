from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from Database.Connection import get_db
from Controllers.Admin_Controller import *
from Models.Users_Model import Users
from Schemas.Admin_Schemas import AdminCreate, AdminLogin
from Utils.Dependencies import require_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])


#Tạo admin mới (chỉ cho setup key)
@router.post("/create-admin")
def create_admin_account(admin: AdminCreate, db: Session = Depends(get_db)):
    return create_admin(db, admin.full_name, admin.email, admin.password, admin.setup_key)

# Lấy tất cả user (cần admin)
@router.get("/users")
def get_users(db: Session = Depends(get_db), current_user: Users = Depends(require_admin)):
    return get_all_users(db)

# Lấy chi tiết user
@router.get("/users/{user_id}")
def get_user_detail(user_id: int, db: Session = Depends(get_db), current_user: Users = Depends(require_admin)):
    return get_user_by_id(db, user_id)

# Cập nhật role user
@router.put("/users/{user_id}/role")
def update_user_role_route(user_id: int, new_role: str, db: Session = Depends(get_db), current_user: Users = Depends(require_admin)):
    return update_user_role(db, user_id, new_role)

# Xóa user theo id
@router.delete("/users/{user_id}")
def delete_user_route(user_id: int, db: Session = Depends(get_db), current_user: Users = Depends(require_admin)):
    return delete_user(db, user_id)

# Xóa tất cả user (trừ admin)
@router.delete("/users")
def delete_all_users_route(db: Session = Depends(get_db), current_user: Users = Depends(require_admin)):
    return delete_all_users(db)
