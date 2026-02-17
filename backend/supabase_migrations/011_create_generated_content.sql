-- Migration: Create generated_content table
-- Date: 2026-02-17
-- Purpose: Store AI-generated content for social accounts

CREATE TABLE generated_content (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  account_id UUID REFERENCES social_accounts(id) ON DELETE SET NULL,
  context_id UUID REFERENCES client_context(id) ON DELETE SET NULL,
  content_type VARCHAR(50) NOT NULL CHECK (content_type IN (
    'post', 'caption', 'story', 'ad', 'reel_script', 'bio', 'hashtags', 'email'
  )),
  platform VARCHAR(50),
  prompt TEXT NOT NULL,
  generated_text TEXT NOT NULL,
  tokens_used INTEGER DEFAULT 0,
  model_used VARCHAR(100) DEFAULT 'gpt-4o-mini',
  is_saved BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_generated_content_client ON generated_content(client_id);
CREATE INDEX idx_generated_content_account ON generated_content(account_id);
CREATE INDEX idx_generated_content_created ON generated_content(created_at DESC);
CREATE INDEX idx_generated_content_saved ON generated_content(is_saved);

-- Enable RLS
ALTER TABLE generated_content ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "service_role_all_access"
ON generated_content
FOR ALL
TO service_role
USING (true);

CREATE POLICY "Clients access own content"
ON generated_content
FOR ALL
USING (
  client_id IN (
    SELECT id FROM clients
    WHERE id = client_id
  )
);
