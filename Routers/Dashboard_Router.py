from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from Database.Connection import get_db
from Utils.Dependencies import require_admin
from Controllers.Dashboard_Controller import get_dashboard_stats

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats", dependencies=[Depends(require_admin)])
def get_stats(time_range: str = 'month', db: Session = Depends(get_db)):
    return get_dashboard_stats(db, time_range)