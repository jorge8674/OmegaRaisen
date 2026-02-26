"""
Handler de generación/edición de imágenes para Content Lab.
- DALL-E 3: Generación desde cero
- GPT-Image-1: Edición con imágenes base
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
import logging
import os
import base64
import io
import httpx
from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.ai.openai_service import openai_service

logger = logging.getLogger(__name__)

async def handle_generate_image(
    account_id: str, prompt: str, style: str = "realistic", attachments: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Handler HTTP para generación/edición de imágenes.
    - Si hay attachments → editar con GPT-Image-1
    - Sin attachments → generar con DALL-E 3
    """
    try:
        supabase = get_supabase_service()
        # 1. Obtener client info
        account_response = supabase.client.table("social_accounts")\
            .select("client_id, platform, clients!inner(name, plan)")\
            .eq("id", account_id)\
            .execute()
        if not account_response.data:
            raise HTTPException(404, f"Social account {account_id} not found")
        account = account_response.data[0]
        client_id = account["client_id"]
        client_name = account["clients"]["name"]

        # 2. Detectar si es edición o generación
        image_attachments = [a for a in (attachments or []) if a.get("type") == "image" or "base64" in a]
        if image_attachments:
            logger.info(f"Editing image for {client_name} with GPT-Image-1 ({len(image_attachments)} images)")
            result = await _edit_with_gpt_image1(prompt, image_attachments, style)
        else:
            logger.info(f"Generating image for {client_name} with DALL-E 3")
            result = await _generate_with_dalle3(prompt, style)

        # 3. Guardar en DB
        try:
            supabase.client.table("content_lab_generated").insert({
                "client_id": client_id,
                "social_account_id": account_id,
                "content_type": "image",
                "content": result["image_url"],
                "provider": result["provider"],
                "model": result["model"],
                "tokens_used": 0,
            }).execute()
        except Exception as db_error:
            logger.warning(f"Failed to save image to DB: {db_error}")

        logger.info(f"Image {result['mode']} for client {client_id} via {result['model']}")

        # 4. Retornar response en formato flat
        return {
            "generated_text": result["image_url"],
            "content_type": "image",
            "provider": result["provider"],
            "model": result["model"],
            "mode": result["mode"],
            "cached": False,
            "tokens_used": 0
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(500, f"Error generando imagen: {str(e)}")

async def _edit_with_gpt_image1(prompt: str, images: List[Dict[str, Any]], style: str) -> Dict[str, Any]:
    """
    Edita imagen(es) con GPT-Image-1.
    Soporta: agregar logos, modificar elementos, combinar imágenes, cambiar fondo, etc.
    """
    # Preparar imágenes como bytes
    image_files = []
    for img in images[:4]:  # Máximo 4 imágenes
        base64_data = img.get("base64", "")
        if not base64_data:
            continue
        # Remover prefijo data:image/xxx;base64, si existe
        if "," in base64_data:
            base64_data = base64_data.split(",", 1)[1]
        try:
            image_bytes = base64.b64decode(base64_data)
            image_files.append(("image", ("image.png", io.BytesIO(image_bytes), "image/png")))
        except Exception as e:
            logger.warning(f"Failed to decode base64 image: {e}")
            continue

    if not image_files:
        # Fallback a DALL-E 3 si no hay imágenes válidas
        logger.warning("No valid images for editing, falling back to DALL-E 3")
        return await _generate_with_dalle3(prompt, style)

    # Construir prompt mejorado
    enhanced_prompt = _enhance_prompt(prompt, style)

    # Llamar GPT-Image-1 edit endpoint
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/images/edits",
                headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"},
                data={"model": "gpt-image-1", "prompt": enhanced_prompt, "n": 1, "size": "1024x1024"},
                files=image_files
            )
            response.raise_for_status()
            result = response.json()
    except Exception as e:
        logger.error(f"GPT-Image-1 edit failed: {e}")
        return await _generate_with_dalle3(prompt, style)  # Fallback a DALL-E 3

    # GPT-Image-1 puede retornar base64 o URL
    if result["data"][0].get("b64_json"):
        b64 = result["data"][0]["b64_json"]
        image_url = f"data:image/png;base64,{b64}"
    else:
        image_url = result["data"][0].get("url", "")

    return {"image_url": image_url, "provider": "openai", "model": "gpt-image-1", "mode": "edit"}

async def _generate_with_dalle3(prompt: str, style: str) -> Dict[str, Any]:
    """Generación nueva con DALL-E 3 (sin imágenes base)"""
    enhanced_prompt = _enhance_prompt(prompt, style)
    try:
        image_urls = await openai_service.generate_image(
            prompt=enhanced_prompt, n=1, size="1024x1024", quality="standard"
        )
        if not image_urls:
            raise Exception("DALL-E 3 returned no images")
        return {"image_url": image_urls[0], "provider": "openai", "model": "dall-e-3", "mode": "generate"}
    except Exception as e:
        logger.error(f"DALL-E 3 generation failed: {e}")
        raise HTTPException(500, f"DALL-E 3 generation failed: {str(e)}")

def _enhance_prompt(prompt: str, style: str) -> str:
    """Mejora el prompt según el estilo solicitado"""
    style_suffixes = {
        "realistic": ", photorealistic, high quality, professional photography",
        "cartoon": ", cartoon style, vibrant colors, playful illustration",
        "minimal": ", minimalist design, clean lines, simple composition"
    }
    suffix = style_suffixes.get(style, style_suffixes["realistic"])
    enhanced = f"{prompt}{suffix}"
    # DALL-E 3 limit: 4000 chars
    if len(enhanced) > 4000:
        max_prompt_len = 4000 - len(suffix)
        enhanced = f"{prompt[:max_prompt_len]}{suffix}"
    return enhanced
