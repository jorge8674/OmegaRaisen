"""
Router principal de Content Lab.
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import APIRouter, HTTPException, Query

from .models import (
    GenerateTextRequest, GenerateTextResponse,
    GenerateImageRequest, GenerateImageResponse,
    ContentListResponse, SaveContentResponse, DeleteContentResponse
)
from .handlers.generate_text import handle_generate_text

router = APIRouter(prefix="/content-lab", tags=["content-lab"])


@router.post("/generate/", response_model=GenerateTextResponse)
async def generate_text(
    request: GenerateTextRequest
) -> GenerateTextResponse:
    """
    Genera contenido de texto usando LLM apropiado según tier.

    - **client_id**: ID del cliente
    - **social_account_id**: ID de la cuenta social
    - **content_type**: caption, script, hashtags, story, ad, bio, email
    - **brief**: Instrucciones específicas del usuario

    Returns contenido generado + metadata (provider, model, tokens).
    """
    return await handle_generate_text(request)


@router.post("/generate-image/", response_model=GenerateImageResponse)
async def generate_image(
    account_id: str = Query(..., description="Social account UUID"),
    prompt: str = Query(..., description="Image description"),
    style: str = Query(default="realistic", description="Image style: realistic, cartoon, minimal")
) -> GenerateImageResponse:
    """
    Genera imagen usando DALL-E 3

    Frontend envía query params (no body):
    - **account_id**: Social account UUID
    - **prompt**: Descripción de la imagen
    - **style**: realistic, cartoon, minimal (default: realistic)

    Returns URL de imagen + metadata.
    """
    from .handlers.generate_image import handle_generate_image
    return await handle_generate_image(account_id, prompt, style)


@router.get("/", response_model=ContentListResponse)
async def list_content(
    client_id: int,
    content_type: str = None,
    limit: int = 20,
    offset: int = 0
) -> ContentListResponse:
    """
    Lista contenido generado para un cliente.

    - **client_id**: ID del cliente
    - **content_type**: Filtrar por tipo (opcional)
    - **limit**: Máximo de resultados (default: 20)
    - **offset**: Offset para paginación (default: 0)

    Returns lista de contenido + total.
    """
    # TODO: Implementar handler de listado
    raise HTTPException(501, "List content en desarrollo")


@router.patch("/{content_id}/save/", response_model=SaveContentResponse)
async def save_content(
    content_id: int
) -> SaveContentResponse:
    """
    Toggle estado de guardado de contenido.

    - **content_id**: ID del contenido

    Returns ID + estado de guardado.
    """
    # TODO: Implementar handler de guardado
    raise HTTPException(501, "Save content en desarrollo")


@router.delete("/{content_id}/", response_model=DeleteContentResponse)
async def delete_content(
    content_id: int
) -> DeleteContentResponse:
    """
    Elimina contenido generado.

    - **content_id**: ID del contenido a eliminar

    Returns confirmación de eliminación.
    """
    # TODO: Implementar handler de eliminación
    raise HTTPException(501, "Delete content en desarrollo")
