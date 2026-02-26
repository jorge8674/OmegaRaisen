"""
Router principal de Content Lab.
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import APIRouter, Query

from .models import (
    ContentListResponse, DeleteContentResponse
)
from .handlers import (
    handle_generate_text,
    handle_generate_image,
    handle_generate_video_runway,
    handle_generate_video_fal,
    handle_list_content,
    handle_delete_content,
    handle_analyze_insight,
    handle_analyze_forecast,
    handle_predict_virality
)

router = APIRouter(prefix="/content-lab", tags=["content-lab"])


@router.post("/generate/")
async def generate_text(
    account_id: str = Query(..., description="Social account UUID"),
    content_type: str = Query(..., description="Content type: caption, story, etc."),
    brief: str = Query(..., description="User instructions"),
    language: str = Query(default="es", description="Language: es, en, etc."),
    director: str = Query(default="REX", description="AI Director: NOVA, ATLAS, LUNA, REX, VERA, KIRA, ORACLE")
):
    """
    Genera contenido de texto usando LLM apropiado según tier.

    Frontend envía query params (no body):
    - **account_id**: Social account UUID
    - **content_type**: caption, script, hashtags, story, ad, bio, email
    - **brief**: Instrucciones específicas del usuario
    - **language**: Idioma (default: es)
    - **director**: AI Director (default: REX = gpt-4o-mini)

    Returns flat object con generated_text, content_type, provider, model, cached, tokens_used.
    """
    return await handle_generate_text(account_id, content_type, brief, language, director)


@router.post("/generate-image/")
async def generate_image(
    account_id: str = Query(..., description="Social account UUID"),
    prompt: str = Query(..., description="Image description"),
    style: str = Query(default="realistic", description="Image style: realistic, cartoon, minimal")
):
    """
    Genera imagen usando DALL-E 3

    Frontend envía query params (no body):
    - **account_id**: Social account UUID
    - **prompt**: Descripción de la imagen
    - **style**: realistic, cartoon, minimal (default: realistic)

    Returns flat object con generated_text (URL), content_type, provider, model, cached, tokens_used.
    """
    return await handle_generate_image(account_id, prompt, style)


@router.post("/generate-video-runway/")
async def generate_video_runway(
    account_id: str = Query(..., description="Social account UUID"),
    prompt: str = Query(..., description="Video description"),
    duration: int = Query(default=5, description="Video duration in seconds (5 or 10)"),
    style: str = Query(default="realistic", description="Video style: realistic, cinematic, animated")
):
    """
    Genera video usando Runway Gen-3 Alpha Turbo

    Frontend envía query params (no body):
    - **account_id**: Social account UUID
    - **prompt**: Descripción del video
    - **duration**: Duración en segundos (5 o 10, default: 5)
    - **style**: realistic, cinematic, animated (default: realistic)

    Returns flat object con generated_text (video URL), content_type, provider, model, duration, ratio.
    """
    return await handle_generate_video_runway(account_id, prompt, duration, style)


@router.post("/generate-video-fal/")
async def generate_video_fal(
    account_id: str = Query(..., description="Social account UUID"),
    prompt: str = Query(..., description="Video description"),
    duration: int = Query(default=5, description="Video duration in seconds"),
    model: str = Query(default="kling", description="Fal model: kling, hunyuan, wan"),
    style: str = Query(default="realistic", description="Video style: realistic, cinematic, animated")
):
    """
    Genera video usando Fal.ai (Kling, Hunyuan, Wan)

    Frontend envía query params (no body):
    - **account_id**: Social account UUID
    - **prompt**: Descripción del video
    - **duration**: Duración en segundos (default: 5)
    - **model**: kling, hunyuan, wan (default: kling)
    - **style**: realistic, cinematic, animated (default: realistic)

    Returns flat object con generated_text (video URL), content_type, provider, model, aspect_ratio.
    """
    return await handle_generate_video_fal(account_id, prompt, duration, model, style)


@router.get("/", response_model=ContentListResponse)
async def list_content(
    client_id: str,
    content_type: str = None,
    limit: int = 20,
    offset: int = 0
) -> ContentListResponse:
    """
    Lista contenido generado para un cliente.

    - **client_id**: ID del cliente (UUID)
    - **content_type**: Filtrar por tipo (opcional)
    - **limit**: Máximo de resultados (default: 20)
    - **offset**: Offset para paginación (default: 0)

    Returns lista de contenido + total.
    """
    return await handle_list_content(client_id, content_type, limit, offset)


@router.delete("/{content_id}/", response_model=DeleteContentResponse)
async def delete_content(
    content_id: str
) -> DeleteContentResponse:
    """
    Elimina contenido generado.

    - **content_id**: ID del contenido a eliminar (UUID)

    Returns confirmación de eliminación.
    """
    return await handle_delete_content(content_id)


@router.post("/analyze-insight/")
async def analyze_insight(
    content: str = Query(..., description="Generated content text"),
    content_type: str = Query(..., description="Content type: caption, story, etc."),
    platform: str = Query(default="instagram", description="Platform: instagram, facebook, etc.")
):
    """
    Analiza contenido generado y proporciona insights.

    Frontend envía query params:
    - **content**: Texto del contenido generado
    - **content_type**: Tipo de contenido
    - **platform**: Plataforma (default: instagram)

    Returns insights, recommendations, tone analysis, content metrics.
    """
    return await handle_analyze_insight(content, content_type, platform)


@router.post("/analyze-forecast/")
async def analyze_forecast(
    content: str = Query(..., description="Generated content text"),
    content_type: str = Query(..., description="Content type"),
    platform: str = Query(default="instagram", description="Platform"),
    avg_followers: int = Query(default=5000, description="Average followers count")
):
    """
    Predice métricas de engagement para contenido generado.

    Frontend envía query params:
    - **content**: Texto del contenido generado
    - **content_type**: Tipo de contenido
    - **platform**: Plataforma (default: instagram)
    - **avg_followers**: Promedio de followers (default: 5000)

    Returns predicted likes, comments, shares, reach, engagement_rate, confidence level.
    """
    return await handle_analyze_forecast(content, content_type, platform, avg_followers)


@router.post("/analyze-virality/")
async def analyze_virality(
    content: str = Query(..., description="Generated content text"),
    content_type: str = Query(..., description="Content type"),
    platform: str = Query(default="instagram", description="Platform")
):
    """
    Predice score de viralidad para contenido generado.

    Frontend envía query params:
    - **content**: Texto del contenido generado
    - **content_type**: Tipo de contenido
    - **platform**: Plataforma (default: instagram)

    Returns virality_score (0-1), virality_level, key factors, recommendations.
    """
    return await handle_predict_virality(content, content_type, platform)


@router.get("/providers/")
async def list_providers():
    """
    Lista todos los AI providers disponibles (7 directores OMEGA).

    Returns dict con metadata de cada director:
    - provider: anthropic, openai, deepseek, gemini, groq
    - model: Modelo específico
    - description: Descripción del director
    - strengths: Fortalezas
    - best_for: Casos de uso óptimos
    """
    from app.services.ai_providers import AIProviders
    providers = AIProviders()
    return {
        "directors": providers.list_directors(),
        "default": providers.get_default_director()
    }
