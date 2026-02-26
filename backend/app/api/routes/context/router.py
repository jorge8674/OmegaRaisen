"""Context Library Router"""
from fastapi import APIRouter, Query, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from .handlers import handle_list_context, handle_create_context, handle_delete_context, handle_get_context_for_agent, handle_extract_url, handle_extract_file

class CreateContextRequest(BaseModel):
    name: str
    content: str
    scope: str
    scope_id: Optional[str] = None
    tags: Optional[list[str]] = []
    file_type: Optional[str] = "text"

class ExtractUrlRequest(BaseModel):
    url: str

class UpdateContextRequest(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    scope: Optional[str] = None
    scope_id: Optional[str] = None
    tags: Optional[list[str]] = None

router = APIRouter(prefix="/context", tags=["Context Library 📚"])

@router.get("/")
async def list_context(scope: str = Query(None)):
    """List all context documents (filter by scope)"""
    return await handle_list_context(scope)

@router.post("/")
async def create_context(request: CreateContextRequest):
    """Create new context document"""
    return await handle_create_context(request)

@router.patch("/{context_id}/")
async def update_context(context_id: str, request: UpdateContextRequest):
    """Update context document (partial)"""
    from fastapi import HTTPException
    from app.infrastructure.supabase_service import get_supabase_service

    update_data = {k: v for k, v in request.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(400, "No hay datos para actualizar")

    supabase = get_supabase_service()
    result = supabase.client.table("context_library")\
        .update(update_data)\
        .eq("id", context_id)\
        .execute()

    if not result.data:
        raise HTTPException(404, "Documento no encontrado")

    # Auto-clear cache so NOVA gets fresh context immediately
    import app.services.context_service as ctx_module
    ctx_module._global_cache = None
    ctx_module._global_cache_time = None

    return result.data[0]

@router.delete("/{context_id}/")
async def delete_context(context_id: str):
    """Delete context document"""
    return await handle_delete_context(context_id)

@router.get("/for-agent/")
async def get_context_for_agent(agent_code: str = Query(...), client_id: str = Query(None), department: str = Query(None)):
    """Get relevant context for agent"""
    return await handle_get_context_for_agent(agent_code, client_id, department)

@router.post("/extract-url/")
async def extract_url(request: ExtractUrlRequest):
    """Extract content from URL (webpage or PDF)"""
    return await handle_extract_url(request.url)

@router.post("/cache/clear/")
async def clear_context_cache():
    """Force clear context cache (for immediate refresh)"""
    import app.services.context_service as ctx_module
    ctx_module._global_cache = None
    ctx_module._global_cache_time = None
    return {"cleared": True, "message": "Context cache cleared - next NOVA chat will refresh from DB"}

@router.post("/extract-file/")
async def extract_file(file: UploadFile = File(...)):
    """Extract text from uploaded file (PDF, TXT, MD)"""
    return await handle_extract_file(file)
