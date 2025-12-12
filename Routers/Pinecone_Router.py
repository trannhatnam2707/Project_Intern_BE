from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from Database.Connection import get_db
from Schemas.Pinecone_Schemas import PineconePayload
from Service.Pinecone_Service import sync_product_to_pinecone

router = APIRouter(prefix="/api/pinecone", tags=["Pinecone Sync"])

@router.post("/sync")
def handle_sync_webhook(payload: PineconePayload):
    try:
        success = sync_product_to_pinecone(
            action=payload.action,
            product_id=payload.id,
            data=payload.data
        )
        
        if success:
            return {"status": "success", "message": f"Đã xử lý {payload.action} cho ID {payload.id}"}
        else:
            return {"status": "failed", "message": "Có lỗi hoặc không có dữ liệu để xử lý"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))