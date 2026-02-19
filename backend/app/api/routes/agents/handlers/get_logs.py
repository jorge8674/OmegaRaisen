"""
Handler: Get Execution Logs
Retrieves detailed logs for an execution
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import HTTPException
import logging

from app.api.routes.agents.models import LogListResponse, LogResponse
from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.agent_repository import AgentRepository

logger = logging.getLogger(__name__)


async def handle_get_logs(
    execution_id: str,
    limit: int = 100
) -> LogListResponse:
    """
    Get logs for an execution

    Args:
        execution_id: Execution UUID
        limit: Max log entries to return

    Returns:
        LogListResponse with execution logs

    Raises:
        HTTPException 404: If execution not found
        HTTPException 500: If query fails
    """
    try:
        # Get services
        supabase = get_supabase_service()
        repo = AgentRepository(supabase)

        # Fetch logs
        logs = repo.find_logs_by_execution(execution_id, limit=limit)

        if not logs:
            # Verify execution exists
            try:
                exec_check = supabase.client.table("agent_executions")\
                    .select("id, agent_id")\
                    .eq("id", execution_id)\
                    .single()\
                    .execute()

                if not exec_check.data:
                    raise HTTPException(404, f"Execution '{execution_id}' not found")

            except Exception:
                raise HTTPException(404, f"Execution '{execution_id}' not found")

        # Map to response DTOs
        items = [
            LogResponse(
                id=log.id,
                execution_id=log.execution_id,
                agent_id=log.agent_id,
                level=log.level,
                message=log.message,
                details=log.details,
                logged_at=log.logged_at.isoformat() if log.logged_at else "",
                created_at=log.created_at.isoformat() if log.created_at else "",
            )
            for log in logs
        ]

        logger.info(f"Retrieved {len(items)} logs for execution '{execution_id}'")

        return LogListResponse(
            items=items,
            total=len(items),
            execution_id=execution_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting logs for execution {execution_id}: {e}")
        raise HTTPException(500, f"Failed to get logs: {str(e)}")
