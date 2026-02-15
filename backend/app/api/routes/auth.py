"""
Auth API Routes
Role-based authentication with bcrypt + PyJWT
"""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.infrastructure.supabase_service import get_supabase_service
from app.config import settings
import bcrypt
import jwt
from datetime import datetime, timedelta
import logging

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

# JWT Secret from config (fallback for development)
JWT_SECRET = getattr(settings, 'jwt_secret_key', 'omega-raisen-jwt-secret-2026-CHANGE-IN-PRODUCTION')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 7


# ═══════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════

class RegisterRequest(BaseModel):
    """Register new client account"""
    name: str
    email: EmailStr
    password: str
    plan: str = "basic"
    reseller_id: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request with password validation"""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh JWT token"""
    refresh_token: str


class APIResponse(BaseModel):
    """Standard API response"""
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None
    token: Optional[str] = None
    refresh_token: Optional[str] = None
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

@router.post("/register", response_model=APIResponse)
async def register(request: RegisterRequest) -> APIResponse:
    """
    Register new client account

    - **name**: Client name
    - **email**: Client email (must be unique)
    - **password**: Password (min 8 characters)
    - **plan**: Subscription plan (basic/pro/enterprise) - default: basic
    - **reseller_id**: Optional reseller UUID for white-label clients

    Returns:
    - 201: Account created successfully with JWT token
    - 400: Email already exists or validation error
    - 500: Server error

    Password is hashed with bcrypt before storage
    """
    try:
        service = get_supabase_service()

        # 1. Validate password strength (min 8 chars)
        if len(request.password) < 8:
            return APIResponse(
                success=False,
                error="weak_password",
                message="Password must be at least 8 characters"
            )

        # 2. Check if email already exists in clients table
        try:
            existing_client = service.client.table("clients")\
                .select("id, email")\
                .eq("email", request.email)\
                .execute()

            if existing_client.data and len(existing_client.data) > 0:
                return APIResponse(
                    success=False,
                    error="email_exists",
                    message="Email already registered"
                )
        except Exception as db_error:
            logger.error(f"Error checking existing email: {db_error}")
            return APIResponse(
                success=False,
                error="server_error",
                message="Registration error"
            )

        # 3. Hash password with bcrypt
        try:
            password_hash = bcrypt.hashpw(
                request.password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
        except Exception as hash_error:
            logger.error(f"Error hashing password: {hash_error}")
            return APIResponse(
                success=False,
                error="server_error",
                message="Registration error"
            )

        # 4. Generate refresh token
        refresh_token = jwt.encode(
            {
                "email": request.email,
                "type": "refresh",
                "exp": datetime.utcnow() + timedelta(days=30)
            },
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )

        # 5. Create client in database
        try:
            client_data = {
                "name": request.name,
                "email": request.email,
                "password_hash": password_hash,
                "plan": request.plan,
                "role": "client",
                "status": "active",
                "subscription_status": "inactive",
                "trial_active": False,
                "refresh_token": refresh_token
            }

            if request.reseller_id:
                client_data["reseller_id"] = request.reseller_id

            client_response = service.client.table("clients").insert(client_data).execute()

            if not client_response.data:
                return APIResponse(
                    success=False,
                    error="creation_failed",
                    message="Failed to create account"
                )

            new_client = client_response.data[0]
            logger.info(f"New client registered: {request.email}")

        except Exception as db_error:
            logger.error(f"Error creating client: {db_error}")
            return APIResponse(
                success=False,
                error="server_error",
                message="Registration error"
            )

        # 6. Generate access token (JWT)
        access_token = jwt.encode(
            {
                "email": new_client["email"],
                "role": new_client["role"],
                "client_id": new_client["id"],
                "reseller_id": new_client.get("reseller_id"),
                "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS),
                "iat": datetime.utcnow()
            },
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )

        # 7. Return success with tokens
        return APIResponse(
            success=True,
            data={
                "client_id": new_client["id"],
                "email": new_client["email"],
                "name": new_client["name"],
                "plan": new_client["plan"],
                "role": new_client["role"],
                "redirect_to": "/client/dashboard"
            },
            token=access_token,
            refresh_token=refresh_token,
            message="Account created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}", exc_info=True)
        return APIResponse(
            success=False,
            error="server_error",
            message="An error occurred during registration"
        )


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

        # 1. Get password hash from clients table
        try:
            client_response = service.client.table("clients")\
                .select("id, email, password_hash, role, status, reseller_id")\
                .eq("email", request.email)\
                .execute()

            if not client_response.data or len(client_response.data) == 0:
                logger.warning(f"Login attempt for non-existent email: {request.email}")
                return APIResponse(
                    success=False,
                    error="unauthorized",
                    message="Invalid credentials"
                )

            client = client_response.data[0]
            stored_hash = client.get("password_hash")

            if not stored_hash:
                logger.warning(f"Client {request.email} has no password hash")
                return APIResponse(
                    success=False,
                    error="unauthorized",
                    message="Invalid credentials"
                )
        except Exception as db_error:
            logger.error(f"Database error getting client: {db_error}")
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

        # 3. Check if account is active
        if client.get("status") != "active":
            return APIResponse(
                success=False,
                error="account_disabled",
                message="Account is disabled"
            )

        # 4. Check if client has role
        if not client.get("role"):
            logger.warning(f"Client {request.email} has no role assigned")
            return APIResponse(
                success=False,
                error="no_role",
                message="User has no role assigned"
            )

        # 5. Get redirect URL based on role
        redirect_to = get_redirect_by_role(client["role"])

        # 6. Generate JWT token
        payload = {
            "email": client["email"],
            "role": client["role"],
            "reseller_id": client.get("reseller_id"),
            "client_id": client.get("id"),
            "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS),
            "iat": datetime.utcnow()
        }

        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        # 7. Prepare response data
        login_data = {
            "email": client["email"],
            "role": client["role"],
            "reseller_id": client.get("reseller_id"),
            "client_id": client.get("id"),
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


@router.post("/refresh", response_model=APIResponse)
async def refresh_token(request: RefreshTokenRequest) -> APIResponse:
    """
    Refresh JWT access token using refresh token

    - **refresh_token**: Valid refresh token (30 day expiration)

    Returns:
    - 200: New access token generated
    - 401: Invalid or expired refresh token

    Validates refresh token and generates new access token (7 day expiration)
    """
    try:
        # 1. Verify refresh token
        try:
            payload = jwt.decode(
                request.refresh_token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM]
            )

            # Check if token is a refresh token
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token type"
                )

        except jwt.ExpiredSignatureError:
            return APIResponse(
                success=False,
                error="token_expired",
                message="Refresh token expired"
            )
        except jwt.InvalidTokenError:
            return APIResponse(
                success=False,
                error="invalid_token",
                message="Invalid refresh token"
            )

        # 2. Get user from database
        service = get_supabase_service()
        email = payload.get("email")

        client_response = service.client.table("clients")\
            .select("id, email, role, reseller_id, status, refresh_token")\
            .eq("email", email)\
            .execute()

        if not client_response.data:
            return APIResponse(
                success=False,
                error="user_not_found",
                message="User not found"
            )

        client = client_response.data[0]

        # 3. Verify refresh token matches stored token
        if client.get("refresh_token") != request.refresh_token:
            return APIResponse(
                success=False,
                error="token_mismatch",
                message="Invalid refresh token"
            )

        # 4. Check if account is active
        if client.get("status") != "active":
            return APIResponse(
                success=False,
                error="account_inactive",
                message="Account is not active"
            )

        # 5. Generate new access token
        new_access_token = jwt.encode(
            {
                "email": client["email"],
                "role": client["role"],
                "client_id": client["id"],
                "reseller_id": client.get("reseller_id"),
                "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS),
                "iat": datetime.utcnow()
            },
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )

        logger.info(f"Access token refreshed for: {email}")

        return APIResponse(
            success=True,
            token=new_access_token,
            data={
                "email": client["email"],
                "role": client["role"]
            },
            message="Token refreshed successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}", exc_info=True)
        return APIResponse(
            success=False,
            error="server_error",
            message="An error occurred refreshing token"
        )
