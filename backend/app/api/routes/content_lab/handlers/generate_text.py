"""
Handler de generación de texto para Content Lab.
Filosofía: No velocity, only precision 🐢💎
DDD: API Interface layer - thin orchestration over services.
Strict <200L per file.
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging

from app.services.ai_providers import AIProviders
from app.infrastructure.supabase_service import get_supabase_service
from app.services.content_lab_context_service import ContentLabContextService
from app.services.content_lab_prompt_service import ContentLabPromptService

logger = logging.getLogger(__name__)

# Content type aliases (frontend variations)
CONTENT_TYPE_MAP = {
    "reel_script": "reel",
    "reel_tiktok": "reel",
    "ad": "anuncio",
    "hashtag": "hashtags",
    "topic": "hashtags",
}


async def handle_generate_text(
    account_id: str, content_type: str, brief: str,
    language: str = "es", director: str = "REX"
) -> dict:
    """
    Generates text using Prompt Vault + AI providers.
    Workflow: Load context → Select prompt → Generate → Save → Return
    """
    try:
        # Map organizational agents to AI Directors
        AGENT_TO_DIRECTOR = {
            "RAFA": "REX",  # RAFA (Content Creator) → REX (GPT-4o-mini, fast)
            "ATLAS": "ATLAS",  # Pass-through
            "NOVA": "NOVA"  # Pass-through
        }
        director_normalized = AGENT_TO_DIRECTOR.get(director.upper(), director.upper())

        # Normalize content_type
        content_type = CONTENT_TYPE_MAP.get(content_type, content_type)

        # Get Supabase client
        supabase = get_supabase_service()

        # 1. Obtener client_id y platform - intenta social_accounts, luego clients
        client_id, client_name, plan, platform, social_account_id = (
            _lookup_client_and_account(supabase, account_id)
        )

        # Normalize plan to match LLM_TIERS
        user_tier = _normalize_plan(plan)

        logger.info(
            f"Generating {content_type} for {client_name} ({user_tier}) - "
            f"brief: {brief[:50]}..."
        )

        # 2. Load client context + brand voice
        context_service = ContentLabContextService(supabase)
        context_data, audience, tone, keywords, brand_voice = (
            context_service.load_context_with_brand_voice(client_id)
        )

        # 3. Select and build prompts (vault vs default)
        prompt_service = ContentLabPromptService(supabase)
        vertical = context_data.get("business_type") or "generic"

        user_prompt, system_prompt, vault_used = (
            await prompt_service.select_and_build_prompts(
                content_type=content_type,
                vertical=vertical,
                platform=platform,
                brief=brief,
                client_name=client_name,
                audience=audience,
                tone=tone,
                language=language,
                goal="engagement",
                context_data=context_data,
                brand_voice=brand_voice,
                keywords=keywords
            )
        )

        # 4. Llamar al AI provider seleccionado (multi-engine)
        ai_providers = AIProviders()
        llm_response = await ai_providers.generate(
            director=director_normalized,
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=2000,
            temperature=0.7
        )

        # 5. Guardar en DB (including vault_prompt_id for tracking)
        supabase.client.table("content_lab_generated").insert({
            "client_id": client_id,
            "social_account_id": social_account_id,
            "content_type": content_type,
            "content": llm_response["content"],
            "provider": llm_response["provider"],
            "model": llm_response["model"],
            "tokens_used": llm_response["tokens_used"],
            "vault_prompt_id": vault_used["id"] if vault_used else None
        }).execute()

        logger.info(
            f"Generated {content_type} for client {client_id} "
            f"via {director_normalized} ({llm_response['provider']}/{llm_response['model']})"
        )

        # 6. Retornar response en formato flat (with vault metadata)
        return {
            "generated_text": llm_response["content"],
            "content_type": content_type,
            "provider": llm_response["provider"],
            "model": llm_response["model"],
            "director": director_normalized,
            "cached": False,
            "tokens_used": llm_response["tokens_used"],
            "vault_prompt_used": vault_used
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise HTTPException(500, f"Error generando contenido: {str(e)}")


def _lookup_client_and_account(supabase, account_id: str) -> tuple:
    """Lookup client data. Tries social_accounts first, then clients table."""
    # Try social_accounts first
    account_response = supabase.client.table("social_accounts")\
        .select("client_id, platform, clients!inner(name, plan)")\
        .eq("id", account_id)\
        .execute()

    if account_response.data:
        account = account_response.data[0]
        return (
            account["client_id"],
            account["clients"]["name"],
            account["clients"].get("plan") or "pro_197",
            account["platform"],
            account_id
        )

    # Fallback: try as client_id
    client_response = supabase.client.table("clients")\
        .select("id, name, plan")\
        .eq("id", account_id)\
        .execute()

    if not client_response.data:
        raise HTTPException(404, f"Account or client {account_id} not found")

    client = client_response.data[0]

    # Find first social account for this client
    social_resp = supabase.client.table("social_accounts")\
        .select("id, platform")\
        .eq("client_id", client["id"])\
        .limit(1)\
        .execute()

    if not social_resp.data:
        raise HTTPException(400, f"Client {client['id']} has no social accounts")

    return (
        client["id"],
        client["name"],
        client.get("plan") or "pro_197",
        social_resp.data[0]["platform"],
        social_resp.data[0]["id"]
    )


def _normalize_plan(plan: str) -> str:
    """Normalize plan to match LLM_TIERS keys"""
    plan_map = {
        "basico": "basico_97",
        "pro": "pro_197",
        "enterprise": "enterprise_497",
        "basico_97": "basico_97",
        "pro_197": "pro_197",
        "enterprise_497": "enterprise_497"
    }
    return plan_map.get(plan, "pro_197")
