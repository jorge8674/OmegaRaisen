"""
Billing API Routes
Stripe integration for subscriptions and payments
"""
from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel, Field
from typing import Optional
from app.config import settings
import stripe
import logging

router = APIRouter(prefix="/billing", tags=["billing"])
logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.stripe_secret_key


# ═══════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════

class CreateCheckoutSessionRequest(BaseModel):
    """Request to create Stripe checkout session"""
    client_id: str = Field(..., description="Client UUID")
    plan: str = Field(..., description="basic|pro|enterprise")
    trial: bool = Field(default=False, description="Enable trial period")


class CheckoutSessionResponse(BaseModel):
    """Checkout session response"""
    success: bool
    checkout_url: Optional[str] = None
    session_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


class CancelSubscriptionRequest(BaseModel):
    """Request to cancel subscription"""
    client_id: str = Field(..., description="Client UUID")


class SubscriptionStatusResponse(BaseModel):
    """Subscription status response"""
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None
    error: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_price_id(plan: str) -> str:
    """Get Stripe price ID for plan"""
    plan_prices = {
        "basic": settings.stripe_price_basic,
        "pro": settings.stripe_price_pro,
        "enterprise": settings.stripe_price_enterprise
    }

    price_id = plan_prices.get(plan.lower())
    if not price_id:
        raise ValueError(f"Invalid plan: {plan}")

    return price_id


# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(request: CreateCheckoutSessionRequest) -> CheckoutSessionResponse:
    """
    Create Stripe Checkout session for subscription

    - **client_id**: Client UUID to associate subscription
    - **plan**: Subscription plan (basic|pro|enterprise)
    - **trial**: Enable trial period (default: false)

    Returns:
    - 200: Checkout session created, returns checkout_url
    - 400: Invalid plan or missing price ID
    - 500: Stripe API error
    """
    try:
        # Validate plan
        valid_plans = ["basic", "pro", "enterprise"]
        if request.plan.lower() not in valid_plans:
            return CheckoutSessionResponse(
                success=False,
                error="invalid_plan",
                message=f"Plan must be one of: {', '.join(valid_plans)}"
            )

        # Get price ID
        try:
            price_id = get_price_id(request.plan)
        except ValueError as e:
            return CheckoutSessionResponse(
                success=False,
                error="invalid_plan",
                message=str(e)
            )

        if not price_id:
            return CheckoutSessionResponse(
                success=False,
                error="missing_price_id",
                message=f"Stripe price ID not configured for plan: {request.plan}"
            )

        # Create checkout session
        checkout_params = {
            "mode": "subscription",
            "line_items": [{
                "price": price_id,
                "quantity": 1
            }],
            "success_url": f"https://r-omega.agency/dashboard?session_id={{CHECKOUT_SESSION_ID}}",
            "cancel_url": "https://r-omega.agency/pricing",
            "metadata": {
                "client_id": request.client_id,
                "plan": request.plan
            }
        }

        # Add trial if requested
        if request.trial:
            checkout_params["subscription_data"] = {
                "trial_period_days": 14
            }

        session = stripe.checkout.Session.create(**checkout_params)

        logger.info(f"Checkout session created for client {request.client_id}, plan: {request.plan}")

        return CheckoutSessionResponse(
            success=True,
            checkout_url=session.url,
            session_id=session.id,
            message="Checkout session created successfully"
        )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session: {e}")
        return CheckoutSessionResponse(
            success=False,
            error="stripe_error",
            message=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        return CheckoutSessionResponse(
            success=False,
            error="server_error",
            message="An error occurred creating checkout session"
        )


@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: Optional[str] = Header(None)):
    """
    Stripe webhook endpoint

    Receives events from Stripe:
    - checkout.session.completed: Subscription created
    - customer.subscription.updated: Subscription changed
    - customer.subscription.deleted: Subscription cancelled

    Verifies webhook signature and updates client subscription in database
    """
    try:
        payload = await request.body()

        # Verify webhook signature
        if not settings.stripe_webhook_secret:
            logger.warning("Stripe webhook secret not configured - skipping signature verification")
            event = stripe.Event.construct_from(
                stripe.util.json.loads(payload), stripe.api_key
            )
        else:
            try:
                event = stripe.Webhook.construct_event(
                    payload,
                    stripe_signature,
                    settings.stripe_webhook_secret
                )
            except stripe.error.SignatureVerificationError as e:
                logger.error(f"Webhook signature verification failed: {e}")
                raise HTTPException(status_code=400, detail="Invalid signature")

        # Handle event
        event_type = event["type"]
        logger.info(f"Received Stripe webhook: {event_type}")

        if event_type == "checkout.session.completed":
            session = event["data"]["object"]
            client_id = session.get("metadata", {}).get("client_id")
            plan = session.get("metadata", {}).get("plan")
            subscription_id = session.get("subscription")
            customer_id = session.get("customer")

            logger.info(f"Checkout completed - Client: {client_id}, Plan: {plan}, Subscription: {subscription_id}")

            # Update client subscription in database
            if client_id and plan and subscription_id:
                from app.infrastructure.supabase_service import get_supabase_service
                supabase = get_supabase_service()
                await supabase.update_client_subscription(
                    client_id=client_id,
                    stripe_customer_id=customer_id,
                    stripe_subscription_id=subscription_id,
                    plan=plan,
                    subscription_status="active"
                )
                logger.info(f"Client {client_id} subscription activated in database")

        elif event_type == "customer.subscription.updated":
            subscription = event["data"]["object"]
            subscription_id = subscription["id"]
            status = subscription["status"]

            logger.info(f"Subscription updated - ID: {subscription_id}, Status: {status}")

            # TODO: Update subscription status in database
            # await update_subscription_status(subscription_id, status)

        elif event_type == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            subscription_id = subscription["id"]

            logger.info(f"Subscription deleted - ID: {subscription_id}")

            # Cancel subscription in database
            from app.infrastructure.supabase_service import get_supabase_service
            supabase = get_supabase_service()
            result = await supabase.cancel_client_subscription(subscription_id)
            if result:
                logger.info(f"Subscription {subscription_id} cancelled in database")
            else:
                logger.warning(f"No client found with subscription {subscription_id}")

        else:
            logger.info(f"Unhandled event type: {event_type}")

        return {"received": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.post("/cancel-subscription", response_model=SubscriptionStatusResponse)
async def cancel_subscription(request: CancelSubscriptionRequest) -> SubscriptionStatusResponse:
    """
    Cancel client subscription

    - **client_id**: Client UUID

    Returns:
    - 200: Subscription cancelled (will cancel at period end)
    - 404: Subscription not found
    - 500: Stripe API error
    """
    try:
        # Get subscription_id from database using client_id
        from app.infrastructure.supabase_service import get_supabase_service
        supabase = get_supabase_service()
        subscription_data = await supabase.get_client_subscription(request.client_id)

        if not subscription_data:
            return SubscriptionStatusResponse(
                success=False,
                error="not_found",
                message="No client found with this ID"
            )

        stripe_subscription_id = subscription_data.get("stripe_subscription_id")
        if not stripe_subscription_id:
            return SubscriptionStatusResponse(
                success=False,
                error="no_subscription",
                message="Client has no active Stripe subscription to cancel"
            )

        # Cancel subscription in Stripe (at period end)
        subscription = stripe.Subscription.modify(
            stripe_subscription_id,
            cancel_at_period_end=True
        )

        logger.info(f"Subscription {stripe_subscription_id} will cancel at period end for client {request.client_id}")

        return SubscriptionStatusResponse(
            success=True,
            data={
                "subscription_id": stripe_subscription_id,
                "status": "cancelling",
                "cancel_at": subscription.cancel_at,
                "cancel_at_period_end": subscription.cancel_at_period_end
            },
            message="Subscription will be cancelled at period end"
        )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error cancelling subscription: {e}")
        return SubscriptionStatusResponse(
            success=False,
            error="stripe_error",
            message=str(e)
        )
    except Exception as e:
        logger.error(f"Error cancelling subscription: {e}")
        return SubscriptionStatusResponse(
            success=False,
            error="server_error",
            message="An error occurred cancelling subscription"
        )


@router.get("/subscription/{client_id}", response_model=SubscriptionStatusResponse)
async def get_subscription_status(client_id: str) -> SubscriptionStatusResponse:
    """
    Get subscription status for client

    - **client_id**: Client UUID

    Returns:
    - 200: Subscription status
    - 404: Subscription not found
    - 500: Stripe API error
    """
    try:
        # Get subscription from database using client_id
        from app.infrastructure.supabase_service import get_supabase_service
        supabase = get_supabase_service()
        subscription_data = await supabase.get_client_subscription(client_id)

        if not subscription_data:
            return SubscriptionStatusResponse(
                success=False,
                error="not_found",
                message="No subscription found for this client"
            )

        # Check if client has a Stripe subscription
        stripe_subscription_id = subscription_data.get("stripe_subscription_id")
        if not stripe_subscription_id:
            # Return local data if no Stripe subscription
            return SubscriptionStatusResponse(
                success=True,
                data={
                    "client_id": client_id,
                    "subscription_id": None,
                    "status": subscription_data.get("subscription_status", "inactive"),
                    "plan": subscription_data.get("plan"),
                    "trial_active": subscription_data.get("trial_active", False)
                },
                message="Client exists but has no active Stripe subscription"
            )

        # Get live status from Stripe
        subscription = stripe.Subscription.retrieve(stripe_subscription_id)

        return SubscriptionStatusResponse(
            success=True,
            data={
                "client_id": client_id,
                "subscription_id": subscription.id,
                "status": subscription.status,
                "plan": subscription_data.get("plan"),
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "trial_active": subscription_data.get("trial_active", False)
            },
            message="Subscription status retrieved"
        )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error getting subscription: {e}")
        return SubscriptionStatusResponse(
            success=False,
            error="stripe_error",
            message=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting subscription status: {e}")
        return SubscriptionStatusResponse(
            success=False,
            error="server_error",
            message="An error occurred getting subscription status"
        )
