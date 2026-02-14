"""
Supabase Service
Handles Supabase database and storage operations
"""
import logging
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger(__name__)


class SupabaseService:
    """Service for Supabase operations"""

    def __init__(self):
        """Initialize Supabase client"""
        try:
            self.client: Client = create_client(
                settings.supabase_url,
                settings.supabase_service_role_key  # Admin access
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise

    # ═══════════════════════════════════════════════════════════
    # RESELLERS
    # ═══════════════════════════════════════════════════════════

    async def create_reseller(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new reseller"""
        try:
            response = self.client.table('resellers').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating reseller: {e}")
            raise

    async def get_reseller(self, reseller_id: str) -> Optional[Dict[str, Any]]:
        """Get reseller by ID"""
        try:
            response = self.client.table('resellers').select('*').eq('id', reseller_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting reseller: {e}")
            raise

    async def get_reseller_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get reseller by slug"""
        try:
            response = self.client.table('resellers').select('*').eq('slug', slug).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting reseller by slug: {e}")
            raise

    async def get_all_resellers(self) -> List[Dict[str, Any]]:
        """Get all resellers"""
        try:
            response = self.client.table('resellers').select('*').order('created_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting all resellers: {e}")
            raise

    async def update_reseller(self, reseller_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update reseller"""
        try:
            response = self.client.table('resellers').update(data).eq('id', reseller_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating reseller: {e}")
            raise

    # ═══════════════════════════════════════════════════════════
    # RESELLER BRANDING
    # ═══════════════════════════════════════════════════════════

    async def create_branding(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create reseller branding"""
        try:
            response = self.client.table('reseller_branding').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating branding: {e}")
            raise

    async def get_branding(self, reseller_id: str) -> Optional[Dict[str, Any]]:
        """Get reseller branding"""
        try:
            response = self.client.table('reseller_branding').select('*').eq('reseller_id', reseller_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting branding: {e}")
            raise

    async def update_branding(self, reseller_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update reseller branding"""
        try:
            # Check if branding exists
            existing = await self.get_branding(reseller_id)

            if existing:
                # Update existing
                response = self.client.table('reseller_branding').update(data).eq('reseller_id', reseller_id).execute()
            else:
                # Create new
                data['reseller_id'] = reseller_id
                response = self.client.table('reseller_branding').insert(data).execute()

            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating branding: {e}")
            raise

    # ═══════════════════════════════════════════════════════════
    # RESELLER AGENTS
    # ═══════════════════════════════════════════════════════════

    async def create_reseller_agent(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create reseller agent"""
        try:
            response = self.client.table('reseller_agents').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating reseller agent: {e}")
            raise

    async def get_reseller_agents(self, reseller_id: str) -> List[Dict[str, Any]]:
        """Get all agents for a reseller"""
        try:
            response = self.client.table('reseller_agents').select('*').eq('reseller_id', reseller_id).eq('status', 'active').execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting reseller agents: {e}")
            raise

    # ═══════════════════════════════════════════════════════════
    # CLIENTS
    # ═══════════════════════════════════════════════════════════

    async def get_reseller_clients(self, reseller_id: str) -> List[Dict[str, Any]]:
        """Get all clients for a reseller"""
        try:
            response = self.client.table('clients').select('*').eq('reseller_id', reseller_id).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting reseller clients: {e}")
            raise

    async def assign_client_to_reseller(self, client_id: str, reseller_id: str) -> Dict[str, Any]:
        """Assign existing client to reseller"""
        try:
            response = self.client.table('clients').update({'reseller_id': reseller_id}).eq('id', client_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error assigning client to reseller: {e}")
            raise

    # ═══════════════════════════════════════════════════════════
    # STORAGE - MEDIA UPLOAD
    # ═══════════════════════════════════════════════════════════

    async def upload_media(
        self,
        bucket: str,
        file_path: str,
        file_data: bytes,
        content_type: str
    ) -> str:
        """
        Upload media file to Supabase Storage

        Args:
            bucket: Storage bucket name
            file_path: Path within bucket (e.g., 'reseller_slug/hero.mp4')
            file_data: File binary data
            content_type: MIME type

        Returns:
            Public URL of uploaded file
        """
        try:
            # Upload file
            response = self.client.storage.from_(bucket).upload(
                path=file_path,
                file=file_data,
                file_options={"content-type": content_type, "upsert": "true"}
            )

            # Get public URL
            public_url = self.client.storage.from_(bucket).get_public_url(file_path)

            logger.info(f"Media uploaded successfully: {public_url}")
            return public_url
        except Exception as e:
            logger.error(f"Error uploading media: {e}")
            raise

    async def delete_media(self, bucket: str, file_path: str) -> bool:
        """Delete media file from storage"""
        try:
            self.client.storage.from_(bucket).remove([file_path])
            logger.info(f"Media deleted: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting media: {e}")
            raise


# Global instance
supabase_service = SupabaseService()
