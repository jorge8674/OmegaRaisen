"""Context Library Router"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
from .handlers import handle_list_context, handle_create_context, handle_delete_context, handle_get_context_for_agent, handle_extract_url

class CreateContextRequest(BaseModel):
    name: str
    content: str
    scope: str
    scope_id: Optional[str] = None
    tags: Optional[list[str]] = []
    file_type: Optional[str] = "text"

class ExtractUrlRequest(BaseModel):
    url: str

router = APIRouter(prefix="/context", tags=["Context Library 📚"])

@router.get("/")
async def list_context(scope: str = Query(None)):
    """List all context documents (filter by scope)"""
    return await handle_list_context(scope)

@router.post("/")
async def create_context(request: CreateContextRequest):
    """Create new context document"""
    return await handle_create_context(request)

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
