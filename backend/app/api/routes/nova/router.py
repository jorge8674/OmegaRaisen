"""
NOVA Router - Data Persistence & Agent Memory
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import APIRouter, Query
from typing import Optional

from .handlers import (
    handle_get_data,
    handle_save_data,
    SaveDataRequest,
    handle_get_agent_memory,
    handle_save_agent_memory,
    SaveAgentMemoryRequest,
    handle_chat,
    ChatRequest
)

router = APIRouter(prefix="/nova", tags=["NOVA 👑"])


@router.get("/data/")
async def get_data(
    type: Optional[str] = Query(None, description="Filter by type: chat_history | context_docs | reports")
):
    """Get NOVA data filtered by type"""
    return await handle_get_data(data_type=type)


@router.post("/data/")
async def save_data(request: SaveDataRequest):
    """Save/update NOVA data (UPSERT)"""
    return await handle_save_data(request)


@router.get("/agent-memory/")
async def get_agent_memory(
    agent_code: Optional[str] = Query(None, description="Filter by agent code (e.g., NOVA, ATLAS)")
):
    """Get last 10 agent memory entries"""
    return await handle_get_agent_memory(agent_code)


@router.post("/agent-memory/")
async def save_agent_memory(request: SaveAgentMemoryRequest):
    """Save new agent memory entry"""
    return await handle_save_agent_memory(request)


@router.post("/chat/")
async def nova_chat(request: ChatRequest):
    """Chat with NOVA AI assistant"""
    return await handle_chat(request)
