
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from Controllers.User_Controller import (
    create_admin,
    delete_all_users,
    delete_user,
    forgot_password,
    get_all_users,
    register_user,
    login_user,
    get_me,
    update_profile,
    change_password,
    refresh_access_token,
    get_user_by_id,
    update_user_role,
    confirm_reset_password
)
from Schemas.Admin_Schemas import AdminCreate
from Schemas.User_Schemas import UserCreate, UserLogin, UserUpdate, ChangePassword, ResetPasswordConfirm
from Database.Connection import get_db
from Utils.Dependencies import get_current_user, require_admin  # check JWT
from Models.Users_Model import Users

router = APIRouter(
    prefix="/api/users",
    tags=["Users/Admin & Auth"],
)

# ---------- Auth ----------
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user)

#Tạo admin mới (chỉ cho setup key)
@router.post("/create-admin")
def create_admin_account(admin: AdminCreate, db: Session = Depends(get_db)):
    return create_admin(db, admin.full_name, admin.email, admin.password, admin.setup_key)

@router.post("/auth/login", tags=["Auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """API login chung cho cả user và admin
        Swagger sẽ dùng route này để authorize """
    
    #chuyển Oauth2 form về schema tương thích
    user_data = type("UserLogin", (), {"Email": form_data.username, "Password": form_data.password})
    return login_user(db, user_data)

@router.post("/refresh")
def refresh_token(refresh_token: str):
    """Lấy access token mới khi access token hết hạn"""
    return refresh_access_token(refresh_token)

#-----------Admin Routes-----------#

# Lấy tất cả user (cần admin)
@router.get("/users")
def get_users(
    page: int = 1, 
    limit: int = 10, 
    search: str = None, 
    db: Session = Depends(get_db), 
    current_user: Users = Depends(require_admin)
):
    return get_all_users(db, page, limit, search)
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

# ---------- User Router----------
@router.get("/me")
def get_my_info(current_user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_me(db, current_user)


@router.put("/profile")
def update_my_profile(
    update_data: UserUpdate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_profile(db, current_user, update_data)


@router.put("/change-password")
def change_my_password(
    data: ChangePassword,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return change_password(db, current_user, data)

# API quên mật khẩu
@router.post("/forgot-password")
async def forgot_password_router(
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    return await forgot_password(db, email, background_tasks)

@router.post("/reset-password")
def reset_password_route(data: ResetPasswordConfirm, db: Session = Depends(get_db)):
    return confirm_reset_password(db, data)
