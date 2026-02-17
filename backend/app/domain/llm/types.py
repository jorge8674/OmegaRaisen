"""
Domain types para sistema multi-LLM.
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Literal, Optional, List
from pydantic import BaseModel, Field

# Content types disponibles
ContentType = Literal[
    "caption", "script", "hashtags", "carrusel",
    "analytics", "story", "ad", "bio", "email"
]

# User tiers basados en planes reales
UserTier = Literal["basico_97", "pro_197", "enterprise_497"]

# Acciones de validación de uso
UsageAction = Literal["allow", "warn", "upsell", "block"]

# Providers de LLM
LLMProvider = Literal[
    "anthropic", "openai", "deepseek",
    "groq", "gemini", "fal"
]

class LLMConfig(BaseModel):
    """Configuración de un modelo LLM."""
    primary: str = Field(..., description="Modelo primario (ej: anthropic/claude-sonnet-4)")
    fallback: List[str] = Field(default_factory=list, description="Modelos de respaldo")
    cache: bool = Field(default=False, description="Activar context caching")

class LLMResponse(BaseModel):
    """Respuesta de generación LLM."""
    content: str
    provider: str
    model: str
    cached: bool
    tokens_used: Optional[int] = None
    cost_usd: Optional[float] = None

class TierConfig(BaseModel):
    """Configuración completa de un tier."""
    caption: LLMConfig
    script: LLMConfig
    hashtags: LLMConfig
    carrusel: Optional[LLMConfig] = None
    analytics: Optional[LLMConfig] = None
    story: Optional[LLMConfig] = None
    ad: Optional[LLMConfig] = None
    bio: Optional[LLMConfig] = None
    email: Optional[LLMConfig] = None
    imagen: LLMConfig
