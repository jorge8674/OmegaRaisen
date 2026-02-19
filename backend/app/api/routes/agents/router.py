"""
Agents Router
FastAPI REST endpoints for agents system
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import APIRouter, Query, Path
from typing import Optional

from .models import (
    AgentListResponse,
    AgentDetailResponse,
    ExecuteAgentRequest,
    ExecutionResponse,
    ExecutionListResponse,
    LogListResponse
)
from .handlers import (
    handle_list_agents,
    handle_get_agent,
    handle_execute_agent,
    handle_get_executions,
    handle_get_logs
)

router = APIRouter(prefix="/agents", tags=["Agents 🤖"])


@router.get("/", response_model=AgentListResponse)
async def list_agents(
    department: Optional[str] = Query(None, description="Filter by department"),
    status: Optional[str] = Query(None, description="Filter by status: active, inactive, maintenance")
) -> AgentListResponse:
    """
    List all agents with metrics

    Returns all agents in the system with their execution statistics.
    Optional filters for department and status.

    **Departments**: núcleo, contenido, video, contexto, publicación, analytics
    """
    return await handle_list_agents(department, status)


@router.get("/{agent_id}/", response_model=AgentDetailResponse)
async def get_agent(
    agent_id: str = Path(..., description="Agent identifier")
) -> AgentDetailResponse:
    """
    Get agent detail with stats

    Returns detailed information about a specific agent including:
    - Agent configuration and capabilities
    - Execution statistics
    - Success/failure rates
    - Average execution time
    """
    return await handle_get_agent(agent_id)


@router.post("/{agent_id}/execute/", response_model=ExecutionResponse, status_code=201)
async def execute_agent(
    agent_id: str = Path(..., description="Agent identifier"),
    request: ExecuteAgentRequest = ...
) -> ExecutionResponse:
    """
    Execute an agent

    Triggers agent execution with provided input data.
    Returns execution details including status and output.

    **Note**: Agent must be in 'active' status to execute.
    """
    return await handle_execute_agent(agent_id, request)


@router.get("/{agent_id}/executions/", response_model=ExecutionListResponse)
async def get_agent_executions(
    agent_id: str = Path(..., description="Agent identifier"),
    limit: int = Query(20, ge=1, le=100, description="Max results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    status: Optional[str] = Query(None, description="Filter by status: pending, running, completed, failed, cancelled")
) -> ExecutionListResponse:
    """
    Get agent execution history

    Returns paginated list of executions for this agent.
    Optional status filter to show only specific execution states.
    """
    return await handle_get_executions(agent_id, limit, offset, status)


@router.get("/executions/{execution_id}/logs/", response_model=LogListResponse)
async def get_execution_logs(
    execution_id: str = Path(..., description="Execution UUID"),
    limit: int = Query(100, ge=1, le=1000, description="Max log entries")
) -> LogListResponse:
    """
    Get execution logs

    Returns detailed logs for a specific execution.
    Useful for debugging and monitoring agent behavior.
    """
    return await handle_get_logs(execution_id, limit)
