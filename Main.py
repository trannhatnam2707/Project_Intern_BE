from ast import Or
from fastapi import FastAPI
from Config.Cors_Config import configure_cors

# ⚠️ Import models TRƯỚC khi import routers
from Models.Users_Model import Users
from Models.Categories_Model import Category
from Models.Products_Model import Product
from Models.AdviceHistory_Model import AdviceHistory
from Models.Order_Model import Order
from Models.OrderDetail_Model import OrderDetail
from Models.Payment_Model import Payment


# Import routers SAU khi đã import models
from Routers import  User_Router, Products_Router, Order_Router, Category_Router, Reviews_Router, Payment_Router

app = FastAPI(title="User Management API", version="1.0.0")

configure_cors(app)

app.include_router(User_Router.router)
app.include_router(Products_Router.router)
app.include_router(Order_Router.router)
app.include_router(Category_Router.router)
app.include_router(Reviews_Router.router)
app.include_router(Payment_Router.router) 