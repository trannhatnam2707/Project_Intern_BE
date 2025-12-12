from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from Database.Connection import get_db
# Import Schema và Controller
from Schemas.Chat_Schemas import ChatRequest
from Controllers.Chat_Controller import chat_with_ai

router = APIRouter(
    prefix="/api/chat",
    tags=["Chatbot"]
)

@router.post("/")
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    API Chatbot RAG:
    1. Nhận câu hỏi từ người dùng.
    2. Tìm kiếm thông tin sản phẩm liên quan trong Pinecone (Vector DB).
    3. Gửi thông tin + câu hỏi cho Gemini AI để sinh câu trả lời.
    """
    try:
        # Gọi Controller để xử lý logic
        response_text = chat_with_ai(db, request.message)
        
        # Trả về format JSON khớp với Frontend (res.data.reply)
        return {"reply": response_text}
        
    except Exception as e:
        return {"reply": f"Xin lỗi, hệ thống gặp lỗi: {str(e)}"}