"""Handler: Create context document"""
import logging
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

async def handle_create_context(
    name: str, content: str, scope: str, scope_id: Optional[str] = None, tags: List[str] = []
) -> Dict[str, Any]:
    """Create new context document."""
    try:
        if scope not in ["global", "client", "department"]:
            raise HTTPException(400, "Invalid scope. Must be: global, client, or department")
        if scope != "global" and not scope_id:
            raise HTTPException(400, f"scope_id required for scope={scope}")
        supabase = get_supabase_service()
        resp = supabase.client.table("context_library").insert({
            "name": name,
            "content": content,
            "scope": scope,
            "scope_id": scope_id,
            "tags": tags
        }).execute()
        if not resp.data:
            raise HTTPException(500, "Failed to create context")
        doc = resp.data[0]
        logger.info(f"Created context: {name} (scope={scope})")
        return {"id": doc["id"], "name": doc["name"], "scope": doc["scope"], "created_at": doc["created_at"]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create context: {e}")
        raise HTTPException(500, f"Failed to create context: {str(e)}")
