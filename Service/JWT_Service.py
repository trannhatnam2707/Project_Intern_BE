from datetime import datetime, timedelta
import os
from fastapi import HTTPException, status
from dotenv import load_dotenv
from jose import jwt , JWTError



load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")


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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid or expired token")