-- ═══════════════════════════════════════════════════════════════
-- MIGRACIÓN 003: Agregar campos adicionales a reseller_branding
-- Para compatibilidad con frontend OMEGA
-- ═══════════════════════════════════════════════════════════════

DO $$
BEGIN
  -- Hero section fields
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='reseller_branding' AND column_name='hero_title'
  ) THEN
    ALTER TABLE reseller_branding ADD COLUMN hero_title VARCHAR(255);
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='reseller_branding' AND column_name='hero_subtitle'
  ) THEN
    ALTER TABLE reseller_branding ADD COLUMN hero_subtitle VARCHAR(500);
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='reseller_branding' AND column_name='hero_cta_url'
  ) THEN
    ALTER TABLE reseller_branding ADD COLUMN hero_cta_url VARCHAR(500);
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='reseller_branding' AND column_name='agency_name'
  ) THEN
    ALTER TABLE reseller_branding ADD COLUMN agency_name VARCHAR(255);
  END IF;

  -- Content sections as JSONB objects
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='reseller_branding' AND column_name='pain_section'
  ) THEN
    ALTER TABLE reseller_branding ADD COLUMN pain_section JSONB;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='reseller_branding' AND column_name='solutions_section'
  ) THEN
    ALTER TABLE reseller_branding ADD COLUMN solutions_section JSONB;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='reseller_branding' AND column_name='services_section'
  ) THEN
    ALTER TABLE reseller_branding ADD COLUMN services_section JSONB;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='reseller_branding' AND column_name='metrics_section'
  ) THEN
    ALTER TABLE reseller_branding ADD COLUMN metrics_section JSONB;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='reseller_branding' AND column_name='process_section'
  ) THEN
    ALTER TABLE reseller_branding ADD COLUMN process_section JSONB;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='reseller_branding' AND column_name='testimonials_section'
  ) THEN
    ALTER TABLE reseller_branding ADD COLUMN testimonials_section JSONB;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='reseller_branding' AND column_name='client_logos_section'
  ) THEN
    ALTER TABLE reseller_branding ADD COLUMN client_logos_section JSONB;
  END IF;

  -- Contact fields (aliases for footer_email/footer_phone)
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='reseller_branding' AND column_name='contact_email'
  ) THEN
    ALTER TABLE reseller_branding ADD COLUMN contact_email VARCHAR(255);
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='reseller_branding' AND column_name='contact_phone'
  ) THEN
    ALTER TABLE reseller_branding ADD COLUMN contact_phone VARCHAR(50);
  END IF;

  -- Footer
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='reseller_branding' AND column_name='footer_text'
  ) THEN
    ALTER TABLE reseller_branding ADD COLUMN footer_text TEXT;
  END IF;

  -- Rename hero_media_type to hero_type for consistency
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='reseller_branding' AND column_name='hero_media_type'
  ) AND NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='reseller_branding' AND column_name='hero_type'
  ) THEN
    ALTER TABLE reseller_branding RENAME COLUMN hero_media_type TO hero_type;
  END IF;

END $$;

-- COMENTARIOS
COMMENT ON COLUMN reseller_branding.hero_title IS 'Título principal del hero';
COMMENT ON COLUMN reseller_branding.hero_subtitle IS 'Subtítulo del hero';
COMMENT ON COLUMN reseller_branding.hero_cta_url IS 'URL del botón CTA del hero';
COMMENT ON COLUMN reseller_branding.pain_section IS 'Sección de pain points (objeto JSON)';
COMMENT ON COLUMN reseller_branding.solutions_section IS 'Sección de soluciones (objeto JSON)';
COMMENT ON COLUMN reseller_branding.services_section IS 'Sección de servicios (objeto JSON)';
COMMENT ON COLUMN reseller_branding.metrics_section IS 'Sección de métricas (objeto JSON)';
COMMENT ON COLUMN reseller_branding.process_section IS 'Sección de proceso (objeto JSON)';
COMMENT ON COLUMN reseller_branding.testimonials_section IS 'Sección de testimonios (objeto JSON)';
COMMENT ON COLUMN reseller_branding.client_logos_section IS 'Sección de logos de clientes (objeto JSON)';
COMMENT ON COLUMN reseller_branding.contact_email IS 'Email de contacto';
COMMENT ON COLUMN reseller_branding.contact_phone IS 'Teléfono de contacto';
COMMENT ON COLUMN reseller_branding.footer_text IS 'Texto del footer';
