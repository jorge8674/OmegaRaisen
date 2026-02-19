"""
Handler de generación de imágenes para Content Lab.
Usa DALL-E 3 para generar imágenes según tier del cliente
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging

from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.ai.openai_service import openai_service

logger = logging.getLogger(__name__)


async def handle_generate_image(
    account_id: str,
    prompt: str,
    style: str = "realistic"
) -> Dict[str, Any]:
    """
    Handler HTTP para generación de imágenes con DALL-E 3.

    Workflow:
    1. Obtener client_id y plan desde account_id
    2. Construir prompt mejorado según estilo
    3. Llamar a DALL-E 3 (OpenAI)
    4. Guardar resultado en DB
    5. Retornar URL + metadata en formato flat

    Args:
        account_id: Social account UUID
        prompt: Descripción de la imagen
        style: Estilo (realistic, cartoon, minimal)

    Returns:
        Dict con generated_text, content_type, provider, model, cached, tokens_used

    Raises:
        HTTPException 404: Account no encontrado
        HTTPException 500: Error en generación
    """
    try:
        # Get Supabase client
        supabase = get_supabase_service()

        # 1. Obtener client info desde account_id
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

        logger.info(
            f"Generating image for {client_name} ({plan}) - "
            f"style: {style}, prompt: {prompt[:50]}..."
        )

        # 2. Construir prompt mejorado según estilo
        enhanced_prompt = _enhance_prompt(prompt, style)

        # 3. Llamar a DALL-E 3
        try:
            image_urls = await openai_service.generate_image(
                prompt=enhanced_prompt,
                n=1,
                size="1024x1024",
                quality="standard"  # "standard" o "hd" según tier
            )

            if not image_urls:
                raise Exception("DALL-E 3 returned no images")

            image_url = image_urls[0]

        except Exception as e:
            logger.error(f"DALL-E 3 generation failed: {e}")
            raise HTTPException(
                500,
                f"Image generation failed: {str(e)}"
            )

        # 4. Guardar en DB
        try:
            supabase.client.table("content_lab_generated").insert({
                "client_id": client_id,
                "social_account_id": account_id,
                "content_type": "image",
                "content": image_url,  # Store URL as content
                "provider": "openai",
                "model": "dall-e-3",
                "tokens_used": 0,  # DALL-E doesn't use tokens
            }).execute()
        except Exception as db_error:
            # Log but don't fail - image was generated successfully
            logger.warning(f"Failed to save image to DB: {db_error}")

        logger.info(
            f"Image generated successfully for client {client_id} - "
            f"URL: {image_url[:50]}..."
        )

        # 5. Retornar response en formato que frontend espera
        return {
            "generated_text": image_url,  # URL va en generated_text
            "content_type": "image",      # CRÍTICO: debe ser exactamente "image"
            "provider": "openai",
            "model": "dall-e-3",
            "cached": False,
            "tokens_used": 0
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(500, f"Error generando imagen: {str(e)}")


def _enhance_prompt(prompt: str, style: str) -> str:
    """
    Mejora el prompt según el estilo solicitado

    Args:
        prompt: Prompt original del usuario
        style: Estilo (realistic, cartoon, minimal)

    Returns:
        Prompt mejorado para DALL-E 3
    """
    style_suffixes = {
        "realistic": ", photorealistic, high quality, professional photography",
        "cartoon": ", cartoon style, vibrant colors, playful illustration",
        "minimal": ", minimalist design, clean lines, simple composition"
    }

    suffix = style_suffixes.get(style, style_suffixes["realistic"])

    # Ensure prompt doesn't exceed DALL-E 3 limits (4000 chars)
    enhanced = f"{prompt}{suffix}"

    if len(enhanced) > 4000:
        # Truncate original prompt if too long
        max_prompt_len = 4000 - len(suffix)
        enhanced = f"{prompt[:max_prompt_len]}{suffix}"

    return enhanced
