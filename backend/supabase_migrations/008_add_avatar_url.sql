-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 008: Avatar URL
-- Add avatar_url column to clients table for profile pictures
-- ═══════════════════════════════════════════════════════════════

DO $$
BEGIN
  -- Add avatar_url for profile pictures
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='clients' AND column_name='avatar_url'
  ) THEN
    ALTER TABLE clients ADD COLUMN avatar_url VARCHAR(500);
  END IF;
END $$;

-- Add comment
COMMENT ON COLUMN clients.avatar_url IS 'URL to user profile avatar in Supabase Storage';
