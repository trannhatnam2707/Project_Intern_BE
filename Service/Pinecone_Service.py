import os
import google.generativeai as genai
from pinecone import Pinecone
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

# --- CẤU HÌNH ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# Phải khớp dimension khi tạo index trên Pinecone (gemini-embedding-001 mặc định 3072)
EMBEDDING_OUTPUT_DIM = int(os.getenv("EMBEDDING_OUTPUT_DIMENSIONALITY", "768"))
# Ngưỡng similarity (cosine) — 0.6 thường quá cao, dễ trả về rỗng dù index có dữ liệu
# MIN_MATCH_SCORE = float(os.getenv("PINECONE_MIN_MATCH_SCORE", "0.35"))
# DEBUG_PINECONE = os.getenv("DEBUG_PINECONE", "").lower() in ("1", "true", "yes")

if not PINECONE_API_KEY or not PINECONE_INDEX_NAME:
    print("⚠️ Cảnh báo: Chưa cấu hình Pinecone/Gemini trong .env")

try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)
except Exception as e:
    print(f"❌ Lỗi kết nối Pinecone: {e}")
    index = None

# --- 1. HÀM CẮT CHUỖI THỦ CÔNG (Giống hệt mẫu JS) ---
def split_text_into_chunks(text, chunk_size=1000, overlap=200):
    if not text or len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        # Điểm cuối dự kiến
        end = min(start + chunk_size, text_len)
        
        # Nếu chưa hết văn bản, tìm dấu cách gần nhất để không cắt giữa từ
        if end < text_len:
            # rfind: tìm vị trí xuất hiện cuối cùng của ' ' trong khoảng [start, end]
            last_space = text.rfind(' ', start, end)
            if last_space != -1 and last_space > start:
                end = last_space
        
        # Cắt và thêm vào mảng
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Tính điểm bắt đầu cho chunk sau (có gối đầu - overlap)
        start = end - overlap
        
        # Tránh vòng lặp vô tận
        if start >= end:
            start = end
            
    return chunks

# --- 2. HÀM TẠO EMBEDDING ---
def get_embedding(text):
    try:
        # Xóa dòng mới để tối ưu vector
        clean_text = text.replace("\n", " ")
        result = genai.embed_content(
            model="gemini-embedding-001",
            content=clean_text,
            task_type="retrieval_document",
            output_dimensionality=EMBEDDING_OUTPUT_DIM,
        )
        return result['embedding']
    except Exception as e:
        print(f"❌ Lỗi tạo embedding: {e}")
        return []

# --- 3. HÀM XỬ LÝ CHÍNH (SYNC) ---
def sync_product_to_pinecone(action: str, product_id: int, data=None):
    if not index: return False

    str_id = str(product_id)
    print(f"📩 Pinecone Service: Nhận lệnh {action} cho ID: {str_id}")

    # A. XÓA DỮ LIỆU CŨ (Luôn chạy trước khi Upsert hoặc Delete)
    try:
        # Xóa bằng Filter metadata (Cách chuẩn nhất)
        index.delete(filter={"original_id": {"$eq": str_id}})
        print(f"🗑️ Đã xóa vectors cũ của ID: {str_id}")
    except Exception as e:
        print(f"⚠️ Lỗi xóa filter (thử cách thủ công): {e}")
        # Backup: Xóa theo ID dự đoán (nếu filter lỗi)
        try:
            ids_to_delete = [str_id] + [f"{str_id}#{i}" for i in range(10)]
            index.delete(ids=ids_to_delete)
        except: pass

    # Nếu là DELETE thì xong rồi
    if action == 'DELETE':
        return True

    # B. THÊM MỚI / SỬA (UPSERT)
    if action == 'UPSERT' and data:
        # 1. Tạo nội dung đầy đủ
        full_content = f"""
        Tên: {data.ProductName}
        Giá: {data.Price:,.0f}
        Kho: {data.Stock}
        Mô tả: {data.Description}
        """
        
        # 2. Cắt nhỏ (Chunking)
        chunks = split_text_into_chunks(full_content)
        
        vectors = []
        for i, chunk_text in enumerate(chunks):
            # 3. Tạo Vector
            vector_values = get_embedding(chunk_text)
            
            if not vector_values: continue

            # 4. Đóng gói Vector + Metadata
            vectors.append({
                "id": f"{str_id}#{i}", # ID chunk: 101#0
                "values": vector_values,
                "metadata": {
                    "original_id": str_id,
                    "text_chunk": chunk_text, # Nội dung để RAG đọc
                    "ProductName": data.ProductName,
                    "Price": float(data.Price),
                    "Stock": int(data.Stock)
                }
            })

        # 5. Đẩy lên Pinecone
        if vectors:
            index.upsert(vectors=vectors)
            print(f"✅ Đã đồng bộ {len(vectors)} chunks lên Pinecone")
            return True
            
    return False

# --- 4. HÀM TÌM KIẾM (SEARCH) CHO CHATBOT ---
def search_pinecone(query, top_k=5):
    if not index: return []
    try:
        # Embed câu hỏi
        query_res = genai.embed_content(
            model="gemini-embedding-001",
            content=query,
            task_type="retrieval_query",
            output_dimensionality=EMBEDDING_OUTPUT_DIM,
        )
        
        # Query Pinecone
        result = index.query(
            vector=query_res['embedding'],
            top_k=top_k,
            include_metadata=True
        )

        return [match['metadata'] for match in result['matches'] if match['score'] > 0.6]
    except Exception as e:
        print(f"❌ Lỗi tìm kiếm: {e}")
        return []