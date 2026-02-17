"""
Content Lab Domain Models
Pydantic schemas for AI content generation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


ContentType = Literal[
    "post", "caption", "story", "ad",
    "reel_script", "bio", "hashtags", "email"
]


class ContentGenerateRequest(BaseModel):
    """Request payload for generating content"""
    account_id: str = Field(..., description="Social account UUID")
    content_type: ContentType = Field(..., description="Type of content to generate")
    prompt: str = Field(..., min_length=5, max_length=1000, description="Content theme/prompt")
    extra_instructions: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Additional instructions"
    )


class GeneratedContentProfile(BaseModel):
    """Complete generated content profile from database"""
    id: str
    client_id: str
    account_id: Optional[str] = None
    context_id: Optional[str] = None
    content_type: str
    platform: Optional[str] = None
    prompt: str
    generated_text: str
    tokens_used: int = 0
    model_used: str
    is_saved: bool = False
    created_at: Optional[datetime] = None


class ContentGenerateResponse(BaseModel):
    """Standard API response for content generation"""
    success: bool
    data: Optional[GeneratedContentProfile] = None
    message: Optional[str] = None
    error: Optional[str] = None


class ContentListResponse(BaseModel):
    """API response for listing generated content"""
    success: bool
    data: List[GeneratedContentProfile] = []
    total: int = 0
    message: Optional[str] = None
