"""
Auth API Routes
Role-based authentication endpoints for OMEGA platform
"""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, EmailStr
from typing import Optional
import base64
import json
from app.infrastructure.supabase_service import get_supabase_service
import logging

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════

class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr
    password: str  # Ignored for now (Phase 3 MVP)


class LoginResponse(BaseModel):
    """Login response"""
    email: str
    role: str
    reseller_id: Optional[str] = None
    client_id: Optional[str] = None
    redirect_to: str


class APIResponse(BaseModel):
    """Standard API response"""
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None
    token: Optional[str] = None
    error: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_redirect_by_role(role: str) -> str:
    """Get redirect URL based on user role"""
    redirects = {
        "owner": "/admin/resellers",
        "reseller": "/reseller/dashboard",
        "agent": "/dashboard",
        "client": "/client/dashboard"
    }
    return redirects.get(role, "/")


def create_simple_token(user_data: dict) -> str:
    """
    Create simple token (base64 encoded user data)

    NOTE: This is MVP auth - Phase 4 will use proper JWT
    """
    token_data = json.dumps(user_data)
    return base64.b64encode(token_data.encode()).decode()


def decode_simple_token(token: str) -> Optional[dict]:
    """Decode simple token"""
    try:
        token_data = base64.b64decode(token.encode()).decode()
        return json.loads(token_data)
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════
# AUTH ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.post("/login", response_model=APIResponse)
async def login(request: LoginRequest) -> APIResponse:
    """
    Login with email (password ignored for Phase 3 MVP)

    Returns:
    - 200: Login successful with token and redirect
    - 401: Email not found (error: "unauthorized")
    - 403: Account disabled (error: "account_disabled")

    NOTE: Password validation will be added in Phase 4
    """
    try:
        service = get_supabase_service()

        # Get user by email
        user = await service.get_user_by_email(request.email)

        if not user:
            return APIResponse(
                success=False,
                error="unauthorized",
                message="Invalid credentials"
            )

        # Check if account is active
        if not user.get("is_active", True):
            return APIResponse(
                success=False,
                error="account_disabled",
                message="Account is disabled"
            )

        # Get redirect URL based on role
        redirect_to = get_redirect_by_role(user["role"])

        # Create token (simple base64 for MVP)
        token_data = {
            "email": user["email"],
            "role": user["role"],
            "reseller_id": user.get("reseller_id"),
            "client_id": user.get("client_id")
        }
        token = create_simple_token(token_data)

        # Prepare response data
        login_data = {
            "email": user["email"],
            "role": user["role"],
            "reseller_id": user.get("reseller_id"),
            "client_id": user.get("client_id"),
            "redirect_to": redirect_to
        }

        return APIResponse(
            success=True,
            data=login_data,
            token=token,
            message="Login successful"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me", response_model=APIResponse)
async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> APIResponse:
    """
    Get current user from token

    Header: Authorization: Bearer {token}

    Returns:
    - 200: User data
    - 401: Invalid or missing token
    """
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid authorization header"
            )

        # Extract token
        token = authorization.replace("Bearer ", "")

        # Decode token
        user_data = decode_simple_token(token)
        if not user_data:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        # Get full user data from database
        service = get_supabase_service()
        user = await service.get_user_by_email(user_data["email"])

        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        # Check if still active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=403,
                detail="Account is disabled"
            )

        return APIResponse(
            success=True,
            data={
                "email": user["email"],
                "role": user["role"],
                "reseller_id": user.get("reseller_id"),
                "client_id": user.get("client_id"),
                "is_active": user.get("is_active", True)
            },
            message="User retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout", response_model=APIResponse)
async def logout() -> APIResponse:
    """
    Logout (stateless - frontend deletes token)

    Returns:
    - 200: Logout successful

    NOTE: This is stateless auth - the token is not stored server-side.
    The frontend should delete the token from localStorage/cookies.
    """
    return APIResponse(
        success=True,
        data={},
        message="Logout successful"
    )
