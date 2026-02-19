"""
Handler: Get Agent Executions
Retrieves execution history for an agent
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import HTTPException
import logging
from typing import Optional

from app.api.routes.agents.models import ExecutionListResponse, ExecutionResponse
from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.agent_repository import AgentRepository

logger = logging.getLogger(__name__)


async def handle_get_executions(
    agent_id: str,
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None
) -> ExecutionListResponse:
    """
    Get execution history for an agent

    Args:
        agent_id: Agent identifier
        limit: Max results per page
        offset: Pagination offset
        status: Optional status filter

    Returns:
        ExecutionListResponse with paginated executions

    Raises:
        HTTPException 404: If agent not found
        HTTPException 500: If query fails
    """
    try:
        # Get services
        supabase = get_supabase_service()
        repo = AgentRepository(supabase)

        # Verify agent exists
        agent = repo.find_by_agent_id(agent_id)
        if not agent:
            raise HTTPException(404, f"Agent '{agent_id}' not found")

        # Fetch executions
        executions = repo.find_executions_by_agent(
            agent_id=agent_id,
            limit=limit,
            offset=offset,
            status=status
        )

        # Count total
        total = repo.count_executions(agent_id, status)

        # Map to response DTOs
        items = [
            ExecutionResponse(
                id=exec.id,
                agent_id=exec.agent_id,
                client_id=exec.client_id,
                user_id=exec.user_id,
                triggered_by=exec.triggered_by,
                input_data=exec.input_data,
                output_data=exec.output_data,
                error_message=exec.error_message,
                status=exec.status,
                started_at=exec.started_at.isoformat() if exec.started_at else None,
                completed_at=exec.completed_at.isoformat() if exec.completed_at else None,
                execution_time_ms=exec.execution_time_ms,
                metadata=exec.metadata,
                created_at=exec.created_at.isoformat() if exec.created_at else "",
            )
            for exec in executions
        ]

        logger.info(f"Retrieved {len(items)} executions for agent '{agent_id}'")

        return ExecutionListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            agent_id=agent_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting executions for agent {agent_id}: {e}")
        raise HTTPException(500, f"Failed to get executions: {str(e)}")
