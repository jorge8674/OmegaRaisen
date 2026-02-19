"""
Handler: Get Agent Detail
Retrieves single agent with detailed stats
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import HTTPException
import logging

from app.api.routes.agents.models import AgentDetailResponse, AgentResponse
from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.agent_repository import AgentRepository

logger = logging.getLogger(__name__)


async def handle_get_agent(agent_id: str) -> AgentDetailResponse:
    """
    Get agent detail with stats

    Args:
        agent_id: Agent identifier

    Returns:
        AgentDetailResponse with agent info and execution stats

    Raises:
        HTTPException 404: If agent not found
        HTTPException 500: If query fails
    """
    try:
        # Get services
        supabase = get_supabase_service()
        repo = AgentRepository(supabase)

        # Fetch agent
        agent = repo.find_by_agent_id(agent_id)

        if not agent:
            raise HTTPException(404, f"Agent '{agent_id}' not found")

        # Build stats
        stats = {
            "operational_status": agent.is_operational(),
            "can_execute": agent.can_execute(),
            "success_rate": agent.success_rate(),
            "failure_rate": 100 - agent.success_rate() if agent.total_executions > 0 else 0,
            "avg_execution_seconds": agent.avg_execution_time_ms / 1000 if agent.avg_execution_time_ms > 0 else 0,
            "total_executions": agent.total_executions,
            "successful": agent.successful_executions,
            "failed": agent.failed_executions,
            "pending": repo.count_executions(agent_id, "pending"),
            "running": repo.count_executions(agent_id, "running"),
        }

        # Map to response DTO
        agent_response = AgentResponse(
            id=agent.id,
            agent_id=agent.agent_id,
            name=agent.name,
            description=agent.description,
            department=agent.department,
            category=agent.category,
            status=agent.status,
            version=agent.version,
            capabilities=agent.capabilities,
            config=agent.config,
            total_executions=agent.total_executions,
            successful_executions=agent.successful_executions,
            failed_executions=agent.failed_executions,
            success_rate=agent.success_rate(),
            avg_execution_time_ms=agent.avg_execution_time_ms,
            last_executed_at=agent.last_executed_at.isoformat() if agent.last_executed_at else None,
            is_active=agent.is_active,
            created_at=agent.created_at.isoformat() if agent.created_at else "",
            updated_at=agent.updated_at.isoformat() if agent.updated_at else "",
        )

        logger.info(f"Retrieved agent '{agent_id}' with stats")

        return AgentDetailResponse(
            agent=agent_response,
            stats=stats
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent {agent_id}: {e}")
        raise HTTPException(500, f"Failed to get agent: {str(e)}")
