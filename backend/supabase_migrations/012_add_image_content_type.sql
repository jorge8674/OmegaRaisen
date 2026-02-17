-- Migration: Add 'image' to generated_content content_type
-- Date: 2026-02-17
-- Purpose: Allow DALL-E 3 image generation content type

-- Drop existing constraint
ALTER TABLE generated_content
DROP CONSTRAINT IF EXISTS generated_content_content_type_check;

-- Add new constraint with 'image' type
ALTER TABLE generated_content
ADD CONSTRAINT generated_content_content_type_check
CHECK (content_type IN (
  'post', 'caption', 'story', 'ad', 'reel_script',
  'bio', 'hashtags', 'email', 'image'
));
