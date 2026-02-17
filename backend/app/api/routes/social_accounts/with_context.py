"""
Social Account With Context Endpoints
POST /social-accounts/with-context/ - Create account + context in one operation
PATCH /social-accounts/with-context/{account_id}/ - Update account + context
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional, List
import logging
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.api.routes.social_accounts.models import (
    SocialAccountProfile,
    SocialAccountResponse,
    PlatformOption
)
from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.repositories.social_account_repository import social_account_repository
from app.infrastructure.repositories.client_repository import client_repository
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Plan limits for social accounts
PLAN_LIMITS = {
    "basic": 2,
    "pro": 5,
    "enterprise": float('inf')
}


class ContextData(BaseModel):
    """Embedded context data for social account - matches client_context schema"""
    business_name: str = Field(..., min_length=1, max_length=200)
    industry: str = Field(..., min_length=1, max_length=100)
    business_description: Optional[str] = Field(default=None, max_length=1000)
    communication_tone: str = Field(default="casual")
    primary_goal: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    forbidden_words: List[str] = Field(default_factory=list)
    forbidden_topics: List[str] = Field(default_factory=list)
    brand_colors: List[str] = Field(default_factory=list)
    website_url: Optional[str] = Field(default=None, max_length=500)
    custom_instructions: Optional[str] = None


class SocialAccountWithContextCreate(BaseModel):
    """Create social account with embedded context"""
    client_id: str = Field(..., description="Client UUID")
    platform: PlatformOption = Field(..., description="Social media platform")
    username: str = Field(..., min_length=1, max_length=255)
    profile_url: Optional[str] = Field(default=None, max_length=500)
    context: ContextData = Field(..., description="Context data for this account")


class SocialAccountWithContextUpdate(BaseModel):
    """Update social account and/or context"""
    username: Optional[str] = Field(default=None, min_length=1, max_length=255)
    profile_url: Optional[str] = Field(default=None, max_length=500)
    context: Optional[ContextData] = None


@router.post("/", response_model=SocialAccountResponse)
async def create_account_with_context(
    request: SocialAccountWithContextCreate,
    authorization: Optional[str] = Header(None)
) -> SocialAccountResponse:
    """
    Create social account with its own context in one operation.
    Validates plan limits and creates both context and account.
    """
    try:
        # 1. Get authenticated user
        user = await get_current_user(authorization)
        role = user["role"]
        authenticated_id = user["id"]

        # 2. Extract client_id
        client_id = request.client_id

        # 3. Verify client exists and user has access
        client = await client_repository.get_client(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        # 4. Role-based access control
        if role == "reseller" and client.get("reseller_id") != authenticated_id:
            raise HTTPException(
                status_code=403,
                detail="Resellers can only create accounts for their clients"
            )
        elif role == "client" and client_id != authenticated_id:
            raise HTTPException(
                status_code=403,
                detail="Clients can only create accounts for themselves"
            )

        # 5. Validate plan limits
        client_plan = client.get("plan", "basic")
        plan_limit = PLAN_LIMITS.get(client_plan, 2)

        existing_accounts = await social_account_repository.list_accounts(
            client_id=client_id
        )
        active_count = len([acc for acc in existing_accounts if acc.get("is_active", True)])

        if active_count >= plan_limit:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"Plan limit reached. {client_plan.capitalize()} plan allows "
                    f"up to {int(plan_limit)} social account(s). Upgrade to add more."
                )
            )

        # 6. Create context first
        supabase_service = get_supabase_service()
        context_data = {
            "client_id": client_id,
            "business_name": request.context.business_name,
            "industry": request.context.industry,
            "business_description": request.context.business_description,
            "communication_tone": request.context.communication_tone,
            "primary_goal": request.context.primary_goal,
            "keywords": request.context.keywords,
            "forbidden_words": request.context.forbidden_words,
            "forbidden_topics": request.context.forbidden_topics,
            "brand_colors": request.context.brand_colors,
            "website_url": request.context.website_url,
            "custom_instructions": request.context.custom_instructions,
            "target_audience": {},
            "platforms": [],
            "is_active": True,
            "version": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        context_result = supabase_service.client.table("client_context")\
            .insert(context_data)\
            .execute()

        if not context_result.data:
            raise HTTPException(status_code=500, detail="Failed to create context")

        context_id = context_result.data[0]["id"]
        logger.info(f"Context created: {context_id} for client {client_id}")

        # 7. Create social account with context_id
        account_data = {
            "client_id": client_id,
            "platform": request.platform,
            "username": request.username,
            "profile_url": request.profile_url,
            "context_id": context_id,
            "scraping_enabled": True,
            "scraped_data": {},
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        created_account = await social_account_repository.create_account(account_data)

        logger.info(
            f"Social account with context created: {request.platform} - "
            f"{request.username} for client {client_id}"
        )

        return SocialAccountResponse(
            success=True,
            data=SocialAccountProfile(**created_account),
            message="Social account with context created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating account with context: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while creating account with context"
        )


@router.patch("/{account_id}/", response_model=SocialAccountResponse)
async def update_account_with_context(
    account_id: str,
    request: SocialAccountWithContextUpdate,
    authorization: Optional[str] = Header(None)
) -> SocialAccountResponse:
    """
    Update social account and optionally its context.
    """
    try:
        # 1. Get authenticated user
        user = await get_current_user(authorization)
        role = user["role"]
        authenticated_id = user["id"]

        # 2. Get account
        account = await social_account_repository.get_account(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Social account not found")

        # 3. Verify access
        client_id = account.get("client_id")
        client = await client_repository.get_client(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        # 4. Role-based access control
        if role == "client":
            raise HTTPException(
                status_code=403,
                detail="Clients cannot update social accounts"
            )
        elif role == "reseller" and client.get("reseller_id") != authenticated_id:
            raise HTTPException(
                status_code=403,
                detail="Resellers can only update their clients' accounts"
            )

        # 5. Update context if provided
        if request.context and account.get("context_id"):
            supabase_service = get_supabase_service()
            context_updates = {
                "business_name": request.context.business_name,
                "industry": request.context.industry,
                "business_description": request.context.business_description,
                "communication_tone": request.context.communication_tone,
                "primary_goal": request.context.primary_goal,
                "keywords": request.context.keywords,
                "forbidden_words": request.context.forbidden_words,
                "forbidden_topics": request.context.forbidden_topics,
                "brand_colors": request.context.brand_colors,
                "website_url": request.context.website_url,
                "custom_instructions": request.context.custom_instructions,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

            context_result = supabase_service.client.table("client_context")\
                .update(context_updates)\
                .eq("id", account["context_id"])\
                .execute()

            if not context_result.data:
                logger.warning(f"Failed to update context {account['context_id']}")

        # 6. Update account
        account_updates = {}
        if request.username is not None:
            account_updates["username"] = request.username
        if request.profile_url is not None:
            account_updates["profile_url"] = request.profile_url

        if account_updates:
            updated_account = await social_account_repository.update_account(
                account_id, account_updates
            )
            logger.info(f"Social account {account_id} updated")
        else:
            updated_account = account

        return SocialAccountResponse(
            success=True,
            data=SocialAccountProfile(**updated_account),
            message="Social account updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating account with context: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while updating account"
        )
