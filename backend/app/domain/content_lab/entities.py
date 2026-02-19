"""
Content Lab Domain Entities
Filosofía: No velocity, only precision 🐢💎
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ContentLabGenerated:
    """
    Entidad de dominio para contenido generado.

    Representa una pieza de contenido (texto o imagen) generada
    por el sistema para un cliente/cuenta social.
    """

    id: str
    client_id: str
    social_account_id: str
    content_type: str  # 'caption', 'image', 'script', etc.
    content: str  # Texto generado o URL de imagen
    provider: str  # 'openai', 'anthropic', 'fal'
    model: str
    tokens_used: int
    is_saved: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    def toggle_saved(self) -> None:
        """Toggle estado de guardado (favorito)."""
        self.is_saved = not self.is_saved

    def soft_delete(self) -> None:
        """Marca el contenido como eliminado (soft delete)."""
        self.is_active = False

    def can_be_modified(self) -> bool:
        """Verifica si el contenido puede ser modificado."""
        return self.is_active

    def to_dict(self) -> dict:
        """Convierte entidad a diccionario."""
        return {
            "id": self.id,
            "client_id": self.client_id,
            "social_account_id": self.social_account_id,
            "content_type": self.content_type,
            "content": self.content,
            "provider": self.provider,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "is_saved": self.is_saved,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
