from sqlalchemy.orm import Session
import google.generativeai as genai
import os
from dotenv import load_dotenv
from Service.Pinecone_Service import search_pinecone

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def chat_with_ai(db: Session, user_message: str, history: list):
    if not GEMINI_API_KEY:
        return "Hệ thống AI đang bảo trì."

    # --- 1. XỬ LÝ NGỮ CẢNH TÌM KIẾM (Search Context) ---
    # Nếu câu hỏi quá ngắn (ví dụ: "giá sao?", "có màu gì?", "trả góp ko"), 
    # ta cần ghép với câu hỏi trước đó của User để Pinecone tìm đúng sản phẩm.
    
    search_query = user_message
    
    # Tìm tin nhắn gần nhất của user trong lịch sử
    last_user_msg = ""
    if history:
        # Lấy tin nhắn cuối cùng mà sender là 'user'
        for msg in reversed(history):
            if msg.get('sender') == 'user':
                last_user_msg = msg.get('text', '')
                break
    
    # Nếu có tin nhắn trước đó, thử ghép ngữ cảnh để search tốt hơn
    if last_user_msg:
        # Kỹ thuật đơn giản: "iPhone 15 Pro Max" + " " + "Có trả góp không?"
        # Giúp Pinecone tìm thấy vector chứa cả thông tin sản phẩm và chính sách trả góp
        search_query = f"{last_user_msg} {user_message}"

    print(f"🔍 Search Query thực tế: {search_query}") # Debug để xem server tìm gì

    # --- 2. RETRIEVAL (Tìm kiếm Pinecone với query đã ghép) ---
    relevant_contexts = search_pinecone(search_query, top_k=5)

    context_text = ""
    if relevant_contexts:
        context_text = "🔍 THÔNG TIN TÌM THẤY TỪ KHO:\n"
        for i, item in enumerate(relevant_contexts):
            name = item.get('ProductName', 'Sản phẩm')
            price = float(item.get('Price', 0))
            stock = int(item.get('Stock', 0))
            desc = item.get('text_chunk', '') or item.get('Description', '')
            status = "Còn hàng" if stock > 0 else "Hết hàng"
            
            context_text += f"- {name} (Giá: {price:,.0f}đ, Kho: {status})\n"
            context_text += f"  Chi tiết: {desc}\n\n"
    else:
        context_text = "⚠️ Không tìm thấy thông tin sản phẩm cụ thể nào trong kho."

    # --- 3. FORMAT LỊCH SỬ CHAT (Chat History) ---
    # Chuyển list history thành text để đưa vào Prompt
    chat_history_text = ""
    # Chỉ lấy 6 tin nhắn gần nhất để đỡ tốn token
    recent_history = history[-6:] 
    for msg in recent_history:
        role = "Khách" if msg['sender'] == 'user' else "AI"
        chat_history_text += f"{role}: {msg['text']}\n"

    # --- 4. GENERATION (Prompt) ---
    prompt = f"""
     Bạn là nhân viên tư vấn bán hàng chuyên nghiệp, nhiệt tình của cửa hàng công nghệ WeHappi Tech.
    
     KHÁCH HỎI: "{user_message}"
    
     THÔNG TIN KHO HÀNG THAM KHẢO:
    {context_text}
    
     YÊU CẦU TRẢ LỜI:
    1. Chỉ trả lời dựa trên "THÔNG TIN KHO HÀNG" được cung cấp ở trên.
    2. Nếu tìm thấy sản phẩm phù hợp:
       - Giới thiệu tên, giá và các điểm nổi bật nhất (trong phần mô tả).
       - Nếu "Hết hàng", hãy báo khách biết để họ cân nhắc.
       - Có thể tìm thêm thông tin ở ngoài để trả lời hay hơn (Nhưng phải đúng sản phẩm)
    3. Nếu KHÔNG tìm thấy thông tin liên quan:
       - Xin lỗi khéo léo và gợi ý khách hỏi về các sản phẩm công nghệ khác (Điện thoại, Laptop...).
       - Tuyệt đối KHÔNG tự bịa ra sản phẩm không có trong danh sách.
    4. Giọng văn: Thân thiện, vui vẻ, sử dụng emoji  để sinh động, không nên viết quá dài.
    """


    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Xin lỗi, tôi đang mất kết nối một chút. Bạn hỏi lại nhé!"