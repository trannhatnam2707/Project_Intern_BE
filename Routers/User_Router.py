from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from Controllers.User_Controller import (
    register_user,
    login_user,
    get_me,
    update_profile,
    change_password,
    refresh_access_token,
)
from Schemas.User_Schemas import UserCreate, UserLogin, UserUpdate, ChangePassword
from Database.Connection import get_db
from Utils.Dependencies import get_current_user  # check JWT
from Models.Users_Model import Users

router = APIRouter(
    prefix="/api",
    tags=["Users và Auth"],
)

# ---------- Auth ----------
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user)


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


# ---------- User ----------
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


