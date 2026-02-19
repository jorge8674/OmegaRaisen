"""
Handler: List Agents
Retrieves all agents with metrics
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import HTTPException
import logging
from typing import Optional

from app.api.routes.agents.models import AgentListResponse, AgentResponse
from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.agent_repository import AgentRepository

logger = logging.getLogger(__name__)


async def handle_list_agents(
    department: Optional[str] = None,
    status: Optional[str] = None
) -> AgentListResponse:
    """
    List all agents with optional filters

    Args:
        department: Filter by department (núcleo, contenido, video, etc.)
        status: Filter by status (active, inactive, maintenance)

    Returns:
        AgentListResponse with all agents and their metrics

    Raises:
        HTTPException 500: If query fails
    """
    try:
        # Get services
        supabase = get_supabase_service()
        repo = AgentRepository(supabase)

        # Fetch agents
        agents = repo.find_all(department=department, status=status)

        # Map to response DTOs
        items = [
            AgentResponse(
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
            for agent in agents
        ]

        logger.info(f"Listed {len(items)} agents (department={department}, status={status})")

        return AgentListResponse(
            items=items,
            total=len(items),
            department_filter=department,
            status_filter=status
        )

    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(500, f"Failed to list agents: {str(e)}")
