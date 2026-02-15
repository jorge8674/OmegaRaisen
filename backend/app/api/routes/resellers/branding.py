"""
Reseller Branding Routes
Endpoints for managing white-label branding and media uploads
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Dict, Any
from app.infrastructure.supabase_service import get_supabase_service
from app.models.shared_models import APIResponse
from app.models.reseller_models import (
    BrandingRequest,
    sanitize_json_field,
)
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{reseller_id}/branding", response_model=APIResponse)
async def update_branding(
    reseller_id: str,
    request: BrandingRequest
) -> APIResponse:
    """
    Create or update reseller branding

    Args:
        reseller_id: Reseller UUID
        request: Branding data (colors, copy, sections, etc.)

    Returns:
        APIResponse with updated branding object

    Raises:
        HTTPException 404: Reseller not found
        HTTPException 500: Server error

    Updates all branding fields including:
        - Colors (primary, secondary)
        - Hero section (media, title, subtitle, CTA)
        - Content sections (pain, solutions, services, metrics, etc.)
        - Contact info and social links
        - Pricing plans
    """
    try:
        service = get_supabase_service()

        # Verify reseller exists
        reseller = await service.get_reseller(reseller_id)
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller not found")

        # Update branding
        branding_data = request.model_dump(exclude_none=True)
        branding = await service.update_branding(reseller_id, branding_data)

        return APIResponse(
            success=True,
            data=branding,
            message="Branding updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating branding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{reseller_id}/branding", response_model=APIResponse)
async def get_branding(reseller_id: str) -> APIResponse:
    """
    Get reseller branding configuration

    Args:
        reseller_id: Reseller UUID

    Returns:
        APIResponse with complete branding object (or defaults if not configured)

    Raises:
        HTTPException 500: Server error

    Returns complete branding with:
        - Reseller slug for frontend routing
        - All branding fields with defaults if not set
        - Sanitized JSONB fields (ensures dicts, never lists)
        - Pricing plans as array
    """
    try:
        service = get_supabase_service()

        # Get reseller to extract slug
        try:
            reseller_response = service.client.table("resellers")\
                .select("slug")\
                .eq("id", reseller_id)\
                .execute()

            slug = reseller_response.data[0].get("slug") if reseller_response.data else None
        except Exception as slug_error:
            logger.warning(
                f"Could not fetch slug for reseller {reseller_id}: {slug_error}"
            )
            slug = None

        branding = await service.get_branding(reseller_id)

        # If no branding exists, return defaults instead of 404
        if not branding:
            branding = {
                "reseller_id": reseller_id,
                "slug": slug,
                "primary_color": "38 85% 55%",
                "secondary_color": "225 12% 14%",
                "hero_cta_text": "Comenzar",
                "agency_name": None,
                "logo_url": None,
                "hero_type": None,
                "hero_media_url": None,
                "hero_title": None,
                "hero_subtitle": None,
                "hero_cta_url": None,
                "pain_section": {},
                "solutions_section": {},
                "services_section": {},
                "metrics_section": {},
                "process_section": {},
                "testimonials_section": {},
                "client_logos_section": {},
                "contact_email": None,
                "contact_phone": None,
                "footer_text": None,
                "social_links": {},
                "pricing_plans": []
            }
        else:
            # Add slug to branding data
            branding["slug"] = slug

            # Sanitize JSONB fields to ensure they're always dicts, never lists
            branding["pain_section"] = sanitize_json_field(
                branding.get("pain_section")
            )
            branding["solutions_section"] = sanitize_json_field(
                branding.get("solutions_section")
            )
            branding["services_section"] = sanitize_json_field(
                branding.get("services_section")
            )
            branding["metrics_section"] = sanitize_json_field(
                branding.get("metrics_section")
            )
            branding["process_section"] = sanitize_json_field(
                branding.get("process_section")
            )
            branding["testimonials_section"] = sanitize_json_field(
                branding.get("testimonials_section")
            )
            branding["client_logos_section"] = sanitize_json_field(
                branding.get("client_logos_section")
            )
            branding["social_links"] = sanitize_json_field(
                branding.get("social_links")
            )

            # Ensure pricing_plans is always an array
            branding["pricing_plans"] = branding.get("pricing_plans") or []

        return APIResponse(
            success=True,
            data=branding,
            message="Branding retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting branding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{reseller_id}/upload-hero-media", response_model=APIResponse)
async def upload_hero_media(
    reseller_id: str,
    file: UploadFile = File(...)
) -> APIResponse:
    """
    Upload hero media (video or image, max 15MB)

    Args:
        reseller_id: Reseller UUID
        file: Media file (video/mp4, video/webm, image/jpeg, image/png, image/webp)

    Returns:
        APIResponse with public URL and media type

    Raises:
        HTTPException 404: Reseller not found
        HTTPException 400: Invalid file type or size
        HTTPException 500: Server error

    Uploads to Supabase Storage bucket 'reseller-media' at:
        {slug}/hero.{extension}

    Updates branding with hero_media_url and hero_media_type
    """
    try:
        service = get_supabase_service()

        # Verify reseller exists
        reseller = await service.get_reseller(reseller_id)
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller not found")

        # Validate file type
        allowed_types = [
            "video/mp4", "video/webm",
            "image/jpeg", "image/png", "image/webp"
        ]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
            )

        # Validate file size (15MB max)
        file_data = await file.read()
        file_size_mb = len(file_data) / (1024 * 1024)
        if file_size_mb > 15:
            raise HTTPException(
                status_code=400,
                detail=f"File too large ({file_size_mb:.2f}MB). Max 15MB allowed."
            )

        # Determine media type
        media_type = "video" if file.content_type.startswith("video/") else "image"

        # Generate file path
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "mp4"
        file_path = f"{reseller['slug']}/hero.{file_extension}"

        # Upload to Supabase Storage
        public_url = await service.upload_media(
            bucket="reseller-media",
            file_path=file_path,
            file_data=file_data,
            content_type=file.content_type
        )

        # Update branding with new media URL
        await service.update_branding(reseller_id, {
            "hero_media_url": public_url,
            "hero_media_type": media_type
        })

        return APIResponse(
            success=True,
            data={
                "url": public_url,
                "media_type": media_type
            },
            message="Hero media uploaded successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading hero media: {e}")
        raise HTTPException(status_code=500, detail=str(e))
