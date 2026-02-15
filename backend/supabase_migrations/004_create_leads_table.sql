-- =============================================
-- OMEGA LEADS TABLE
-- Migration 004: Create leads table
-- Purpose: Store leads from reseller landing pages
-- =============================================

-- Leads from contact forms
CREATE TABLE IF NOT EXISTS leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reseller_id UUID NOT NULL REFERENCES resellers(id) ON DELETE CASCADE,

  -- Contact info
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  phone VARCHAR(50),
  message TEXT,

  -- Source tracking
  source VARCHAR(100) DEFAULT 'landing_page',

  -- Status
  status VARCHAR(50) DEFAULT 'new',  -- new, contacted, qualified, converted, lost
  notes TEXT,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  contacted_at TIMESTAMPTZ
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_leads_reseller ON leads(reseller_id);
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at DESC);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_leads_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_leads_timestamp
  BEFORE UPDATE ON leads
  FOR EACH ROW
  EXECUTE FUNCTION update_leads_updated_at();

-- Comments
COMMENT ON TABLE leads IS 'Leads from reseller landing pages and contact forms';
COMMENT ON COLUMN leads.source IS 'Lead source: landing_page, referral, manual, etc.';
COMMENT ON COLUMN leads.status IS 'Lead status: new, contacted, qualified, converted, lost';
