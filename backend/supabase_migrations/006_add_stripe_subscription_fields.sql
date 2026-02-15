-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 006: Stripe Subscription Fields
-- Add stripe_subscription_id and subscription_status to clients table
-- ═══════════════════════════════════════════════════════════════

DO $$
BEGIN
  -- Add stripe_subscription_id
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='clients' AND column_name='stripe_subscription_id'
  ) THEN
    ALTER TABLE clients ADD COLUMN stripe_subscription_id VARCHAR(255);
  END IF;

  -- Add subscription_status (separate from general status)
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='clients' AND column_name='subscription_status'
  ) THEN
    ALTER TABLE clients ADD COLUMN subscription_status VARCHAR(50) DEFAULT 'inactive';
  END IF;
END $$;

-- Add index for subscription lookups
CREATE INDEX IF NOT EXISTS idx_clients_stripe_subscription_id ON clients(stripe_subscription_id);
CREATE INDEX IF NOT EXISTS idx_clients_subscription_status ON clients(subscription_status);

-- Add comments
COMMENT ON COLUMN clients.stripe_subscription_id IS 'Stripe subscription ID for recurring billing';
COMMENT ON COLUMN clients.subscription_status IS 'Stripe subscription status: inactive/active/past_due/canceled/trialing';
