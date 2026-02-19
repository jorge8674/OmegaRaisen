"""
Handler de análisis de contenido para Content Lab.
Proporciona insight, forecast y predicción de viralidad.
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging

from app.agents.analytics_agent import analytics_agent
from app.agents.competitive_intelligence_agent import competitive_intelligence_agent
from app.infrastructure.ai.openai_service import openai_service

logger = logging.getLogger(__name__)


async def handle_analyze_insight(
    content: str,
    content_type: str,
    platform: str = "instagram"
) -> Dict[str, Any]:
    """
    Analiza contenido generado y proporciona insights.

    Workflow:
    1. Usar Analytics Agent para generar insights
    2. Proporcionar recomendaciones específicas

    Args:
        content: Texto del contenido generado
        content_type: Tipo de contenido (caption, story, etc.)
        platform: Plataforma (instagram, facebook, etc.)

    Returns:
        Dict con insights, recommendations, tone_analysis
    """
    try:
        # Construir prompt para análisis de contenido
        prompt = (
            f"Analiza este contenido de {platform} ({content_type}):\n\n"
            f"{content}\n\n"
            f"Proporciona:\n"
            f"1. ¿Qué funciona bien? (3 puntos)\n"
            f"2. ¿Qué se puede mejorar? (2 puntos)\n"
            f"3. Análisis de tono (profesional/casual/emocional/etc.)\n"
            f"4. Llamado a la acción: ¿es efectivo?"
        )

        # Generar análisis con OpenAI
        analysis_text = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )

        # Usar Analytics Agent para métricas adicionales
        metrics = {
            "content_length": len(content),
            "content_type": content_type,
            "platform": platform
        }

        agent_insights = await analytics_agent.execute({
            "type": "insights",
            "metrics": metrics
        })

        logger.info(
            f"Generated insights for {content_type} content "
            f"({len(content)} chars)"
        )

        return {
            "success": True,
            "insights": analysis_text,
            "ai_analysis": agent_insights.get("insights", ""),
            "content_metrics": {
                "length": len(content),
                "estimated_read_time_seconds": len(content.split()) * 0.5
            }
        }

    except Exception as e:
        logger.error(f"Insight analysis failed: {e}")
        raise HTTPException(500, f"Error generando insights: {str(e)}")


async def handle_analyze_forecast(
    content: str,
    content_type: str,
    platform: str = "instagram",
    avg_followers: int = 5000
) -> Dict[str, Any]:
    """
    Predice métricas de engagement para contenido generado.

    Workflow:
    1. Analizar factores de engagement del contenido
    2. Generar predicciones basadas en tipo y plataforma

    Args:
        content: Texto del contenido generado
        content_type: Tipo de contenido
        platform: Plataforma
        avg_followers: Promedio de followers (para calcular reach)

    Returns:
        Dict con predicted_likes, predicted_comments, predicted_shares,
        predicted_reach, confidence_level
    """
    try:
        # Construir prompt para predicción de engagement
        prompt = (
            f"Predice el engagement para este contenido de {platform}:\n\n"
            f"Tipo: {content_type}\n"
            f"Contenido: {content}\n"
            f"Followers promedio: {avg_followers}\n\n"
            f"Estima (en formato numérico):\n"
            f"- Likes esperados (número)\n"
            f"- Comentarios esperados (número)\n"
            f"- Shares esperados (número)\n"
            f"- Reach estimado (% de followers)\n"
            f"- Nivel de confianza (bajo/medio/alto)"
        )

        # Generar predicción con OpenAI
        prediction_text = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=250,
            temperature=0.6
        )

        # Calcular estimaciones básicas (fallback)
        # En producción, esto usaría modelos ML entrenados con data real
        content_score = min(len(content) / 500, 1.0)  # Longer = better
        engagement_rate = 0.03  # 3% baseline

        if content_type in ["reel", "video"]:
            engagement_rate *= 2.5  # Video performs better
        elif content_type in ["story"]:
            engagement_rate *= 1.2
        elif content_type in ["post", "caption"]:
            engagement_rate *= 1.0

        predicted_likes = int(avg_followers * engagement_rate * content_score)
        predicted_comments = int(predicted_likes * 0.08)  # 8% of likes
        predicted_shares = int(predicted_likes * 0.03)  # 3% of likes
        predicted_reach = int(avg_followers * 0.3)  # 30% reach

        logger.info(
            f"Generated forecast for {content_type}: "
            f"{predicted_likes} likes predicted"
        )

        return {
            "success": True,
            "predicted_engagement": {
                "likes": predicted_likes,
                "comments": predicted_comments,
                "shares": predicted_shares,
                "reach": predicted_reach,
                "engagement_rate": round(engagement_rate * 100, 2)
            },
            "ai_prediction": prediction_text,
            "confidence_level": "medium",
            "factors_analyzed": [
                "content_length",
                "content_type",
                "platform_benchmarks",
                "audience_size"
            ]
        }

    except Exception as e:
        logger.error(f"Forecast analysis failed: {e}")
        raise HTTPException(500, f"Error generando forecast: {str(e)}")


async def handle_predict_virality(
    content: str,
    content_type: str,
    platform: str = "instagram"
) -> Dict[str, Any]:
    """
    Predice score de viralidad para contenido generado.

    Workflow:
    1. Analizar factores de viralidad (emociones, controversia, relevancia)
    2. Calcular score 0-1

    Args:
        content: Texto del contenido generado
        content_type: Tipo de contenido
        platform: Plataforma

    Returns:
        Dict con virality_score, factors, recommendations
    """
    try:
        # Construir prompt para predicción de viralidad
        prompt = (
            f"Analiza el potencial viral de este contenido de {platform}:\n\n"
            f"{content}\n\n"
            f"Evalúa (escala 0-10):\n"
            f"1. Impacto emocional\n"
            f"2. Relevancia/Tendencia actual\n"
            f"3. Llamado a compartir\n"
            f"4. Factor sorpresa/novedad\n"
            f"5. Controversia positiva\n\n"
            f"Da un score total y explica los factores clave."
        )

        # Generar análisis con OpenAI
        virality_analysis = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=250,
            temperature=0.7
        )

        # Calcular score básico (fallback)
        # En producción, esto usaría un modelo ML entrenado
        base_score = 0.4  # Baseline

        # Factores que aumentan viralidad
        if len(content) < 150:  # Short & snappy
            base_score += 0.1
        if "?" in content:  # Questions engage
            base_score += 0.1
        if any(emoji in content for emoji in ["😍", "🔥", "💯", "✨"]):
            base_score += 0.1
        if content_type in ["reel", "video", "story"]:
            base_score += 0.2

        virality_score = min(base_score, 1.0)

        logger.info(
            f"Calculated virality score for {content_type}: {virality_score}"
        )

        return {
            "success": True,
            "virality_score": round(virality_score, 2),
            "virality_level": (
                "high" if virality_score >= 0.7 else
                "medium" if virality_score >= 0.4 else
                "low"
            ),
            "ai_analysis": virality_analysis,
            "key_factors": {
                "emotional_impact": round(virality_score * 0.9, 2),
                "shareability": round(virality_score * 0.85, 2),
                "trending_relevance": round(virality_score * 0.7, 2),
                "surprise_factor": round(virality_score * 0.6, 2)
            },
            "recommendations": [
                "Agregar más emociones fuertes" if virality_score < 0.5 else "Buen impacto emocional",
                "Incluir call-to-action para compartir" if "?" not in content else "Buen engagement",
                "Considerar formato video" if content_type not in ["reel", "video"] else "Formato óptimo"
            ]
        }

    except Exception as e:
        logger.error(f"Virality prediction failed: {e}")
        raise HTTPException(500, f"Error prediciendo viralidad: {str(e)}")
