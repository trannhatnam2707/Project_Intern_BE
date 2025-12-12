from sqlalchemy.orm import Session
import google.generativeai as genai
import os
from dotenv import load_dotenv
# Import hàm tìm kiếm từ Service Pinecone chúng ta đã viết
from Service.Pinecone_Service import search_pinecone

# Load cấu hình
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def chat_with_ai(db: Session, user_message: str):
    # 1. Kiểm tra Key
    if not GEMINI_API_KEY:
        return "Hệ thống AI đang bảo trì (Thiếu API Key)."

    # 2. RETRIEVAL: Tìm kiếm thông tin liên quan từ Pinecone
    # Hàm này trả về list các metadata của các chunk khớp nhất (độ tương đồng > 0.6)
    relevant_contexts = search_pinecone(user_message, top_k=5)

    # 3. AUGMENTED: Xây dựng ngữ cảnh (Context) để "mớm" cho AI
    context_text = ""
    if relevant_contexts:
        context_text = " DỮ LIỆU TÌM THẤY TRONG KHO:\n"
        for i, item in enumerate(relevant_contexts):
            # Lấy thông tin từ metadata (đã lưu lúc Upsert)
            name = item.get('ProductName', 'Sản phẩm')
            price = float(item.get('Price', 0))
            stock = int(item.get('Stock', 0))
            # Ưu tiên lấy text_chunk (nội dung cắt nhỏ), nếu không có thì lấy Description gốc
            desc = item.get('text_chunk', '') or item.get('Description', '')
            
            status = "Còn hàng" if stock > 0 else "Hết hàng"
            
            context_text += f"--- Sản phẩm {i+1}: {name} ---\n"
            context_text += f"• Giá: {price:,.0f} VNĐ | Kho: {status}\n"
            context_text += f"• Thông tin chi tiết: {desc}\n\n"
    else:
        context_text = " Hệ thống KHÔNG tìm thấy sản phẩm nào trong kho khớp với từ khóa trong câu hỏi."

    # 4. GENERATION: Tạo Prompt và gửi cho Gemini
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
        # Gọi Gemini
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Lỗi Gemini: {e}")
        return "Xin lỗi, tôi đang bị chóng mặt chút xíu. Bạn hãy thử hỏi lại sau nhé!"