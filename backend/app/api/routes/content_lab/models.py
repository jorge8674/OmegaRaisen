"""
Modelos Pydantic para Content Lab API.
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Optional, Any
from pydantic import BaseModel, Field

from app.domain.llm.types import ContentType


class GenerateTextRequest(BaseModel):
    """Request para generación de texto."""
    client_id: str = Field(..., description="ID del cliente (UUID)")
    social_account_id: str = Field(..., description="ID de cuenta social (UUID)")
    content_type: ContentType = Field(..., description="Tipo de contenido")
    brief: str = Field(..., min_length=1, description="Brief del usuario")

    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "bd68ca50-b8ef-4240-a0ce-44df58f53171",
                "social_account_id": "cb1dfe0a-43a2-4e9b-9099-df6035f76700",
                "content_type": "caption",
                "brief": "Post sobre nuestro nuevo producto"
            }
        }


class GenerateTextResponse(BaseModel):
    """Response de generación de texto."""
    content: str = Field(..., description="Contenido generado")
    metadata: dict[str, Any] = Field(
        ...,
        description="Metadata (provider, model, tokens, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "🚀 Descubre nuestro nuevo producto...",
                "metadata": {
                    "provider": "anthropic",
                    "model": "claude-sonnet-4",
                    "cached": True,
                    "tokens_used": 150
                }
            }
        }


class GenerateImageRequest(BaseModel):
    """Request para generación de imágenes."""
    client_id: str = Field(..., description="ID del cliente (UUID)")
    social_account_id: str = Field(..., description="ID de cuenta social (UUID)")
    prompt: str = Field(..., min_length=1, description="Descripción de la imagen")
    style: str = Field(
        default="realistic",
        description="Estilo: realistic, cartoon, minimal"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "bd68ca50-b8ef-4240-a0ce-44df58f53171",
                "social_account_id": "cb1dfe0a-43a2-4e9b-9099-df6035f76700",
                "prompt": "Producto tecnológico moderno sobre fondo blanco",
                "style": "realistic"
            }
        }


class GenerateImageResponse(BaseModel):
    """Response de generación de imagen."""
    image_url: str = Field(..., description="URL de la imagen generada")
    metadata: dict[str, Any] = Field(
        ...,
        description="Metadata (provider, model, style, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "image_url": "https://storage.example.com/image123.png",
                "metadata": {
                    "provider": "fal",
                    "model": "flux-dev",
                    "style": "realistic"
                }
            }
        }


class ContentListResponse(BaseModel):
    """Response de listado de contenido."""
    items: list[dict[str, Any]] = Field(
        ...,
        description="Lista de contenido generado"
    )
    total: int = Field(..., description="Total de items")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "content": "Caption generado...",
                        "content_type": "caption",
                        "created_at": "2026-02-17T20:00:00Z"
                    }
                ],
                "total": 1
            }
        }


class SaveContentResponse(BaseModel):
    """Response de guardar contenido."""
    id: str = Field(..., description="ID del contenido (UUID)")
    saved: bool = Field(..., description="Estado de guardado")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "saved": True
            }
        }


class DeleteContentResponse(BaseModel):
    """Response de eliminar contenido."""
    id: str = Field(..., description="ID del contenido eliminado (UUID)")
    deleted: bool = Field(..., description="Confirmación de eliminación")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "deleted": True
            }
        }
