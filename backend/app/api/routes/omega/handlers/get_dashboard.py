"""
Handler: OMEGA Company Dashboard - Super Admin Executive View
Real Stripe + Supabase data
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging
import os
from datetime import date, timedelta
import stripe

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


async def handle_get_omega_dashboard() -> Dict[str, Any]:
    """
    Get OMEGA Company executive dashboard with real data

    Returns:
        Complete agency metrics: revenue, resellers, clients, content, agents, posts

    Raises:
        HTTPException 500: Database or Stripe error
    """
    try:
        supabase = get_supabase_service()
        today = date.today()
        first_of_month = today.replace(day=1).isoformat()

        # 1. Stripe Revenue Data
        mrr = 0
        total_revenue = 0
        try:
            # Get active subscriptions for MRR
            subscriptions = stripe.Subscription.list(status='active', limit=100)
            mrr = sum(
                sub.plan.amount / 100 for sub in subscriptions.data
                if sub.plan.interval == 'month'
            )

            # Get total revenue from charges
            charges = stripe.Charge.list(limit=100)
            total_revenue = sum(c.amount / 100 for c in charges.data if c.paid)
        except Exception as e:
            logger.warning(f"Stripe data unavailable: {e}")

        # 2. Resellers Stats
        resellers_resp = supabase.client.table("resellers")\
            .select("id, name, slug, plan, status")\
            .execute()
        resellers_data = resellers_resp.data or []

        active_resellers = [r for r in resellers_data if r.get("status") == "active"]
        trial_resellers = [r for r in resellers_data if r.get("status") == "trial"]

        # 3. Clients Stats
        clients_resp = supabase.client.table("clients")\
            .select("id, reseller_id, created_at, status")\
            .neq("status", "deleted")\
            .execute()
        clients_data = clients_resp.data or []

        new_clients_month = [
            c for c in clients_data
            if c.get("created_at", "")[:10] >= first_of_month
        ]

        # Clients by reseller
        by_reseller = {}
        for c in clients_data:
            rid = c.get("reseller_id", "direct")
            by_reseller[rid] = by_reseller.get(rid, 0) + 1

        # 4. Content Stats
        content_resp = supabase.client.table("content_lab_generated")\
            .select("id, content_type, created_at")\
            .execute()
        content_data = content_resp.data or []

        content_month = [
            c for c in content_data
            if c.get("created_at", "")[:10] >= first_of_month
        ]

        by_type = {}
        for c in content_data:
            ctype = c.get("content_type", "unknown")
            by_type[ctype] = by_type.get(ctype, 0) + 1

        videos_total = by_type.get("video", 0)

        # 5. Agents Stats
        exec_resp = supabase.client.table("agent_executions")\
            .select("id, status, started_at")\
            .execute()
        exec_data = exec_resp.data or []

        exec_month = [
            e for e in exec_data
            if e.get("started_at", "")[:10] >= first_of_month
        ]

        successful = sum(1 for e in exec_data if e.get("status") == "completed")
        success_rate = round((successful / len(exec_data)) * 100, 1) if exec_data else 0

        # 6. Social Accounts
        accounts_resp = supabase.client.table("social_accounts")\
            .select("id, platform, is_active")\
            .eq("is_active", True)\
            .execute()
        accounts_data = accounts_resp.data or []

        by_platform = {}
        for acc in accounts_data:
            platform = acc.get("platform", "unknown")
            by_platform[platform] = by_platform.get(platform, 0) + 1

        # 7. Scheduled Posts
        posts_resp = supabase.client.table("scheduled_posts")\
            .select("id, status, scheduled_date")\
            .eq("is_active", True)\
            .execute()
        posts_data = posts_resp.data or []

        scheduled = [p for p in posts_data if p.get("status") == "scheduled"]
        published_month = [
            p for p in posts_data
            if p.get("status") == "published" and p.get("scheduled_date", "")[:10] >= first_of_month
        ]

        next_7days = (today + timedelta(days=7)).isoformat()
        upcoming = [
            p for p in scheduled
            if today.isoformat() <= p.get("scheduled_date", "")[:10] <= next_7days
        ]

        logger.info(f"OMEGA Dashboard: {len(resellers_data)} resellers, {len(clients_data)} clients")

        return {
            "agency": {
                "name": "Raisen Agency",
                "plan": "enterprise",
                "mrr": round(mrr, 2),
                "arr": round(mrr * 12, 2),
                "total_revenue": round(total_revenue, 2)
            },
            "resellers": {
                "total": len(resellers_data),
                "active": len(active_resellers),
                "trial": len(trial_resellers),
                "list": resellers_data[:10]
            },
            "clients": {
                "total": len(clients_data),
                "active": len(clients_data),
                "new_this_month": len(new_clients_month),
                "by_reseller": by_reseller
            },
            "content": {
                "generated_total": len(content_data),
                "generated_this_month": len(content_month),
                "by_type": by_type,
                "videos_generated": videos_total
            },
            "agents": {
                "total": 37,
                "executions_total": len(exec_data),
                "executions_this_month": len(exec_month),
                "success_rate": success_rate
            },
            "social_accounts": {
                "total": len(accounts_data),
                "by_platform": by_platform
            },
            "scheduled_posts": {
                "total_scheduled": len(scheduled),
                "published_this_month": len(published_month),
                "upcoming_7days": len(upcoming)
            }
        }

    except Exception as e:
        logger.error(f"Error getting OMEGA dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")
