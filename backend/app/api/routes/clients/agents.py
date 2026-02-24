"""
Client Agents Endpoint
GET /clients/{client_id}/agents/ - List agents assigned to client
"""
from fastapi import APIRouter, Header
from typing import Optional
from app.api.routes.clients.handlers import handle_get_client_agents
from app.api.routes.auth.auth_utils import get_current_user

router = APIRouter()


@router.get("/{client_id}/agents/")
async def get_client_agents(
    client_id: str,
    authorization: Optional[str] = Header(None)
):
    """Get agents assigned to this client"""
    await get_current_user(authorization)  # Auth check
    return await handle_get_client_agents(client_id)
