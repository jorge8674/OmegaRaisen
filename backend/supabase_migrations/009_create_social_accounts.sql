-- Migration: Create social_accounts table
-- Date: 2026-02-16
-- Purpose: Store social media accounts for clients with plan-based limits

-- Drop table if exists (for clean recreation)
DROP TABLE IF EXISTS social_accounts CASCADE;

-- Create social_accounts table
CREATE TABLE social_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('instagram', 'facebook', 'twitter', 'linkedin', 'tiktok', 'youtube', 'pinterest')),
    username VARCHAR(255) NOT NULL,
    profile_url TEXT,
    context_id UUID REFERENCES client_context(id) ON DELETE SET NULL,
    scraping_enabled BOOLEAN DEFAULT true,
    scraped_data JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_client_platform_username UNIQUE (client_id, platform, username)
);

-- Create indexes for performance
CREATE INDEX idx_social_accounts_client ON social_accounts(client_id);
CREATE INDEX idx_social_accounts_platform ON social_accounts(platform);
CREATE INDEX idx_social_accounts_context ON social_accounts(context_id);
CREATE INDEX idx_social_accounts_active ON social_accounts(is_active);

-- Enable RLS
ALTER TABLE social_accounts ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "service_role_all_access"
ON social_accounts
FOR ALL
TO service_role
USING (true);

CREATE POLICY "users_read_own_accounts"
ON social_accounts
FOR SELECT
TO authenticated
USING (client_id IN (SELECT id FROM clients WHERE id = auth.uid()));

CREATE POLICY "users_insert_own_accounts"
ON social_accounts
FOR INSERT
TO authenticated
WITH CHECK (client_id IN (SELECT id FROM clients WHERE id = auth.uid()));

CREATE POLICY "users_update_own_accounts"
ON social_accounts
FOR UPDATE
TO authenticated
USING (client_id IN (SELECT id FROM clients WHERE id = auth.uid()));
