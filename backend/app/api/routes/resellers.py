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
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def sanitize_json_field(val: Any) -> Dict[str, Any]:
    """
    Sanitize JSONB fields to ensure they're always dicts, never lists.
    Prevents frontend errors when Supabase returns [] instead of {}.
    """
    if isinstance(val, list):
        return {}
    if val is None:
        return {}
    if isinstance(val, dict):
        return val
    # If it's some other type, convert to empty dict
    return {}


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
    # Basic info
    agency_name: Optional[str] = None
    logo_url: Optional[str] = None

    # Colors
    primary_color: str = Field(default="38 85% 55%", description="HSL or hex color")
    secondary_color: str = Field(default="225 12% 14%", description="HSL or hex color")

    # Hero section
    hero_type: Optional[str] = Field(None, description="'image' or 'video'")
    hero_media_type: Optional[str] = Field(None, description="'image' or 'video' (alias for hero_type)")
    hero_media_url: Optional[str] = None
    hero_title: Optional[str] = None
    hero_subtitle: Optional[str] = None
    hero_cta_text: str = Field(default="Comenzar")
    hero_cta_url: Optional[str] = None

    # Content sections (as objects)
    pain_section: Optional[Dict[str, Any]] = None
    solutions_section: Optional[Dict[str, Any]] = None
    services_section: Optional[Dict[str, Any]] = None
    metrics_section: Optional[Dict[str, Any]] = None
    process_section: Optional[Dict[str, Any]] = None
    testimonials_section: Optional[Dict[str, Any]] = None
    client_logos_section: Optional[Dict[str, Any]] = None

    # Contact
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

    # Footer
    footer_text: Optional[str] = None
    social_links: Optional[Dict[str, Any]] = None

    # Legacy fields (keep for backward compatibility)
    agency_tagline: Optional[str] = None
    badge_text: Optional[str] = None
    pain_items: Optional[List[str]] = None
    solution_items: Optional[List[str]] = None
    services: Optional[List[Dict[str, str]]] = None
    metrics: Optional[List[Dict[str, Any]]] = None
    process_steps: Optional[List[Dict[str, str]]] = None
    testimonials: Optional[List[Dict[str, str]]] = None
    footer_email: Optional[str] = None
    footer_phone: Optional[str] = None
    legal_pages: Optional[List[Dict[str, str]]] = None


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


