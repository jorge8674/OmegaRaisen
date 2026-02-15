-- =============================================
-- OMEGA BRANDING PRICING PLANS
-- Migration 005: Add pricing_plans column
-- Purpose: Store pricing tiers for reseller landing pages
-- =============================================

-- Add pricing_plans column to reseller_branding
ALTER TABLE reseller_branding
ADD COLUMN IF NOT EXISTS pricing_plans JSONB DEFAULT '[]';

-- Comment
COMMENT ON COLUMN reseller_branding.pricing_plans IS 'Array of pricing plan objects with structure: {name, price, features[], cta_text, etc.}';
