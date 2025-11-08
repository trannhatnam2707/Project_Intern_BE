from fastapi import FastAPI

from Config.Cors_Config import configure_cors
from Routers import Admin_Router, User_Router , Products_Router



app = FastAPI(title="User Management API", version="1.0.0")

configure_cors(app)


app.include_router(User_Router.router)
app.include_router(Admin_Router.router)
app.include_router(Products_Router.router)

