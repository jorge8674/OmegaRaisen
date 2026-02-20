"""
Handler: NOVA Chat with Claude Sonnet 4.5 (Anthropic)
Conversational AI assistant for OMEGA Company with agent memory
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any, List
from fastapi import HTTPException
from pydantic import BaseModel
import logging
import os
import asyncio

from app.services.agent_memory_service import AgentMemoryService

logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
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
    Process chat messages with Claude Sonnet 4.5 + agent memory

    Args:
        request: ChatRequest with messages and optional context_docs

    Returns:
        Dict with assistant response

    Raises:
        HTTPException 500: Anthropic API error
        HTTPException 503: Anthropic service unavailable
    """
    try:
        memory_service = AgentMemoryService()

        # Build context from documents if provided
        context_text = ""
        if request.context_docs:
            context_text = "\n\nDOCUMENTOS DE CONTEXTO:\n"
            for doc in request.context_docs:
                context_text += f"\n--- {doc.get('name', 'Documento')} ---\n"
                context_text += doc.get('content', '')[:2000]  # Limit per doc

        # Build messages array for Claude
        messages = []
        for msg in request.messages[-20:]:  # Last 20 messages
            if msg.role in ["user", "assistant"]:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        # Ensure messages start with user
        if not messages or messages[0]["role"] != "user":
            messages.insert(0, {
                "role": "user",
                "content": "Hola NOVA, estoy listo para trabajar."
            })

        # Detect mentioned agents in recent messages
        recent_text = " ".join([m["content"] for m in messages[-3:]])
        mentioned_agents = memory_service.extract_mentioned_agents(recent_text)

        # Enrich system prompt with agent memory if agents mentioned
        agent_memory_context = ""
        if mentioned_agents:
            # Get context for the most mentioned agent
            agent_context = await memory_service.get_agent_context(mentioned_agents[0])
            if agent_context:
                agent_memory_context = f"\n\nMEMORIA RECIENTE DE {mentioned_agents[0]}:\n{agent_context}"

        # Build enhanced system prompt
        enhanced_system = NOVA_SYSTEM_PROMPT + context_text + agent_memory_context

        # Check for Anthropic API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("ANTHROPIC_API_KEY not configured")
            return {
                "role": "assistant",
                "content": "⚠️ Lo siento, el servicio de IA no está configurado correctamente. Por favor verifica que ANTHROPIC_API_KEY esté configurado en las variables de entorno.\n\nMientras tanto, puedo ayudarte accediendo directamente a los endpoints de la API."
            }

        # Call Anthropic API
        try:
            import httpx

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": "claude-sonnet-4-5-20250929",
                        "max_tokens": 2000,
                        "temperature": 0.7,
                        "system": enhanced_system,
                        "messages": messages
                    }
                )

                if response.status_code != 200:
                    error_detail = response.text
                    logger.error(f"Anthropic API error: {response.status_code} - {error_detail}")

                    if response.status_code == 401:
                        raise HTTPException(status_code=503, detail="Invalid Anthropic API key")
                    elif response.status_code == 429:
                        raise HTTPException(status_code=503, detail="Anthropic rate limit exceeded")
                    else:
                        raise HTTPException(status_code=503, detail=f"Anthropic API error: {response.status_code}")

                data = response.json()
                assistant_message = data["content"][0]["text"]

                logger.info(f"NOVA chat (Claude): generated {len(assistant_message)} chars")

                # Save agent memory asynchronously (non-blocking)
                user_message = messages[-1]["content"] if messages else ""
                all_text = user_message + " " + assistant_message
                mentioned_in_response = memory_service.extract_mentioned_agents(all_text)

                if mentioned_in_response:
                    # Create task to save memory without blocking response
                    asyncio.create_task(
                        memory_service.save_conversation_memory(
                            agent_codes=mentioned_in_response,
                            user_message=user_message,
                            nova_response=assistant_message,
                            recent_context=messages[-5:]
                        )
                    )
                    logger.info(f"Saving memory for agents: {', '.join(mentioned_in_response)}")

                return {
                    "role": "assistant",
                    "content": assistant_message
                }

        except httpx.TimeoutException:
            logger.error("Anthropic API timeout")
            raise HTTPException(status_code=503, detail="AI service timeout - please try again")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in NOVA chat: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat: {str(e)}")
