from passlib.context import CryptContext  

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#-----Hash mật khẩu-------#
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

#-----Kiểm tra mât khẩu-------#
def verify_password(plain_password: str, hashed_pw: str) -> bool:
    return pwd_context.verify(plain_password, hashed_pw)

