-- Context Library Migration
-- Global knowledge base for NOVA and all agents
-- Filosofía: No velocity, only precision 🐢💎

CREATE TABLE IF NOT EXISTS public.context_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    content TEXT NOT NULL,
    scope TEXT NOT NULL CHECK (scope IN ('global','client','department')),
    scope_id TEXT,  -- NULL if global, client_id if scope=client, dept name if scope=department
    file_type TEXT DEFAULT 'text',  -- text, pdf, md, docx
    tags TEXT[] DEFAULT '{}',
    created_by TEXT DEFAULT 'ibrain',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_ctx_scope ON context_library(scope, scope_id);
CREATE INDEX IF NOT EXISTS idx_ctx_active ON context_library(is_active);
CREATE INDEX IF NOT EXISTS idx_ctx_created_at ON context_library(created_at DESC);

-- RLS (Row Level Security)
ALTER TABLE context_library ENABLE ROW LEVEL SECURITY;

CREATE POLICY "all_access_authenticated" ON context_library
FOR ALL TO authenticated
USING (true) WITH CHECK (true);

CREATE POLICY "all_access_anon" ON context_library
FOR ALL TO anon
USING (true) WITH CHECK (true);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_context_library_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_context_library_updated_at ON context_library;
CREATE TRIGGER update_context_library_updated_at
    BEFORE UPDATE ON context_library
    FOR EACH ROW
    EXECUTE FUNCTION update_context_library_updated_at();
