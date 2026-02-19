"""
Router principal de Content Lab.
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import APIRouter, Query

from .models import (
    ContentListResponse, SaveContentResponse, DeleteContentResponse
)
from .handlers import (
    handle_generate_text,
    handle_generate_image,
    handle_list_content,
    handle_save_content,
    handle_delete_content
)

router = APIRouter(prefix="/content-lab", tags=["content-lab"])


@router.post("/generate/")
async def generate_text(
    account_id: str = Query(..., description="Social account UUID"),
    content_type: str = Query(..., description="Content type: caption, story, etc."),
    brief: str = Query(..., description="User instructions"),
    language: str = Query(default="es", description="Language: es, en, etc.")
):
    """
    Genera contenido de texto usando LLM apropiado según tier.

    Frontend envía query params (no body):
    - **account_id**: Social account UUID
    - **content_type**: caption, script, hashtags, story, ad, bio, email
    - **brief**: Instrucciones específicas del usuario
    - **language**: Idioma (default: es)

    Returns flat object con generated_text, content_type, provider, model, cached, tokens_used.
    """
    return await handle_generate_text(account_id, content_type, brief, language)


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


@router.patch("/{content_id}/save/", response_model=SaveContentResponse)
async def save_content(
    content_id: str
) -> SaveContentResponse:
    """
    Toggle estado de guardado de contenido.

    - **content_id**: ID del contenido (UUID)

    Returns ID + estado de guardado.
    """
    return await handle_save_content(content_id)


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
