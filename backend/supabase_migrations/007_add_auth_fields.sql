-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 007: Authentication Fields
-- Add password_hash, role, and refresh_token to clients table
-- ═══════════════════════════════════════════════════════════════

DO $$
BEGIN
  -- Add password_hash for authentication
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='clients' AND column_name='password_hash'
  ) THEN
    ALTER TABLE clients ADD COLUMN password_hash VARCHAR(255);
  END IF;

  -- Add role for authorization (client, admin, reseller)
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='clients' AND column_name='role'
  ) THEN
    ALTER TABLE clients ADD COLUMN role VARCHAR(50) DEFAULT 'client';
  END IF;

  -- Add refresh_token for JWT refresh flow
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='clients' AND column_name='refresh_token'
  ) THEN
    ALTER TABLE clients ADD COLUMN refresh_token VARCHAR(500);
  END IF;
END $$;

-- Add indexes for authentication lookups
CREATE INDEX IF NOT EXISTS idx_clients_email ON clients(email);
CREATE INDEX IF NOT EXISTS idx_clients_role ON clients(role);

-- Add comments
COMMENT ON COLUMN clients.password_hash IS 'Bcrypt hashed password for authentication';
COMMENT ON COLUMN clients.role IS 'User role: client/admin/reseller';
COMMENT ON COLUMN clients.refresh_token IS 'JWT refresh token for token renewal';
