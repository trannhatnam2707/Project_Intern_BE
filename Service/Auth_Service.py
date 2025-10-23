from datetime import datetime, timedelta
import re 
from dotenv import load_dotenv
import os
from passlib.context import CryptContext  
from jose import jwt , JWTError

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#-----Hash mật khẩu-------#
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

#-----Kiểm tra mât khẩu-------#
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

#-----Tạo JWT-------#
def create_access_token(data: dict, expires_delta: timedelta | None ) -> str:
    to_endcode = data.copy()
    expires = datetime.utcnow() + (expires_delta or timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)))
    to_endcode.update({"exp": expires})
    encoded_jwt = jwt.encode(to_endcode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#------Giải mã JWT-------#
def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None