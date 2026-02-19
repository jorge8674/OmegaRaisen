"""
Scheduled Post Repository
Data access layer for scheduled posts using Repository Pattern
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Optional, List
from datetime import date
import logging

from app.infrastructure.supabase_service import SupabaseService
from app.domain.calendar.entities import ScheduledPost

logger = logging.getLogger(__name__)


class ScheduledPostRepository:
    """Repository for scheduled posts data access"""

    def __init__(self, supabase: SupabaseService):
        """
        Initialize repository

        Args:
            supabase: Supabase service instance
        """
        self.supabase = supabase

    async def create(self, post: ScheduledPost) -> ScheduledPost:
        """
        Create new scheduled post

        Args:
            post: ScheduledPost entity to create

        Returns:
            Created ScheduledPost with generated ID

        Raises:
            Exception: If creation fails
        """
        try:
            data = {
                "client_id": post.client_id,
                "account_id": post.account_id,
                "content_lab_id": post.content_lab_id,
                "content_type": post.content_type,
                "text_content": post.text_content,
                "image_url": post.image_url,
                "hashtags": post.hashtags or [],
                "scheduled_date": str(post.scheduled_date),
                "scheduled_time": str(post.scheduled_time),
                "timezone": post.timezone,
                "status": post.status,
                "is_active": post.is_active,
            }

            response = self.supabase.client.table("scheduled_posts")\
                .insert(data)\
                .execute()

            if not response.data:
                raise Exception("Failed to create scheduled post")

            # Map response to entity
            return self._map_to_entity(response.data[0])

        except Exception as e:
            logger.error(f"Error creating scheduled post: {e}")
            raise

    async def find_by_id(self, post_id: str) -> Optional[ScheduledPost]:
        """
        Find scheduled post by ID

        Args:
            post_id: Post UUID

        Returns:
            ScheduledPost if found, None otherwise
        """
        try:
            response = self.supabase.client.table("scheduled_posts")\
                .select("*")\
                .eq("id", post_id)\
                .eq("is_active", True)\
                .execute()

            if not response.data:
                return None

            return self._map_to_entity(response.data[0])

        except Exception as e:
            logger.error(f"Error finding scheduled post {post_id}: {e}")
            return None

    async def find_by_account(
        self,
        account_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[ScheduledPost]:
        """
        Find scheduled posts by account

        Args:
            account_id: Social account UUID
            limit: Max results
            offset: Pagination offset

        Returns:
            List of ScheduledPost entities
        """
        try:
            response = self.supabase.client.table("scheduled_posts")\
                .select("*")\
                .eq("account_id", account_id)\
                .eq("is_active", True)\
                .order("scheduled_date", desc=False)\
                .order("scheduled_time", desc=False)\
                .range(offset, offset + limit - 1)\
                .execute()

            if not response.data:
                return []

            return [self._map_to_entity(row) for row in response.data]

        except Exception as e:
            logger.error(f"Error finding posts for account {account_id}: {e}")
            return []

    async def count_by_date(
        self,
        account_id: str,
        scheduled_date: date
    ) -> int:
        """
        Count active posts for account on specific date
        Uses Supabase RPC function for performance

        Args:
            account_id: Social account UUID
            scheduled_date: Date to count posts for

        Returns:
            Number of active posts
        """
        try:
            response = self.supabase.client.rpc(
                "count_posts_for_day",
                {
                    "p_account_id": account_id,
                    "p_date": str(scheduled_date)
                }
            ).execute()

            return response.data or 0

        except Exception as e:
            logger.error(f"Error counting posts: {e}")
            return 0

    async def update(self, post: ScheduledPost) -> ScheduledPost:
        """
        Update existing scheduled post

        Args:
            post: ScheduledPost entity with updates

        Returns:
            Updated ScheduledPost

        Raises:
            Exception: If update fails
        """
        try:
            data = {
                "content_type": post.content_type,
                "text_content": post.text_content,
                "image_url": post.image_url,
                "hashtags": post.hashtags or [],
                "scheduled_date": str(post.scheduled_date),
                "scheduled_time": str(post.scheduled_time),
                "timezone": post.timezone,
                "status": post.status,
                "error_message": post.error_message,
            }

            response = self.supabase.client.table("scheduled_posts")\
                .update(data)\
                .eq("id", post.id)\
                .execute()

            if not response.data:
                raise Exception("Failed to update scheduled post")

            return self._map_to_entity(response.data[0])

        except Exception as e:
            logger.error(f"Error updating scheduled post {post.id}: {e}")
            raise

    async def delete(self, post_id: str) -> bool:
        """
        Soft delete scheduled post (set is_active=False)

        Args:
            post_id: Post UUID

        Returns:
            True if deleted successfully

        Raises:
            Exception: If delete fails
        """
        try:
            response = self.supabase.client.table("scheduled_posts")\
                .update({"is_active": False})\
                .eq("id", post_id)\
                .execute()

            return bool(response.data)

        except Exception as e:
            logger.error(f"Error deleting scheduled post {post_id}: {e}")
            raise

    def _map_to_entity(self, row: dict) -> ScheduledPost:
        """Map database row to ScheduledPost entity"""
        from datetime import datetime

        return ScheduledPost(
            id=row.get("id"),
            client_id=row.get("client_id"),
            account_id=row.get("account_id"),
            content_lab_id=row.get("content_lab_id"),
            content_type=row.get("content_type"),
            text_content=row.get("text_content"),
            image_url=row.get("image_url"),
            hashtags=row.get("hashtags", []),
            scheduled_date=datetime.fromisoformat(row["scheduled_date"]).date() if row.get("scheduled_date") else None,
            scheduled_time=datetime.fromisoformat(f"2000-01-01T{row['scheduled_time']}").time() if row.get("scheduled_time") else None,
            timezone=row.get("timezone", "America/Puerto_Rico"),
            status=row.get("status", "draft"),
            is_active=row.get("is_active", True),
            published_at=datetime.fromisoformat(row["published_at"]) if row.get("published_at") else None,
            error_message=row.get("error_message"),
            created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row.get("updated_at") else None,
        )
