from pydantic import BaseModel

class AdminCreate(BaseModel):
    full_name: str
    email: str
    password: str
    setup_key: str

class AdminLogin(BaseModel):
    Email: str
    Password: str