"""Handler: Create context document"""
import logging
from typing import Dict, Any
from fastapi import HTTPException
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

async def handle_create_context(request) -> Dict[str, Any]:
    """Create new context document from JSON body."""
    try:
        if request.scope not in ["global", "client", "department"]:
            raise HTTPException(400, "Invalid scope. Must be: global, client, or department")
        if request.scope != "global" and not request.scope_id:
            raise HTTPException(400, f"scope_id required for scope={request.scope}")
        supabase = get_supabase_service()
        resp = supabase.client.table("context_library").insert({
            "name": request.name,
            "content": request.content,
            "scope": request.scope,
            "scope_id": request.scope_id,
            "tags": request.tags or [],
            "file_type": request.file_type or "text",
            "created_by": "ibrain"
        }).execute()
        if not resp.data:
            raise HTTPException(500, "Failed to create context")
        doc = resp.data[0]
        logger.info(f"Created context: {request.name} (scope={request.scope})")
        return doc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create context: {e}")
        raise HTTPException(500, f"Failed to create context: {str(e)}")
