from fastapi import APIRouter


router = APIRouter()

@router.get("/health", tags=["internal"])
async def health():
    return {"status": "ok"}