"""
Router multi-LLM con fallback automático.
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Optional
import logging
from litellm import completion

from app.domain.llm.types import (
    ContentType, UserTier, LLMResponse
)
from app.domain.llm.config import LLM_TIERS

logger = logging.getLogger(__name__)

async def generate_content(
    content_type: ContentType,
    user_tier: UserTier,
    prompt: str,
    system_prompt: Optional[str] = None,
    **kwargs
) -> LLMResponse:
    """
    Genera contenido usando el modelo apropiado según tier y tipo.

    Args:
        content_type: Tipo de contenido (caption, script, etc.)
        user_tier: Tier del cliente (basico_97, pro_197, enterprise_497)
        prompt: Prompt del usuario
        system_prompt: Prompt del sistema (opcional)
        **kwargs: Argumentos adicionales para litellm

    Returns:
        LLMResponse con contenido, provider, modelo, cache status

    Raises:
        Exception: Si todos los modelos del fallback chain fallan
    """
    # Obtener configuración del tier
    tier_config = LLM_TIERS[user_tier]

    # Obtener config específica del tipo de contenido
    content_config = getattr(tier_config, content_type, None)

    if not content_config:
        raise ValueError(
            f"Content type '{content_type}' no configurado para tier '{user_tier}'"
        )

    # Construir mensajes
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        # Llamada a litellm con fallback automático
        response = await completion(
            model=content_config.primary,
            messages=messages,
            fallbacks=content_config.fallback,
            caching=content_config.cache,
            **kwargs
        )

        # Extraer metadata
        provider = response.get("_hidden_params", {}).get(
            "model_provider", "unknown"
        )
        model = response.model
        cached = response.get("_hidden_params", {}).get("cache_hit", False)

        # Calcular tokens usados
        usage = response.get("usage", {})
        tokens_used = usage.get("total_tokens", 0)

        logger.info(
            f"Generated {content_type} for {user_tier} via {provider}/{model} "
            f"(cached: {cached}, tokens: {tokens_used})"
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            provider=provider,
            model=model,
            cached=cached,
            tokens_used=tokens_used,
            cost_usd=None  # TODO: Implementar cost tracking
        )

    except Exception as e:
        logger.error(
            f"LLM generation failed for {user_tier}/{content_type}: {e}"
        )
        raise


async def generate_image(
    user_tier: UserTier,
    prompt: str,
    style: str = "realistic",
    **kwargs
) -> LLMResponse:
    """
    Genera imagen usando el modelo apropiado según tier.

    Args:
        user_tier: Tier del cliente
        prompt: Descripción de la imagen
        style: Estilo de imagen (realistic, cartoon, minimal)
        **kwargs: Argumentos adicionales

    Returns:
        LLMResponse con URL de imagen
    """
    tier_config = LLM_TIERS[user_tier]
    image_config = tier_config.imagen

    # TODO: Implementar generación de imagen con fal.ai/DALL-E
    # Por ahora solo estructura

    logger.info(
        f"Image generation requested for {user_tier} with style {style}"
    )

    raise NotImplementedError(
        "Image generation será implementado en el siguiente archivo"
    )
