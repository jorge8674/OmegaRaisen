-- Migration: Create social_accounts table
-- Date: 2026-02-16
-- Purpose: Store social media accounts for clients with plan-based limits

CREATE TABLE IF NOT EXISTS social_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL CHECK (platform IN (
        'instagram',
        'facebook',
        'twitter',
        'linkedin',
        'tiktok',
        'youtube',
        'pinterest'
    )),
    username VARCHAR(255) NOT NULL,
    profile_url TEXT,
    context_id UUID REFERENCES client_context(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_social_accounts_client_id ON social_accounts(client_id);
CREATE INDEX IF NOT EXISTS idx_social_accounts_platform ON social_accounts(platform);
CREATE INDEX IF NOT EXISTS idx_social_accounts_is_active ON social_accounts(is_active);
CREATE INDEX IF NOT EXISTS idx_social_accounts_context_id ON social_accounts(context_id);

-- RLS Policies (match clients table pattern)
ALTER TABLE social_accounts ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own social accounts
CREATE POLICY "Users can view own social accounts"
    ON social_accounts
    FOR SELECT
    USING (
        client_id IN (
            SELECT id FROM clients WHERE user_id = auth.uid()
        )
    );

-- Policy: Users can insert their own social accounts
CREATE POLICY "Users can insert own social accounts"
    ON social_accounts
    FOR INSERT
    WITH CHECK (
        client_id IN (
            SELECT id FROM clients WHERE user_id = auth.uid()
        )
    );

-- Policy: Users can update their own social accounts
CREATE POLICY "Users can update own social accounts"
    ON social_accounts
    FOR UPDATE
    USING (
        client_id IN (
            SELECT id FROM clients WHERE user_id = auth.uid()
        )
    );

-- Policy: Users can delete their own social accounts
CREATE POLICY "Users can delete own social accounts"
    ON social_accounts
    FOR DELETE
    USING (
        client_id IN (
            SELECT id FROM clients WHERE user_id = auth.uid()
        )
    );

-- Comments for documentation
COMMENT ON TABLE social_accounts IS 'Social media accounts for clients with platform-specific context';
COMMENT ON COLUMN social_accounts.platform IS 'Social media platform: instagram, facebook, twitter, linkedin, tiktok, youtube, pinterest';
COMMENT ON COLUMN social_accounts.context_id IS 'Optional platform-specific context reference';
COMMENT ON COLUMN social_accounts.is_active IS 'Soft delete flag - false = deleted';
