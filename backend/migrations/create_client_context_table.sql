-- Client Context Table Migration
-- Shared memory across agents for client-specific context
-- Filosofía: No velocity, only precision 🐢💎

-- ============================================
-- TABLE: client_context
-- Stores shared context and learning for each client
-- ============================================
CREATE TABLE IF NOT EXISTS client_context (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID UNIQUE NOT NULL,

    -- Brand Identity
    niche TEXT,
    tone TEXT,
    brand_voice JSONB DEFAULT '{}'::jsonb,
    target_audience TEXT,

    -- Competitive Intelligence
    competitors JSONB DEFAULT '[]'::jsonb,

    -- Performance Data
    best_performing_content JSONB DEFAULT '[]'::jsonb,
    posting_patterns JSONB DEFAULT '{}'::jsonb,

    -- Analytics Insights
    avg_engagement_rate DECIMAL(5, 2),
    peak_posting_hours JSONB DEFAULT '[]'::jsonb,
    top_hashtags JSONB DEFAULT '[]'::jsonb,
    audience_demographics JSONB DEFAULT '{}'::jsonb,

    -- Content Preferences
    content_themes JSONB DEFAULT '[]'::jsonb,
    avoided_topics JSONB DEFAULT '[]'::jsonb,
    preferred_formats JSONB DEFAULT '[]'::jsonb,

    -- Metadata
    last_updated_by TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDEXES for performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_client_context_client_id
ON client_context(client_id);

CREATE INDEX IF NOT EXISTS idx_client_context_updated_at
ON client_context(updated_at DESC);

-- ============================================
-- TRIGGER for updated_at
-- ============================================
DROP TRIGGER IF EXISTS update_client_context_updated_at ON client_context;
CREATE TRIGGER update_client_context_updated_at
    BEFORE UPDATE ON client_context
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- COMMENT
-- ============================================
COMMENT ON TABLE client_context IS 'Shared memory and learning context for each client, used by all agents';
COMMENT ON COLUMN client_context.brand_voice IS 'JSON object with tone attributes, vocabulary, style guidelines';
COMMENT ON COLUMN client_context.competitors IS 'Array of competitor objects with names and insights';
COMMENT ON COLUMN client_context.best_performing_content IS 'Array of top-performing posts with metrics';
COMMENT ON COLUMN client_context.posting_patterns IS 'JSON object with optimal times, frequency, days';
