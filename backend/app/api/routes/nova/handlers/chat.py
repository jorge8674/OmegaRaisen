"""
Handler: NOVA Chat with OpenAI
Conversational AI assistant for OMEGA Company
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any, List
from fastapi import HTTPException
from pydantic import BaseModel
import logging
import os

logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context_docs: List[Dict[str, Any]] = []


NOVA_SYSTEM_PROMPT = """Eres NOVA, el CEO Agent de OMEGA Company (Raisen Agency).

Tu rol es asistir al Super Admin (Ibrain) con:
- Visión estratégica de la empresa
- Análisis de métricas y KPIs
- Coordinación entre los 7 directores (ATLAS, LUNA, REX, VERA, KIRA, ORACLE, SOPHIA)
- Decisiones de alto nivel sobre producto, marketing, operaciones y finanzas
- Generación de reportes ejecutivos

Personalidad:
- Profesional pero cercano
- Conciso y directo (No velocity, only precision 🐢💎)
- Basado en datos, no suposiciones
- Proactivo en sugerir mejoras

Capacidades:
- Acceso a métricas en tiempo real vía API
- Conocimiento de los 45 agentes organizacionales
- Contexto completo de la plataforma OmegaRaisen

Responde SIEMPRE en español, con formato markdown cuando sea necesario."""


async def handle_chat(request: ChatRequest) -> Dict[str, Any]:
    """
    Process chat messages with NOVA AI

    Args:
        request: ChatRequest with messages and optional context_docs

    Returns:
        Dict with assistant response

    Raises:
        HTTPException 500: OpenAI API error
        HTTPException 503: OpenAI service unavailable
    """
    try:
        # Build context from documents if provided
        context_text = ""
        if request.context_docs:
            context_text = "\n\nDOCUMENTOS DE CONTEXTO:\n"
            for doc in request.context_docs:
                context_text += f"\n--- {doc.get('name', 'Documento')} ---\n"
                context_text += doc.get('content', '')[:2000]  # Limit per doc

        # Build messages array for OpenAI
        messages = [
            {"role": "system", "content": NOVA_SYSTEM_PROMPT + context_text}
        ]

        # Add conversation history
        for msg in request.messages[-10:]:  # Last 10 messages only
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # Check for OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not configured")
            # Return fallback response
            return {
                "role": "assistant",
                "content": "⚠️ Lo siento, el servicio de IA no está configurado correctamente. Por favor verifica que OPENAI_API_KEY esté configurado en las variables de entorno.\n\nMientras tanto, puedo ayudarte accediendo directamente a los endpoints de la API."
            }

        # Call OpenAI API
        try:
            import httpx

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o",
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }
                )

                if response.status_code != 200:
                    error_detail = response.text
                    logger.error(f"OpenAI API error: {response.status_code} - {error_detail}")

                    if response.status_code == 401:
                        raise HTTPException(
                            status_code=503,
                            detail="Invalid OpenAI API key"
                        )
                    elif response.status_code == 429:
                        raise HTTPException(
                            status_code=503,
                            detail="OpenAI rate limit exceeded"
                        )
                    else:
                        raise HTTPException(
                            status_code=503,
                            detail=f"OpenAI API error: {response.status_code}"
                        )

                data = response.json()
                assistant_message = data["choices"][0]["message"]["content"]

                logger.info(f"NOVA chat: generated {len(assistant_message)} chars")

                return {
                    "role": "assistant",
                    "content": assistant_message
                }

        except httpx.TimeoutException:
            logger.error("OpenAI API timeout")
            raise HTTPException(
                status_code=503,
                detail="AI service timeout - please try again"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in NOVA chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat: {str(e)}"
        )
