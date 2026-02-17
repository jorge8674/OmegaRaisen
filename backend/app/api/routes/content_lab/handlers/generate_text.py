"""
Handler de generación de texto para Content Lab.
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
import logging

from app.api.routes.content_lab.models import (
    GenerateTextRequest, GenerateTextResponse
)
from app.api.routes.content_lab.builders.prompt_builder import (
    build_user_prompt, build_system_prompt
)
from app.services.llm.router import generate_content
from app.domain.llm.types import ContentType, UserTier
from app.infrastructure.supabase_service import get_db

logger = logging.getLogger(__name__)


async def handle_generate_text(
    request: GenerateTextRequest,
    db: Session = Depends(get_db)
) -> GenerateTextResponse:
    """
    Handler HTTP para generación de texto.

    Workflow:
    1. Validar request
    2. Obtener contexto del cliente desde DB
    3. Construir prompts (user + system)
    4. Llamar al router LLM
    5. Guardar resultado en DB
    6. Retornar response

    Args:
        request: Request con brief, client_id, social_account_id, etc.
        db: Sesión de base de datos

    Returns:
        GenerateTextResponse con contenido generado

    Raises:
        HTTPException: Si falla validación o generación
    """
    try:
        # 1. Obtener contexto del cliente desde DB
        # TODO: Usar repository pattern
        client = db.execute(
            "SELECT name, plan FROM clients WHERE id = :id",
            {"id": request.client_id}
        ).fetchone()

        if not client:
            raise HTTPException(404, "Cliente no encontrado")

        social_account = db.execute(
            "SELECT platform, context FROM social_accounts WHERE id = :id",
            {"id": request.social_account_id}
        ).fetchone()

        if not social_account:
            raise HTTPException(404, "Cuenta social no encontrada")

        # 2. Extraer contexto
        client_name = client.name
        user_tier = client.plan or "pro_197"  # Default Pro
        platform = social_account.platform

        context_data = social_account.context or {}
        audience = context_data.get("audience", "General")
        tone = context_data.get("tone", "professional")
        goal = context_data.get("goal", "engagement")
        brand_voice = context_data.get("brand_voice")
        keywords = context_data.get("keywords", [])

        # 3. Construir prompts
        user_prompt = build_user_prompt(
            content_type=request.content_type,
            brief=request.brief,
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
            content_type=request.content_type,
            user_tier=user_tier,
            prompt=user_prompt,
            system_prompt=system_prompt
        )

        # 5. Guardar en DB
        # TODO: Usar repository pattern
        db.execute(
            """
            INSERT INTO content_lab_generated
            (client_id, social_account_id, content_type, content,
             provider, model, tokens_used, created_at)
            VALUES (:client_id, :account_id, :type, :content,
                    :provider, :model, :tokens, NOW())
            """,
            {
                "client_id": request.client_id,
                "account_id": request.social_account_id,
                "type": request.content_type,
                "content": llm_response.content,
                "provider": llm_response.provider,
                "model": llm_response.model,
                "tokens": llm_response.tokens_used
            }
        )
        db.commit()

        logger.info(
            f"Generated {request.content_type} for client {request.client_id} "
            f"via {llm_response.provider}/{llm_response.model}"
        )

        # 6. Retornar response
        return GenerateTextResponse(
            content=llm_response.content,
            metadata={
                "provider": llm_response.provider,
                "model": llm_response.model,
                "cached": llm_response.cached,
                "tokens_used": llm_response.tokens_used
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise HTTPException(500, f"Error generando contenido: {str(e)}")
