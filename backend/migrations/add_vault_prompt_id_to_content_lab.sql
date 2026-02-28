-- Migration: Add vault_prompt_id column to content_lab_generated
-- Purpose: Track which vault prompt was used for performance feedback
-- Date: 2026-02-28

-- Add column to track which prompt from vault was used
ALTER TABLE content_lab_generated
ADD COLUMN IF NOT EXISTS vault_prompt_id UUID REFERENCES prompt_vault(id);

-- Add index for faster lookup
CREATE INDEX IF NOT EXISTS idx_content_lab_vault_prompt
ON content_lab_generated(vault_prompt_id);

-- Comment for documentation
COMMENT ON COLUMN content_lab_generated.vault_prompt_id IS
'References the prompt from prompt_vault that was used to generate this content. NULL if default prompt builder was used.';

-- Verify migration
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'content_lab_generated'
  AND column_name = 'vault_prompt_id';
