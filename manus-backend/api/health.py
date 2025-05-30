from fastapi import APIRouter, HTTPException, Depends
from supabase import Client
from api.deps import get_supabase

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Manus Clone is running"}

@router.get("/health")
async def health_check(db: Client = Depends(get_supabase)):
    try:
        # Test database connection
        db.table("chat").select("count", count="exact").execute()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database connection failed")