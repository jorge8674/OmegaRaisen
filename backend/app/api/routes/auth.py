"""
Auth API Routes
Role-based authentication with bcrypt + PyJWT
"""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.infrastructure.supabase_service import get_supabase_service
from app.config import get_settings
import bcrypt
import jwt
from datetime import datetime, timedelta
import logging

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)
settings = get_settings()

# JWT Secret from config (fallback for development)
JWT_SECRET = getattr(settings, 'jwt_secret_key', 'omega-raisen-jwt-secret-2026-CHANGE-IN-PRODUCTION')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 7


# ═══════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════

class LoginRequest(BaseModel):
    """Login request with password validation"""
    email: EmailStr
    password: str


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


# ═══════════════════════════════════════════════════════════════
# AUTH ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.post("/login", response_model=APIResponse)
async def login(request: LoginRequest) -> APIResponse:
    """
    Login with email and password (bcrypt + JWT)

    Returns:
    - 200: Login successful with JWT token and redirect
    - 401: Invalid credentials
    - 403: Account disabled

    Password is validated against bcrypt hash in user_passwords table
    """
    try:
        service = get_supabase_service()

        # 1. Get password hash from database
        try:
            pwd_response = service.client.table("user_passwords")\
                .select("password_hash")\
                .eq("email", request.email)\
                .execute()

            if not pwd_response.data or len(pwd_response.data) == 0:
                logger.warning(f"Login attempt for non-existent email: {request.email}")
                return APIResponse(
                    success=False,
                    error="unauthorized",
                    message="Invalid credentials"
                )

            stored_hash = pwd_response.data[0]["password_hash"]
        except Exception as db_error:
            logger.error(f"Database error getting password: {db_error}")
            return APIResponse(
                success=False,
                error="server_error",
                message="Authentication error"
            )

        # 2. Verify password with bcrypt
        try:
            password_valid = bcrypt.checkpw(
                request.password.encode('utf-8'),
                stored_hash.encode('utf-8')
            )

            if not password_valid:
                logger.warning(f"Invalid password for: {request.email}")
                return APIResponse(
                    success=False,
                    error="unauthorized",
                    message="Invalid credentials"
                )
        except Exception as bcrypt_error:
            logger.error(f"Bcrypt error: {bcrypt_error}")
            return APIResponse(
                success=False,
                error="server_error",
                message="Authentication error"
            )

        # 3. Get user role from database
        user_role = await service.get_user_by_email(request.email)

        if not user_role:
            logger.warning(f"User {request.email} has password but no role")
            return APIResponse(
                success=False,
                error="no_role",
                message="User has no role assigned"
            )

        # 4. Check if account is active
        if not user_role.get("is_active", True):
            return APIResponse(
                success=False,
                error="account_disabled",
                message="Account is disabled"
            )

        # 5. Get redirect URL based on role
        redirect_to = get_redirect_by_role(user_role["role"])

        # 6. Generate JWT token
        payload = {
            "email": user_role["email"],
            "role": user_role["role"],
            "reseller_id": user_role.get("reseller_id"),
            "client_id": user_role.get("client_id"),
            "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS),
            "iat": datetime.utcnow()
        }

        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        # 7. Prepare response data
        login_data = {
            "email": user_role["email"],
            "role": user_role["role"],
            "reseller_id": user_role.get("reseller_id"),
            "client_id": user_role.get("client_id"),
            "redirect_to": redirect_to
        }

        logger.info(f"Successful login for: {request.email}")

        return APIResponse(
            success=True,
            data=login_data,
            token=token,
            message="Login successful"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}", exc_info=True)
        return APIResponse(
            success=False,
            error="server_error",
            message="An error occurred during login"
        )


@router.get("/me", response_model=APIResponse)
async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> APIResponse:
    """
    Get current user from JWT token

    Header: Authorization: Bearer {jwt_token}

    Returns:
    - 200: User data
    - 401: Invalid or missing token

    Verifies JWT token signature and expiration
    """
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid authorization header"
            )

        # Extract token
        token = authorization.replace("Bearer ", "")

        # Verify and decode JWT token
        try:
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM]
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        # Get fresh user data from database to check if still active
        service = get_supabase_service()
        user_role = await service.get_user_by_email(payload["email"])

        if not user_role:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        # Check if still active
        if not user_role.get("is_active", True):
            raise HTTPException(
                status_code=403,
                detail="Account is disabled"
            )

        # Get redirect URL
        redirect_to = get_redirect_by_role(user_role["role"])

        return APIResponse(
            success=True,
            data={
                "email": user_role["email"],
                "role": user_role["role"],
                "reseller_id": user_role.get("reseller_id"),
                "client_id": user_role.get("client_id"),
                "redirect_to": redirect_to,
                "is_active": user_role.get("is_active", True)
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

    NOTE: JWT tokens are stateless. The frontend should delete
    the token from localStorage/cookies. Tokens will expire
    naturally after 7 days.
    """
    return APIResponse(
        success=True,
        data={},
        message="Logout successful"
    )
