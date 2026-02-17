-- Migration: Create brand_files system with Supabase Storage
-- Date: 2026-02-17
-- Purpose: Store brand guideline files (PDFs, docs, images) for clients

-- 1. Create bucket brand-guides in Supabase Storage
-- NOTE: This must be run in Supabase Storage Dashboard or via SQL:
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'brand-guides',
  'brand-guides',
  false,
  52428800, -- 50MB max per file (Enterprise plan)
  ARRAY[
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'image/png',
    'image/jpeg',
    'image/webp'
  ]
);

-- 2. RLS: Only the account owner can access their files
CREATE POLICY "Clients access own files"
ON storage.objects FOR ALL
USING (
  bucket_id = 'brand-guides' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- 3. Create brand_files table for file tracking
CREATE TABLE brand_files (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  file_name VARCHAR(255) NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  mime_type VARCHAR(100) NOT NULL,
  storage_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_brand_files_client ON brand_files(client_id);
CREATE INDEX idx_brand_files_created ON brand_files(created_at DESC);

-- Enable RLS
ALTER TABLE brand_files ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "service_role_all_access"
ON brand_files
FOR ALL
TO service_role
USING (true);

CREATE POLICY "Owner access brand_files"
ON brand_files FOR ALL
USING (
  client_id IN (
    SELECT id FROM clients
    WHERE id = client_id
  )
);
