"""
OMEGA Company Router - Super Admin Dashboard
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import APIRouter, Query
from typing import Optional

from .handlers import (
    handle_get_omega_dashboard,
    handle_get_resellers,
    handle_get_clients,
    handle_get_revenue,
    handle_get_activity,
    handle_get_agents
)

router = APIRouter(prefix="/omega", tags=["omega"])


@router.get("/dashboard/")
async def get_omega_dashboard():
    """Get OMEGA Company executive dashboard with Stripe + Supabase data"""
    return await handle_get_omega_dashboard()


@router.get("/resellers/")
async def get_resellers(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(default=50, description="Results per page"),
    offset: int = Query(default=0, description="Pagination offset")
):
    """Get resellers list with metrics"""
    return await handle_get_resellers(status, limit, offset)


@router.get("/clients/")
async def get_clients(
    reseller_id: Optional[str] = Query(None, description="Filter by reseller UUID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(default=50, description="Results per page"),
    offset: int = Query(default=0, description="Pagination offset")
):
    """Get all clients with pagination"""
    return await handle_get_clients(reseller_id, status, limit, offset)


@router.get("/revenue/")
async def get_revenue():
    """Get revenue breakdown from Stripe"""
    return await handle_get_revenue()


@router.get("/activity/")
async def get_activity(
    limit: int = Query(default=50, description="Number of activity items")
):
    """Get recent activity feed"""
    return await handle_get_activity(limit)


@router.get("/agents/")
async def get_agents():
    """Get all agents organized by department with stats"""
    return await handle_get_agents()
