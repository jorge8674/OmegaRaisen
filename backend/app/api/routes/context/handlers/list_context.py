"""Handler: List context documents"""
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

async def handle_list_context(scope: Optional[str] = None) -> Dict[str, Any]:
    """List all context documents with optional scope filter."""
    try:
        supabase = get_supabase_service()
        query = supabase.client.table("context_library")\
            .select("*", count="exact")\
            .eq("is_active", True)\
            .order("created_at", desc=True)
        if scope:
            query = query.eq("scope", scope)
        resp = query.execute()
        return {"docs": resp.data or [], "total": resp.count or 0}
    except Exception as e:
        logger.error(f"Failed to list context: {e}")
        raise HTTPException(500, f"Failed to list context: {str(e)}")
