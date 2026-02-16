"""
Client Repository
Database operations for client management
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import logging
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

# Client fields (excludes password_hash for security)
CLIENT_SELECT = (
    "id, email, name, phone, company, plan, role, status, "
    "subscription_status, trial_active, trial_ends_at, "
    "reseller_id, avatar_url, stripe_customer_id, notes, "
    "created_at, updated_at"
)


class ClientRepository:
    """Repository for client CRUD operations"""

    def __init__(self):
        self.service = get_supabase_service()

    async def list_clients(
        self,
        role: str,
        authenticated_id: str,
        reseller_id: Optional[str] = None,
        status: Optional[str] = None,
        plan: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List clients with role-based filtering."""
        try:
            query = self.service.client.table("clients")\
                .select(CLIENT_SELECT)\
                .neq("status", "deleted")

            if role == "reseller":
                query = query.eq("reseller_id", reseller_id)

            if status:
                query = query.eq("status", status)
            if plan:
                query = query.eq("plan", plan)
            if search:
                query = query.or_(f"name.ilike.%{search}%,email.ilike.%{search}%")

            query = query.order("created_at", desc=True)

            response = query.execute()
            return response.data if response.data else []

        except Exception as e:
            logger.error(f"Error listing clients: {e}")
            raise

    async def create_client(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new client."""
        try:
            response = self.service.client.table("clients")\
                .insert(data)\
                .execute()

            if not response.data or len(response.data) == 0:
                raise Exception("Failed to create client")

            client = response.data[0]
            client.pop("password_hash", None)

            logger.info(f"Client created: {data.get('email')}")
            return client

        except Exception as e:
            logger.error(f"Error creating client: {e}")
            raise

    async def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get client by ID (excludes deleted)."""
        try:
            response = self.service.client.table("clients")\
                .select(CLIENT_SELECT)\
                .eq("id", client_id)\
                .neq("status", "deleted")\
                .execute()

            return response.data[0] if response.data else None

        except Exception as e:
            logger.error(f"Error getting client: {e}")
            raise

    async def get_client_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get client by email (includes deleted for duplicate check)."""
        try:
            response = self.service.client.table("clients")\
                .select("*")\
                .eq("email", email)\
                .execute()

            return response.data[0] if response.data else None

        except Exception as e:
            logger.error(f"Error getting client by email: {e}")
            raise

    async def update_client(
        self,
        client_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update client fields."""
        try:
            data["updated_at"] = datetime.now(timezone.utc).isoformat()

            response = self.service.client.table("clients")\
                .update(data)\
                .eq("id", client_id)\
                .execute()

            if not response.data or len(response.data) == 0:
                raise Exception("Client not found or update failed")

            client = response.data[0]
            client.pop("password_hash", None)

            logger.info(f"Client updated: {client_id}")
            return client

        except Exception as e:
            logger.error(f"Error updating client: {e}")
            raise

    async def soft_delete_client(self, client_id: str) -> bool:
        """Soft delete: status = deleted."""
        try:
            response = self.service.client.table("clients")\
                .update({
                    "status": "deleted",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                })\
                .eq("id", client_id)\
                .execute()

            if not response.data or len(response.data) == 0:
                return False

            logger.info(f"Client soft deleted: {client_id}")
            return True

        except Exception as e:
            logger.error(f"Error soft deleting client: {e}")
            raise


# Global instance
client_repository = ClientRepository()
