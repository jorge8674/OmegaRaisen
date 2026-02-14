"""
Resellers API Routes
Endpoints for multi-tenant reseller management
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from app.infrastructure.supabase_service import get_supabase_service
import logging

router = APIRouter(prefix="/resellers", tags=["resellers"])
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════

class CreateResellerRequest(BaseModel):
    """Request to create new reseller"""
    slug: str = Field(..., description="URL slug (e.g., 'agenciajuan')", min_length=3, max_length=50)
    agency_name: str = Field(..., description="Agency name", min_length=2, max_length=255)
    owner_email: EmailStr = Field(..., description="Owner email address")
    owner_name: str = Field(..., description="Owner full name", min_length=2, max_length=255)


class ResellerResponse(BaseModel):
    """Reseller object"""
    id: str
    slug: str
    agency_name: str
    owner_email: str
    owner_name: str
    stripe_account_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    white_label_active: bool
    status: str
    omega_commission_rate: float
    monthly_revenue_reported: float
    payment_due_date: Optional[date] = None
    days_overdue: int
    suspend_switch: bool
    clients_migrated: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class UpdateResellerStatusRequest(BaseModel):
    """Request to update reseller status"""
    status: Optional[str] = Field(None, description="Status: active/warning/suspended/terminated")
    suspend_switch: Optional[bool] = Field(None, description="Manual suspension switch")


class BrandingRequest(BaseModel):
    """Request to create/update branding"""
    logo_url: Optional[str] = None
    hero_media_url: Optional[str] = None
    hero_media_type: Optional[str] = Field(None, description="'video' or 'image'")
    primary_color: str = Field(default="38 85% 55%", description="HSL color")
    secondary_color: str = Field(default="225 12% 14%", description="HSL color")
    agency_tagline: Optional[str] = None
    badge_text: str = Field(default="Boutique Creative Agency")
    hero_cta_text: str = Field(default="Comenzar")
    pain_items: List[str] = Field(default_factory=list)
    solution_items: List[str] = Field(default_factory=list)
    services: List[Dict[str, str]] = Field(default_factory=list)
    metrics: List[Dict[str, Any]] = Field(default_factory=list)
    process_steps: List[Dict[str, str]] = Field(default_factory=list)
    testimonials: List[Dict[str, str]] = Field(default_factory=list)
    footer_email: Optional[str] = None
    footer_phone: Optional[str] = None
    social_links: List[Dict[str, str]] = Field(default_factory=list)
    legal_pages: List[Dict[str, str]] = Field(default_factory=list)


class BrandingResponse(BaseModel):
    """Branding object"""
    id: str
    reseller_id: str
    logo_url: Optional[str]
    hero_media_url: Optional[str]
    hero_media_type: Optional[str]
    primary_color: str
    secondary_color: str
    agency_tagline: Optional[str]
    badge_text: str
    hero_cta_text: str
    pain_items: List[str]
    solution_items: List[str]
    services: List[Dict[str, str]]
    metrics: List[Dict[str, Any]]
    process_steps: List[Dict[str, str]]
    testimonials: List[Dict[str, str]]
    footer_email: Optional[str]
    footer_phone: Optional[str]
    social_links: List[Dict[str, str]]
    legal_pages: List[Dict[str, str]]
    created_at: datetime
    updated_at: Optional[datetime]


class AddClientRequest(BaseModel):
    """Request to add client to reseller"""
    client_id: str = Field(..., description="Client UUID to assign")


class ClientSummary(BaseModel):
    """Client summary for dashboard"""
    id: str
    name: str
    status: str
    created_at: datetime
    # Add more fields as needed from clients table


class ResellerDashboardResponse(BaseModel):
    """Reseller dashboard data"""
    reseller: ResellerResponse
    clients: List[Dict[str, Any]]
    agents: List[Dict[str, Any]]
    total_revenue: float
    omega_commission: float
    active_clients_count: int
    suspended_clients_count: int


class MediaUploadResponse(BaseModel):
    """Media upload response"""
    url: str
    media_type: str


class APIResponse(BaseModel):
    """Generic API response"""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.post("/create", response_model=APIResponse)
async def create_reseller(request: CreateResellerRequest) -> APIResponse:
    """
    Create new reseller account

    - **slug**: URL-friendly identifier (e.g., 'agenciajuan')
    - **agency_name**: Full agency name
    - **owner_email**: Owner's email address
    - **owner_name**: Owner's full name

    Returns newly created reseller object
    """
    try:
        service = get_supabase_service()

        # Check if slug already exists
        existing = await service.get_reseller_by_slug(request.slug)
        if existing:
            raise HTTPException(status_code=400, detail=f"Slug '{request.slug}' already exists")

        # Create reseller
        reseller_data = request.model_dump()
        reseller = await service.create_reseller(reseller_data)

        # Create default branding
        branding_data = {
            "reseller_id": reseller["id"],
            "primary_color": "38 85% 55%",
            "secondary_color": "225 12% 14%",
            "badge_text": "Boutique Creative Agency",
            "hero_cta_text": "Comenzar"
        }
        await service.create_branding(branding_data)

        return APIResponse(
            success=True,
            data=reseller,
            message=f"Reseller '{request.agency_name}' created successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating reseller: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{reseller_id}/dashboard", response_model=APIResponse)
async def get_reseller_dashboard(reseller_id: str) -> APIResponse:
    """
    Get complete reseller dashboard

    Returns:
    - Reseller info
    - All clients with metrics
    - All agents (human)
    - Revenue metrics
    - Active/suspended counts
    """
    try:
        service = get_supabase_service()

        # Get reseller
        reseller = await service.get_reseller(reseller_id)
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller not found")

        # Get clients
        clients = await service.get_reseller_clients(reseller_id)

        # Get agents
        agents = await service.get_reseller_agents(reseller_id)

        # Calculate metrics
        total_revenue = reseller.get("monthly_revenue_reported", 0)
        omega_commission = total_revenue * reseller.get("omega_commission_rate", 0.30)
        active_clients_count = len([c for c in clients if c.get("status") == "active"])
        suspended_clients_count = len([c for c in clients if c.get("status") == "suspended"])

        dashboard_data = {
            "reseller": reseller,
            "clients": clients,
            "agents": agents,
            "total_revenue": total_revenue,
            "omega_commission": omega_commission,
            "active_clients_count": active_clients_count,
            "suspended_clients_count": suspended_clients_count
        }

        return APIResponse(
            success=True,
            data=dashboard_data,
            message="Dashboard loaded successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=APIResponse)
async def get_all_resellers() -> APIResponse:
    """
    Get all resellers (OMEGA admin only)

    Returns list of all resellers with status counters
    """
    try:
        service = get_supabase_service()

        resellers = await service.get_all_resellers()

        # Calculate status counters
        total = len(resellers)
        active = len([r for r in resellers if r.get("status") == "active"])
        suspended = len([r for r in resellers if r.get("status") == "suspended"])
        with_mora = len([r for r in resellers if r.get("days_overdue", 0) > 0])

        return APIResponse(
            success=True,
            data={
                "resellers": resellers,
                "total": total,
                "active": active,
                "suspended": suspended,
                "with_mora": with_mora
            },
            message=f"Found {total} resellers"
        )
    except Exception as e:
        logger.error(f"Error getting all resellers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{reseller_id}/status", response_model=APIResponse)
async def update_reseller_status(
    reseller_id: str,
    request: UpdateResellerStatusRequest
) -> APIResponse:
    """
    Update reseller status (OMEGA admin only)

    - **status**: active/warning/suspended/terminated
    - **suspend_switch**: Manual suspension switch
    """
    try:
        service = get_supabase_service()

        # Get current reseller
        reseller = await service.get_reseller(reseller_id)
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller not found")

        # Prepare update data
        update_data = {}
        if request.status is not None:
            update_data["status"] = request.status
        if request.suspend_switch is not None:
            update_data["suspend_switch"] = request.suspend_switch

        # Update reseller
        updated_reseller = await service.update_reseller(reseller_id, update_data)

        return APIResponse(
            success=True,
            data=updated_reseller,
            message="Reseller status updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating reseller status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{reseller_id}/branding", response_model=APIResponse)
async def update_branding(
    reseller_id: str,
    request: BrandingRequest
) -> APIResponse:
    """
    Create or update reseller branding

    - **All branding fields**: logo, colors, copy, etc.

    Returns updated branding object
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

    Returns complete branding object
    """
    try:
        service = get_supabase_service()

        branding = await service.get_branding(reseller_id)
        if not branding:
            raise HTTPException(status_code=404, detail="Branding not found")

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


@router.get("/{reseller_id}/clients", response_model=APIResponse)
async def get_reseller_clients(reseller_id: str) -> APIResponse:
    """
    Get all clients for reseller

    Returns list of clients with full data
    """
    try:
        service = get_supabase_service()

        clients = await service.get_reseller_clients(reseller_id)

        return APIResponse(
            success=True,
            data={"clients": clients, "count": len(clients)},
            message=f"Found {len(clients)} clients"
        )
    except Exception as e:
        logger.error(f"Error getting clients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{reseller_id}/clients/add", response_model=APIResponse)
async def add_client_to_reseller(
    reseller_id: str,
    request: AddClientRequest
) -> APIResponse:
    """
    Assign existing client to reseller

    - **client_id**: Client UUID to assign
    """
    try:
        service = get_supabase_service()

        # Verify reseller exists
        reseller = await service.get_reseller(reseller_id)
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller not found")

        # Assign client
        client = await service.assign_client_to_reseller(
            request.client_id,
            reseller_id
        )

        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        return APIResponse(
            success=True,
            data=client,
            message="Client assigned to reseller successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning client: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/slug/{slug}", response_model=APIResponse)
async def get_branding_by_slug(slug: str) -> APIResponse:
    """
    Get branding by slug (PUBLIC endpoint)

    Used by white-label landing pages

    Returns complete branding configuration
    """
    try:
        service = get_supabase_service()

        # Get reseller by slug
        reseller = await service.get_reseller_by_slug(slug)
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller not found")

        # Get branding
        branding = await service.get_branding(reseller["id"])
        if not branding:
            raise HTTPException(status_code=404, detail="Branding not configured")

        # Combine reseller + branding
        public_data = {
            "reseller": {
                "slug": reseller["slug"],
                "agency_name": reseller["agency_name"],
                "white_label_active": reseller["white_label_active"]
            },
            "branding": branding
        }

        return APIResponse(
            success=True,
            data=public_data,
            message="Branding loaded successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting branding by slug: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{reseller_id}/upload-hero-media", response_model=APIResponse)
async def upload_hero_media(
    reseller_id: str,
    file: UploadFile = File(...)
) -> APIResponse:
    """
    Upload hero media (video or image, max 15MB)

    Accepts:
    - video/mp4, video/webm
    - image/jpeg, image/png, image/webp

    Returns public URL and media type
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
