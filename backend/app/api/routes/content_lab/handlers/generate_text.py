"""
Handler de generación de texto para Content Lab.
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging

from app.api.routes.content_lab.builders.prompt_builder import (
    build_user_prompt, build_system_prompt
)
from app.services.llm.router import generate_content
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_generate_text(
    account_id: str,
    content_type: str,
    brief: str,
    language: str = "es"
) -> dict:
    """
    Handler HTTP para generación de texto.

    Workflow:
    1. Obtener client_id y contexto desde account_id
    2. Construir prompts (user + system)
    3. Llamar al router LLM
    4. Guardar resultado en DB
    5. Retornar response en formato flat

    Args:
        account_id: Social account UUID
        content_type: Tipo de contenido (caption, story, etc.)
        brief: Brief del usuario
        language: Idioma (default: es)

    Returns:
        Dict con generated_text, content_type, provider, model, cached, tokens_used

    Raises:
        HTTPException: Si falla validación o generación
    """
    try:
        # Normalize content_type aliases (frontend may send variations)
        CONTENT_TYPE_MAP = {
            "reel_script": "reel",
            "reel_tiktok": "reel",
            "ad": "anuncio",
            "hashtag": "hashtags",
            "topic": "hashtags",  # Frontend sometimes sends "topic" for hashtags
        }
        content_type = CONTENT_TYPE_MAP.get(content_type, content_type)

        # Get Supabase client
        supabase = get_supabase_service()

        # 1. Obtener client_id y contexto desde account_id
        account_response = supabase.client.table("social_accounts")\
            .select("client_id, platform, clients!inner(name, plan)")\
            .eq("id", account_id)\
            .execute()

        if not account_response.data:
            raise HTTPException(404, f"Social account {account_id} not found")

        account = account_response.data[0]
        client_id = account["client_id"]
        client_name = account["clients"]["name"]
        plan = account["clients"].get("plan") or "pro_197"
        platform = account["platform"]

        # Normalize plan to match LLM_TIERS keys
        plan_map = {
            "basico": "basico_97",
            "pro": "pro_197",
            "enterprise": "enterprise_497",
            "basico_97": "basico_97",
            "pro_197": "pro_197",
            "enterprise_497": "enterprise_497"
        }
        user_tier = plan_map.get(plan, "pro_197")  # Default to pro_197

        logger.info(
            f"Generating {content_type} for {client_name} ({user_tier}) - "
            f"brief: {brief[:50]}..."
        )

        # 2. Default context values (TODO: Fetch from context table if needed)
        context_data = {}
        audience = "General"
        tone = "professional"
        goal = "engagement"
        brand_voice = None
        keywords = []

        # 3. Construir prompts
        user_prompt = build_user_prompt(
            content_type=content_type,
            brief=brief,
            platform=platform,
            audience=audience,
            tone=tone,
            goal=goal
        )

        system_prompt = build_system_prompt(
            client_name=client_name,
            business_type=context_data.get("business_type"),
            brand_voice=brand_voice,
            keywords=keywords
        )

        # 4. Llamar al router LLM
        llm_response = await generate_content(
            content_type=content_type,
            user_tier=user_tier,
            prompt=user_prompt,
            system_prompt=system_prompt
        )

        # 5. Guardar en DB
        supabase.client.table("content_lab_generated").insert({
            "client_id": client_id,
            "social_account_id": account_id,
            "content_type": content_type,
            "content": llm_response.content,
            "provider": llm_response.provider,
            "model": llm_response.model,
            "tokens_used": llm_response.tokens_used
        }).execute()

        logger.info(
            f"Generated {content_type} for client {client_id} "
            f"via {llm_response.provider}/{llm_response.model}"
        )

        # 6. Retornar response en formato flat (igual que imagen)
        return {
            "generated_text": llm_response.content,
            "content_type": content_type,
            "provider": llm_response.provider,
            "model": llm_response.model,
            "cached": llm_response.cached,
            "tokens_used": llm_response.tokens_used
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise HTTPException(500, f"Error generando contenido: {str(e)}")
