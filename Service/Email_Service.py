from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, MessageType
from Config.Email_Config import conf
from pydantic import EmailStr
import os

load_dotenv()

async def send_reset_password_email(email: EmailStr, reset_token: str):
    # Lấy URL từ .env, nếu không có thì mặc định là localhost
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # Tạo link reset động
    reset_link = f"{frontend_url}/reset-password?token={reset_token}"

    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
        <h2 style="color: #1890ff;">WehappiTech - Yêu cầu đặt lại mật khẩu</h2>
        <p>Xin chào,</p>
        <p>Chúng tôi nhận được yêu cầu khôi phục mật khẩu cho tài khoản <b>{email}</b>.</p>
        <p>Vui lòng nhấn vào nút bên dưới để tạo mật khẩu mới:</p>
        
        <a href="{reset_link}" 
           style="display: inline-block; padding: 12px 24px; background-color: #1890ff; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 10px 0;">
           Đặt lại mật khẩu ngay
        </a>
        
        <p><i>Link này sẽ hết hạn trong 15 phút.</i></p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="font-size: 12px; color: #888;">Nếu bạn không thực hiện yêu cầu này, vui lòng bỏ qua email này.</p>
    </div>
    """

    message = MessageSchema(
        subject="[WehappiTech] Hướng dẫn đặt lại mật khẩu",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    return {"message": "Email has been sent"}