"""
Billing Webhook Endpoint
Stripe webhook event handler for subscription lifecycle
"""
import os
from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
from app.api.routes.billing.stripe_config import stripe
from app.infrastructure.supabase_service import get_supabase_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Fail-fast validation for webhook secret
STRIPE_WEBHOOK_SECRET: str = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
if not STRIPE_WEBHOOK_SECRET:
    raise RuntimeError(
        "STRIPE_WEBHOOK_SECRET environment variable is not set. "
        "Configure it in Railway before deploying."
    )


@router.post("/webhook")
async def stripe_webhook(request: Request) -> Dict[str, bool]:
    """
    Stripe webhook endpoint for subscription events

    Handles:
        - checkout.session.completed: Activates subscription in DB
        - customer.subscription.updated: Updates subscription status (TODO)
        - customer.subscription.deleted: Cancels subscription in DB

    Verifies webhook signature using STRIPE_WEBHOOK_SECRET

    Returns:
        {"received": True} on success

    Raises:
        HTTPException 400: Invalid signature or payload
        HTTPException 500: Processing error
    """
    try:
        # Get raw body as bytes
        payload = await request.body()

        # Get Stripe signature header
        sig_header = request.headers.get("stripe-signature")
        if not sig_header:
            raise HTTPException(status_code=400, detail="Missing stripe-signature header")

        # Verify webhook signature and construct event
        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {e}")
            raise HTTPException(status_code=400, detail="Invalid signature")
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid payload")

        # Handle event
        event_type = event["type"]
        logger.info(f"Received Stripe webhook: {event_type}")

        if event_type == "checkout.session.completed":
            await handle_checkout_completed(event)

        elif event_type == "customer.subscription.updated":
            await handle_subscription_updated(event)

        elif event_type == "customer.subscription.deleted":
            await handle_subscription_deleted(event)

        else:
            logger.info(f"Unhandled event type: {event_type}")

        return {"received": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Webhook processing failed")


async def handle_checkout_completed(event: Dict[str, Any]) -> None:
    """
    Handle checkout.session.completed event

    Activates client subscription in database

    Args:
        event: Stripe event object with session data

    Extracts client_id and plan from session.metadata and calls
    update_client_subscription() to mark subscription as active
    """
    session = event["data"]["object"]
    client_id = session.get("metadata", {}).get("client_id")
    plan = session.get("metadata", {}).get("plan")
    subscription_id = session.get("subscription")
    customer_id = session.get("customer")

    logger.info(
        f"Checkout completed - Client: {client_id}, Plan: {plan}, "
        f"Subscription: {subscription_id}"
    )

    if client_id and plan and subscription_id:
        supabase = get_supabase_service()
        await supabase.update_client_subscription(
            client_id=client_id,
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_id,
            plan=plan,
            subscription_status="active"
        )
        logger.info(f"Client {client_id} subscription activated in database")
    else:
        logger.warning(
            f"Missing required data in checkout.session.completed: "
            f"client_id={client_id}, plan={plan}, subscription_id={subscription_id}"
        )


async def handle_subscription_updated(event: Dict[str, Any]) -> None:
    """
    Handle customer.subscription.updated event

    TODO CRÍTICO: Sin este handler, el estado "cancelling" de
    cancel_at_period_end=True no se refleja en DB hasta que
    expire el período.

    Arquitectura:
    - POST /cancel-subscription llama stripe.Subscription.modify(cancel_at_period_end=True)
    - Stripe dispara customer.subscription.updated inmediatamente con status="active"
      pero cancel_at_period_end=True
    - customer.subscription.deleted NO se dispara hasta el fin del período
    - Por lo tanto, este handler es necesario para reflejar el estado
      "cancelling" en la UI del cliente

    Args:
        event: Stripe event object with subscription data

    Need to implement update_subscription_status() in supabase_service
    to handle status changes (active, past_due, canceling, canceled, etc.)

    Technical Debt: This event should sync Stripe subscription status
    to clients.subscription_status in database for real-time accuracy.
    """
    subscription = event["data"]["object"]
    subscription_id = subscription["id"]
    status = subscription["status"]

    logger.info(f"Subscription updated - ID: {subscription_id}, Status: {status}")

    # TODO: Implement database update
    # supabase = get_supabase_service()
    # await supabase.update_subscription_status(subscription_id, status)

    logger.warning("Subscription update not yet implemented - logged only")


async def handle_subscription_deleted(event: Dict[str, Any]) -> None:
    """
    Handle customer.subscription.deleted event

    Cancels client subscription in database

    Args:
        event: Stripe event object with subscription data

    Calls cancel_client_subscription() to mark subscription as
    cancelled and clear plan in database
    """
    subscription = event["data"]["object"]
    subscription_id = subscription["id"]

    logger.info(f"Subscription deleted - ID: {subscription_id}")

    supabase = get_supabase_service()
    result = await supabase.cancel_client_subscription(subscription_id)

    if result:
        logger.info(f"Subscription {subscription_id} cancelled in database")
    else:
        logger.warning(f"No client found with subscription {subscription_id}")
