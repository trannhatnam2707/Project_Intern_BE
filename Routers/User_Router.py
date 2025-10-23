from fastapi import APIRouter
from Controllers.User_Controller import login_user, register_user
from Schemas.User_Schemas import UserCreate, UserLogin


router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)

@router.post("/register")
def register(user: UserCreate):
    return register_user(user)

@router.post("/login")
def login(user: UserLogin):
    return login_user(user)