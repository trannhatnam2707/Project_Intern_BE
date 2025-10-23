from fastapi import FastAPI

from Config.Cors_Config import configure_cors
from Routers import User_Router



app = FastAPI(title="User Management API", version="1.0.0")

configure_cors(app)


app.include_router(User_Router.router)

@app.get("/")
def root():
    return {"message": "EcommerceAI API is running!"}