class CreateLeadRequest(BaseModel):
    """Request to create lead from landing page contact form"""
    name: str = Field(..., description="Contact name", min_length=2, max_length=255)
    email: EmailStr = Field(..., description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone", max_length=50)
    message: Optional[str] = Field(None, description="Contact message", max_length=2000)
    reseller_id: str = Field(..., description="Reseller UUID")


class CreateLeadBySlugRequest(BaseModel):
    """Request to create lead from public landing page (by slug)"""
    name: str = Field(..., description="Contact name", min_length=2, max_length=255)
    email: EmailStr = Field(..., description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone", max_length=50)
    message: Optional[str] = Field(None, description="Contact message", max_length=2000)
    source: str = Field(default="landing_page", description="Lead source")


class UpdateLeadStatusRequest(BaseModel):
    """Request to update lead status"""
    status: str = Field(..., description="new|contacted|converted|lost")
    notes: Optional[str] = Field(None, description="Optional notes")


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

        # Auto-create password with bcrypt
        import bcrypt
        from uuid import uuid4
        temp_password = "TempAccess2026!"
        password_hash = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt())

        try:
            # Insert password hash into user_passwords table
            service.client.table("user_passwords").upsert({
                "email": request.owner_email,
                "password_hash": password_hash.decode('utf-8')
            }, on_conflict="email").execute()
            logger.info(f"Password created for reseller: {request.owner_email}")
        except Exception as pwd_error:
            logger.warning(f"Could not create password (may already exist): {pwd_error}")

        # Create user_role for automatic login
        user_role_data = {
            "user_id": str(uuid4()),
            "email": request.owner_email,
            "role": "reseller",
            "reseller_id": reseller["id"],
            "is_active": True
        }
        await service.create_user_role(user_role_data)
        logger.info(f"User role created for reseller: {request.owner_email}")

        return APIResponse(
            success=True,
            data={
                **reseller,
                "temp_password": temp_password,
                "note": "Temporary password created. User should change it after first login."
            },
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

    Returns complete branding object (or defaults if not configured)
    Includes reseller slug for frontend routing
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
            logger.warning(f"Could not fetch slug for reseller {reseller_id}: {slug_error}")
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
                "social_links": {}
            }
        else:
            # Add slug to branding data
            branding["slug"] = slug

            # Sanitize JSONB fields to ensure they're always dicts, never lists
            branding["pain_section"] = sanitize_json_field(branding.get("pain_section"))
            branding["solutions_section"] = sanitize_json_field(branding.get("solutions_section"))
            branding["services_section"] = sanitize_json_field(branding.get("services_section"))
            branding["metrics_section"] = sanitize_json_field(branding.get("metrics_section"))
            branding["process_section"] = sanitize_json_field(branding.get("process_section"))
            branding["testimonials_section"] = sanitize_json_field(branding.get("testimonials_section"))
            branding["client_logos_section"] = sanitize_json_field(branding.get("client_logos_section"))
            branding["social_links"] = sanitize_json_field(branding.get("social_links"))

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
    Get reseller + branding by slug (PUBLIC endpoint)

    Used by white-label landing pages to load all branding data

    Returns:
    - 200: Reseller + branding data
    - 404: Agency not found (error: "not_found")
    - 403: Agency suspended (error: "agency_suspended")
    """
    try:
        service = get_supabase_service()

        # Get reseller by slug
        reseller = await service.get_reseller_by_slug(slug)
        if not reseller:
            return APIResponse(
                success=False,
                data={"error": "not_found"},
                message="Agency not found"
            )

        # Check if suspended
        if reseller.get("status") == "suspended":
            return APIResponse(
                success=False,
                data={"error": "agency_suspended"},
                message="This agency is not available"
            )

        # Get branding (or return defaults)
        branding = await service.get_branding(reseller["id"])
        if not branding:
            # Return default branding
            branding = {
                "reseller_id": reseller["id"],
                "primary_color": "38 85% 55%",
                "secondary_color": "225 12% 14%",
                "hero_cta_text": "Comenzar",
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
                "social_links": {}
            }
        else:
            # Sanitize JSONB fields to ensure they're always dicts, never lists
            branding["pain_section"] = sanitize_json_field(branding.get("pain_section"))
            branding["solutions_section"] = sanitize_json_field(branding.get("solutions_section"))
            branding["services_section"] = sanitize_json_field(branding.get("services_section"))
            branding["metrics_section"] = sanitize_json_field(branding.get("metrics_section"))
            branding["process_section"] = sanitize_json_field(branding.get("process_section"))
            branding["testimonials_section"] = sanitize_json_field(branding.get("testimonials_section"))
            branding["client_logos_section"] = sanitize_json_field(branding.get("client_logos_section"))
            branding["social_links"] = sanitize_json_field(branding.get("social_links"))

        # Combine reseller + branding
        public_data = {
            "reseller": {
                "id": reseller["id"],
                "slug": reseller["slug"],
                "agency_name": reseller["agency_name"],
                "status": reseller["status"]
            },
            "branding": branding
        }

        return APIResponse(
            success=True,
            data=public_data,
            message="Reseller found"
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


@router.post("/{reseller_id}/leads", response_model=APIResponse)
async def create_lead(
    reseller_id: str,
    request: CreateLeadRequest
) -> APIResponse:
    """
    Create lead from landing page contact form (PUBLIC endpoint)

    Used by white-label landing pages to submit contact forms

    Accepts:
    - name: Contact name (required)
    - email: Contact email (required)
    - phone: Contact phone (optional)
    - message: Contact message (optional)
    - reseller_id: Reseller UUID (required)

    Returns:
    - 200: Lead created successfully
    - 422: Validation error
    """
    try:
        service = get_supabase_service()

        # Verify reseller exists
        reseller = await service.get_reseller(reseller_id)
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller not found")

        # Create lead
        lead_data = {
            "reseller_id": reseller_id,
            "name": request.name,
            "email": request.email,
            "phone": request.phone,
            "message": request.message
        }

        await service.create_lead(lead_data)

        return APIResponse(
            success=True,
            data={},
            message="Lead received successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/slug/{slug}/lead", response_model=APIResponse)
async def create_lead_by_slug(
    slug: str,
    request: CreateLeadBySlugRequest
) -> APIResponse:
    """
    Create lead from public landing page using slug (PUBLIC endpoint)

    Used by white-label landing pages to submit contact forms
    The reseller_id is automatically inferred from the slug

    Accepts:
    - name: Contact name (required)
    - email: Contact email (required)
    - phone: Contact phone (optional)
    - message: Contact message (optional)
    - source: Lead source (default: "landing_page")

    Returns:
    - 200: Lead created successfully
    - 404: Agency not found
    - 422: Validation error
    """
    try:
        service = get_supabase_service()

        # Get reseller by slug
        reseller = await service.get_reseller_by_slug(slug)
        if not reseller:
            return APIResponse(
                success=False,
                data={"error": "not_found"},
                message="Agency not found"
            )

        # Create lead
        lead_data = {
            "reseller_id": reseller["id"],
            "name": request.name,
            "email": request.email,
            "phone": request.phone,
            "message": request.message,
            "source": request.source
        }

        await service.create_lead(lead_data)

        return APIResponse(
            success=True,
            data={},
            message="Lead received successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating lead by slug: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{reseller_id}/leads", response_model=APIResponse)
async def get_reseller_leads(
    reseller_id: str,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20
) -> APIResponse:
    """
    Get all leads for a reseller with optional filters and pagination

    Query params:
    - status: Optional filter (new|contacted|converted|lost)
    - page: Page number (default: 1)
    - limit: Results per page (default: 20, max: 100)

    Returns paginated leads with counts by status
    """
    try:
        service = get_supabase_service()

        # Verify reseller exists
        reseller = await service.get_reseller(reseller_id)
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller not found")

        # Validate limit
        if limit > 100:
            limit = 100

        # Get leads with pagination
        leads, total = await service.get_reseller_leads(reseller_id, status, page, limit)

        # Get counts by status
        counts = await service.get_lead_counts(reseller_id)

        return APIResponse(
            success=True,
            data={
                "leads": leads,
                "total": total,
                "page": page,
                "limit": limit,
                "counts": counts
            },
            message=f"Found {total} leads"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reseller leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leads/{lead_id}", response_model=APIResponse)
async def get_lead(lead_id: str) -> APIResponse:
    """
    Get a specific lead by ID

    Returns complete lead object
    """
    try:
        service = get_supabase_service()

        lead = await service.get_lead_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        return APIResponse(
            success=True,
            data=lead,
            message="Lead retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/leads/{lead_id}/status", response_model=APIResponse)
async def update_lead_status(
    lead_id: str,
    request: UpdateLeadStatusRequest
) -> APIResponse:
    """
    Update lead status and optional notes

    Accepts:
    - status: new|contacted|converted|lost (required)
    - notes: Optional notes to add

    Logic:
    - If status = "contacted" → sets contacted_at = NOW()
    - If status = "converted" → sets contacted_at if null

    Returns updated lead object
    """
    try:
        service = get_supabase_service()

        # Verify lead exists
        lead = await service.get_lead_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        # Validate status
        valid_statuses = ["new", "contacted", "converted", "lost"]
        if request.status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )

        # Update lead status
        updated_lead = await service.update_lead_status(
            lead_id,
            request.status,
            request.notes
        )

        return APIResponse(
            success=True,
            data=updated_lead,
            message="Lead status updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lead status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
