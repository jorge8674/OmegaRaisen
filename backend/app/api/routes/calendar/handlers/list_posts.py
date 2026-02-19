"""
Handler: List Posts
Retrieves scheduled posts for an account
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import HTTPException
import logging

from app.api.routes.calendar.models import ScheduledPostListResponse, ScheduledPostResponse
from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.scheduled_post_repository import ScheduledPostRepository

logger = logging.getLogger(__name__)


async def handle_list_posts(
    account_id: str,
    limit: int = 20,
    offset: int = 0,
    status: str = None
) -> ScheduledPostListResponse:
    """
    List scheduled posts for an account

    Args:
        account_id: Social account UUID
        limit: Max results per page
        offset: Pagination offset
        status: Optional status filter (draft, scheduled, published, etc.)

    Returns:
        ScheduledPostListResponse with paginated results

    Raises:
        HTTPException 500: If query fails
    """
    try:
        # Get services
        supabase = get_supabase_service()
        repo = ScheduledPostRepository(supabase)

        # Fetch posts (with optional status filter)
        if status:
            # Query with status filter
            query = supabase.client.table("scheduled_posts")\
                .select("*")\
                .eq("account_id", account_id)\
                .eq("is_active", True)\
                .eq("status", status)\
                .order("scheduled_date", desc=False)\
                .order("scheduled_time", desc=False)\
                .range(offset, offset + limit - 1)

            response = query.execute()
            posts = [repo._map_to_entity(row) for row in response.data]
        else:
            # Query without status filter (use existing repo method)
            posts = await repo.find_by_account(account_id, limit, offset)

        # Count total (for pagination)
        # Note: In production, this should be optimized with a separate count query
        count_query = supabase.client.table("scheduled_posts")\
            .select("id", count="exact")\
            .eq("account_id", account_id)\
            .eq("is_active", True)

        if status:
            count_query = count_query.eq("status", status)

        count_response = count_query.execute()

        total = count_response.count if hasattr(count_response, 'count') else len(posts)

        # Map to response DTOs
        items = [
            ScheduledPostResponse(
                id=post.id,
                client_id=post.client_id,
                account_id=post.account_id,
                content_lab_id=post.content_lab_id,
                content_type=post.content_type,
                text_content=post.text_content,
                image_url=post.image_url,
                hashtags=post.hashtags,
                scheduled_date=post.scheduled_date,
                scheduled_time=post.scheduled_time,
                timezone=post.timezone,
                status=post.status,
                agent_assigned=post.agent_assigned,
                is_active=post.is_active,
                created_at=post.created_at.isoformat() if post.created_at else "",
                updated_at=post.updated_at.isoformat() if post.updated_at else "",
            )
            for post in posts
        ]

        logger.info(f"Listed {len(items)} posts for account {account_id}")

        return ScheduledPostListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset
        )

    except Exception as e:
        logger.error(f"Error listing posts for account {account_id}: {e}")
        raise HTTPException(500, f"Failed to list posts: {str(e)}")
