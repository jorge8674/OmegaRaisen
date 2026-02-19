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
    account_id: str = None,
    client_id: str = None,
    limit: int = 20,
    offset: int = 0,
    status: str = None
) -> ScheduledPostListResponse:
    """
    List scheduled posts for an account or client

    Args:
        account_id: Social account UUID (optional if client_id provided)
        client_id: Client UUID (optional if account_id provided)
        limit: Max results per page
        offset: Pagination offset
        status: Optional status filter (draft, scheduled, published, etc.)

    Returns:
        ScheduledPostListResponse with paginated results

    Raises:
        HTTPException 400: If neither account_id nor client_id provided
        HTTPException 500: If query fails
    """
    try:
        # Validate: at least one ID must be provided
        if not account_id and not client_id:
            raise HTTPException(
                400,
                "Either account_id or client_id must be provided"
            )

        # Get services
        supabase = get_supabase_service()
        repo = ScheduledPostRepository(supabase)

        # Build base query
        query = supabase.client.table("scheduled_posts")\
            .select("*")\
            .eq("is_active", True)

        # Filter by account_id OR client_id
        if account_id:
            query = query.eq("account_id", account_id)
        elif client_id:
            query = query.eq("client_id", client_id)

        # Add status filter if provided
        if status:
            query = query.eq("status", status)

        # Order and paginate
        query = query.order("scheduled_date", desc=False)\
            .order("scheduled_time", desc=False)\
            .range(offset, offset + limit - 1)

        # Execute query
        response = query.execute()
        posts = [repo._map_to_entity(row) for row in response.data]

        # Count total (for pagination)
        count_query = supabase.client.table("scheduled_posts")\
            .select("id", count="exact")\
            .eq("is_active", True)

        if account_id:
            count_query = count_query.eq("account_id", account_id)
        elif client_id:
            count_query = count_query.eq("client_id", client_id)

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
