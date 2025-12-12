from pydantic import BaseModel
from typing import List, Optional, Dict

class ChatRequest(BaseModel):
    message: str
    # Nhận thêm danh sách lịch sử: [{'sender': 'user', 'text': '...'}, ...]
    history: List[Dict[str, str]] = []