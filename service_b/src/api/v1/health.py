from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["internal"])
async def health():
    return {"status": "ok"}

from fastapi.responses import HTMLResponse
from fastapi import APIRouter
from pathlib import Path

router = APIRouter()

@router.get("/", include_in_schema=False)
async def index():
    index_path = Path(__file__).parent.parent.parent / "templates" / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding='utf-8'), status_code=200)
    return HTMLResponse(content="<h1>Frontend not found</h1>", status_code=404)
