"""
Content Lab Context Service — Loads client context + brand voice.
DDD: Application Service layer - orchestrates domain data loading.
Strict <200L per file.
"""
from typing import Dict, Any, Optional, Tuple
from app.infrastructure.supabase_service import SupabaseService
from app.infrastructure.repositories.client_context_repository import ClientContextRepository
import logging

logger = logging.getLogger(__name__)


class ContentLabContextService:
    """
    Loads and merges client context with brand voice data.

    Merges two data sources:
    1. client_context table (target_audience, niche, themes)
    2. client_context.brand_file (JSONB with voice rules)
    """

    def __init__(self, supabase: SupabaseService):
        self.supabase = supabase
        self.context_repo = ClientContextRepository(supabase)

    def load_context_with_brand_voice(
        self, client_id: str
    ) -> Tuple[Dict[str, Any], str, str, list, Optional[str]]:
        """
        Loads client context merged with brand voice rules.

        Returns:
            Tuple of (context_data, audience, tone, keywords, brand_voice)
        """
        # Load client context
        client_context = self.context_repo.find_by_client_id(client_id)

        # Load brand voice from client_context table (custom_instructions JSONB)
        brand_file_response = self.supabase.client.table("client_context")\
            .select("custom_instructions, vertical")\
            .eq("client_id", client_id)\
            .execute()

        brand_file = {}
        if brand_file_response.data and brand_file_response.data[0].get("custom_instructions"):
            brand_file = brand_file_response.data[0]["custom_instructions"]
            logger.info(f"Loaded brand voice from custom_instructions for client {client_id}")

        # Extract brand voice rules
        brand_voice_rules = self._extract_brand_voice_rules(brand_file)

        # Merge context with brand_file
        if client_context and client_context.has_context():
            audience = client_context.target_audience or "General"
            tone = brand_voice_rules["primary_tone"]
            brand_voice = client_context.brand_voice
            keywords = client_context.content_themes or []

            context_data = {
                "business_type": (
                    brand_file_response.data[0].get("vertical")
                    if brand_file_response.data
                    else client_context.niche
                ),
                "preferred_formats": client_context.preferred_formats,
                "brand_voice_rules": brand_voice_rules
            }

            logger.info(f"Using enriched context + brand voice for client {client_id}")
        else:
            # Use brand_file only if no context available
            context_data = {
                "business_type": (
                    brand_file_response.data[0].get("vertical")
                    if brand_file_response.data
                    else "generic"
                ),
                "brand_voice_rules": brand_voice_rules
            }
            audience = "General"
            tone = brand_voice_rules["primary_tone"]
            brand_voice = None
            keywords = []

            logger.info(f"Using brand_file only for client {client_id}")

        return context_data, audience, tone, keywords, brand_voice

    def _extract_brand_voice_rules(self, brand_file: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts brand voice rules from brand_file JSONB.

        Schema:
        {
          "voice": {
            "primary_tone": "professional | casual | aspiracional",
            "language_style": "formal | semiformal | coloquial",
            "personality_traits": ["confiable", "innovador"],
            "emojis_allowed": true
          },
          "do": ["Use testimonials", "Mention location"],
          "dont": ["Mention competitors", "Use anglicisms"]
        }
        """
        brand_voice_data = brand_file.get("voice", {})

        return {
            "primary_tone": brand_voice_data.get("primary_tone", "professional"),
            "language_style": brand_voice_data.get("language_style", "semiformal"),
            "personality_traits": brand_voice_data.get("personality_traits", []),
            "emojis_allowed": brand_voice_data.get("emojis_allowed", False),
            "do": brand_file.get("do", []),
            "dont": brand_file.get("dont", [])
        }
