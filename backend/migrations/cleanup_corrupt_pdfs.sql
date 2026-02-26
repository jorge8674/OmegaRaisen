-- Cleanup: Remove corrupt PDF documents from context_library
-- These documents contain raw PDF binary (%PDF-1.4...) instead of extracted text
-- User should re-upload using /extract-url/ endpoint

DELETE FROM context_library
WHERE id IN (
  'b8c36dbf-ddb9-40f3-95c0-256912b11ecb',  -- Presentacion milagrosa
  '60c84d4b-8655-4cce-b63d-0290f959fcfd'   -- Milagrosa
);

-- Expected result: 2 rows deleted
