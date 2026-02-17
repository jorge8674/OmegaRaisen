"""
Content Lab Router
AI-powered content generation using account context.
POST   /content-lab/generate/          - Generate content for a social account
GET    /content-lab/?account_id={id}   - List generated content
PATCH  /content-lab/{id}/save/         - Toggle save status
DELETE /content-lab/{id}/              - Delete generated content
"""
from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional
import logging
from datetime import datetime, timezone
import httpx
import os

from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.supabase_service import get_supabase_service
from .models import (
    ContentGenerateRequest, ContentGenerateResponse,
    ContentListResponse, GeneratedContentProfile
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/content-lab", tags=["content-lab"])

# Content type prompts mapping
CONTENT_TYPE_PROMPTS = {
    "post": "Crea un post completo para redes sociales",
    "caption": "Crea un caption atractivo y conciso",
    "story": "Crea un script corto para Story (máximo 15 segundos)",
    "ad": "Crea un anuncio publicitario persuasivo",
    "reel_script": "Crea un script detallado para Reel/TikTok",
    "bio": "Crea una bio profesional y atractiva",
    "hashtags": "Genera 20-30 hashtags relevantes y estratégicos",
    "email": "Crea un email de marketing completo",
}


def build_system_prompt(context: dict, platform: str, content_type: str) -> str:
    """Build system prompt from account context"""
    business_name = context.get("business_name", "la empresa")
    industry = context.get("industry", "")
    description = context.get("business_description", "")
    tone = context.get("communication_tone", "professional")
    goal = context.get("primary_goal", "awareness")
    keywords = context.get("keywords", [])
    forbidden_words = context.get("forbidden_words", [])
    forbidden_topics = context.get("forbidden_topics", [])

    tone_map = {
        "professional": "profesional y confiable",
        "casual": "casual y cercano",
        "inspirational": "inspirador y motivador",
        "educational": "educativo e informativo",
        "humorous": "humorístico y entretenido",
        "energetic": "energético y dinámico",
    }
    goal_map = {
        "sales": "generar ventas y conversiones",
        "awareness": "aumentar el conocimiento de marca",
        "community": "construir y fortalecer comunidad",
        "leads": "capturar leads y contactos",
        "retention": "fidelizar clientes existentes",
    }

    system = f"""Eres un experto en marketing digital y contenido para redes sociales.

CLIENTE: {business_name}
INDUSTRIA: {industry}
DESCRIPCIÓN: {description}
PLATAFORMA: {platform}
TONO: {tone_map.get(tone, tone)}
OBJETIVO: {goal_map.get(goal, goal)}
"""
    if keywords:
        system += f"KEYWORDS A INCLUIR: {', '.join(keywords[:10])}\n"
    if forbidden_words:
        system += f"PALABRAS PROHIBIDAS (NO usar): {', '.join(forbidden_words)}\n"
    if forbidden_topics:
        system += f"TEMAS PROHIBIDOS (evitar): {', '.join(forbidden_topics)}\n"

    system += f"""
INSTRUCCIONES:
- {CONTENT_TYPE_PROMPTS.get(content_type, 'Crea contenido de calidad')}
- Adapta el contenido específicamente para {platform}
- Mantén el tono {tone_map.get(tone, tone)} consistentemente
- El objetivo principal es {goal_map.get(goal, goal)}
- Escribe directamente el contenido, sin explicaciones previas
- En español latinoamericano, adaptado para Puerto Rico si aplica
"""
    return system


@router.post("/generate/", response_model=ContentGenerateResponse)
async def generate_content(
    request: ContentGenerateRequest,
    authorization: Optional[str] = Header(None)
) -> ContentGenerateResponse:
    """
    Generate AI content for a social account using its context.
    Uses OpenAI GPT-4o-mini with account context for personalization.
    """
    try:
        user = await get_current_user(authorization)
        supabase = get_supabase_service()

        # 1. Get social account
        account_result = supabase.client.table("social_accounts")\
            .select("*")\
            .eq("id", request.account_id)\
            .eq("is_active", True)\
            .single()\
            .execute()

        if not account_result.data:
            raise HTTPException(status_code=404, detail="Cuenta social no encontrada")

        account = account_result.data
        platform = account.get("platform", "instagram")

        # 2. Get context
        context = {}
        context_id = account.get("context_id")
        if context_id:
            ctx_result = supabase.client.table("client_context")\
                .select("*")\
                .eq("id", context_id)\
                .single()\
                .execute()
            if ctx_result.data:
                context = ctx_result.data

        # 3. Build prompts
        system_prompt = build_system_prompt(context, platform, request.content_type)
        user_message = request.prompt
        if request.extra_instructions:
            user_message += f"\n\nInstrucciones adicionales: {request.extra_instructions}"

        # 4. Call OpenAI API
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key no configurada"
            )

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    "max_tokens": 1500,
                    "temperature": 0.7,
                },
            )

        if response.status_code != 200:
            logger.error(f"OpenAI error: {response.text}")
            raise HTTPException(
                status_code=502,
                detail="Error al generar contenido con IA"
            )

        ai_data = response.json()
        generated_text = ai_data["choices"][0]["message"]["content"]
        tokens_used = ai_data.get("usage", {}).get("total_tokens", 0)

        # 5. Save to DB
        db_result = supabase.client.table("generated_content").insert({
            "client_id": account.get("client_id"),
            "account_id": request.account_id,
            "context_id": context_id,
            "content_type": request.content_type,
            "platform": platform,
            "prompt": request.prompt,
            "generated_text": generated_text,
            "tokens_used": tokens_used,
            "model_used": "gpt-4o-mini",
            "is_saved": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()

        if not db_result.data:
            raise HTTPException(
                status_code=500,
                detail="Error guardando contenido generado"
            )

        logger.info(
            f"Content generated: {request.content_type} for {platform} "
            f"({tokens_used} tokens)"
        )

        return ContentGenerateResponse(
            success=True,
            data=GeneratedContentProfile(**db_result.data[0]),
            message="Contenido generado exitosamente"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating content: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar contenido: {str(e)}"
        )


@router.get("/", response_model=ContentListResponse)
async def list_generated_content(
    account_id: Optional[str] = Query(None, description="Filter by account"),
    client_id: Optional[str] = Query(None, description="Filter by client"),
    content_type: Optional[str] = Query(None, description="Filter by type"),
    limit: int = Query(default=20, le=100, description="Max results"),
    authorization: Optional[str] = Header(None)
) -> ContentListResponse:
    """
    List generated content filtered by account or client.
    Returns recent generations with pagination.
    """
    try:
        user = await get_current_user(authorization)
        supabase = get_supabase_service()

        query = supabase.client.table("generated_content")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(limit)

        if account_id:
            query = query.eq("account_id", account_id)
        elif client_id:
            query = query.eq("client_id", client_id)

        if content_type:
            query = query.eq("content_type", content_type)

        result = query.execute()
        items = result.data or []

        return ContentListResponse(
            success=True,
            data=[GeneratedContentProfile(**item) for item in items],
            total=len(items),
            message=f"Found {len(items)} item(s)"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing content: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error al obtener historial"
        )


@router.patch("/{content_id}/save/", response_model=ContentGenerateResponse)
async def toggle_save_content(
    content_id: str,
    authorization: Optional[str] = Header(None)
) -> ContentGenerateResponse:
    """
    Toggle saved status of generated content.
    Allows users to mark content as saved/favorite.
    """
    try:
        user = await get_current_user(authorization)
        supabase = get_supabase_service()

        # Get current status
        current = supabase.client.table("generated_content")\
            .select("is_saved")\
            .eq("id", content_id)\
            .single()\
            .execute()

        if not current.data:
            raise HTTPException(status_code=404, detail="Contenido no encontrado")

        # Toggle status
        new_status = not current.data["is_saved"]
        result = supabase.client.table("generated_content")\
            .update({"is_saved": new_status})\
            .eq("id", content_id)\
            .execute()

        logger.info(f"Content {content_id} saved status: {new_status}")

        return ContentGenerateResponse(
            success=True,
            data=GeneratedContentProfile(**result.data[0]),
            message="Guardado" if new_status else "Removido de guardados"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling save: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error actualizando estado"
        )


@router.delete("/{content_id}/", response_model=ContentGenerateResponse)
async def delete_content(
    content_id: str,
    authorization: Optional[str] = Header(None)
) -> ContentGenerateResponse:
    """
    Delete generated content permanently.
    """
    try:
        user = await get_current_user(authorization)
        supabase = get_supabase_service()

        result = supabase.client.table("generated_content")\
            .delete()\
            .eq("id", content_id)\
            .execute()

        logger.info(f"Content {content_id} deleted")

        return ContentGenerateResponse(
            success=True,
            message="Contenido eliminado"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting content: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error eliminando contenido"
        )
