-- ═══════════════════════════════════════════════════════════════
-- FASE 2: MULTI-TENANT INFRASTRUCTURE
-- Tablas para sistema de resellers white-label
-- ═══════════════════════════════════════════════════════════════

-- TABLA: resellers
-- Agencias que revenden OMEGA con white-label
CREATE TABLE IF NOT EXISTS resellers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug VARCHAR(100) UNIQUE NOT NULL,        -- "agenciajuan"
  agency_name VARCHAR(255) NOT NULL,
  owner_email VARCHAR(255) NOT NULL UNIQUE,
  owner_name VARCHAR(255) NOT NULL,
  stripe_account_id VARCHAR(255),           -- Su propio Stripe Connect
  stripe_customer_id VARCHAR(255),          -- Para cobrarles a ellos
  white_label_active BOOLEAN DEFAULT false,
  status VARCHAR(50) DEFAULT 'active',      -- active/warning/suspended/terminated
  omega_commission_rate DECIMAL(5,2) DEFAULT 0.30,
  monthly_revenue_reported DECIMAL(12,2) DEFAULT 0,
  payment_due_date DATE,
  days_overdue INT DEFAULT 0,
  suspend_switch BOOLEAN DEFAULT false,
  clients_migrated BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- TABLA: reseller_branding
-- Configuración white-label de cada reseller
CREATE TABLE IF NOT EXISTS reseller_branding (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reseller_id UUID REFERENCES resellers(id) ON DELETE CASCADE,
  logo_url VARCHAR(500),
  hero_media_url VARCHAR(500),              -- video o foto del hero (max 15MB)
  hero_media_type VARCHAR(20),              -- 'video' | 'image'
  primary_color VARCHAR(50) DEFAULT '38 85% 55%',
  secondary_color VARCHAR(50) DEFAULT '225 12% 14%',
  agency_tagline VARCHAR(255),
  badge_text VARCHAR(100) DEFAULT 'Boutique Creative Agency',
  hero_cta_text VARCHAR(50) DEFAULT 'Comenzar',
  pain_items JSONB DEFAULT '[]',
  solution_items JSONB DEFAULT '[]',
  services JSONB DEFAULT '[]',
  metrics JSONB DEFAULT '[]',
  process_steps JSONB DEFAULT '[]',
  testimonials JSONB DEFAULT '[]',
  footer_email VARCHAR(255),
  footer_phone VARCHAR(50),
  social_links JSONB DEFAULT '[]',
  legal_pages JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(reseller_id)
);

-- TABLA: reseller_agents
-- Agentes humanos del reseller (para tareas manuales)
CREATE TABLE IF NOT EXISTS reseller_agents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reseller_id UUID REFERENCES resellers(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  hourly_rate DECIMAL(10,2),
  status VARCHAR(50) DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════
-- MODIFICAR: tabla clients
-- Preparar para FASE 2 (Resellers) + Compatibilidad MultiOMEGA B2C
-- ═══════════════════════════════════════════════════════════════
DO $$
BEGIN
  -- FASE 2: Reseller fields
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='clients' AND column_name='reseller_id'
  ) THEN
    ALTER TABLE clients ADD COLUMN reseller_id UUID REFERENCES resellers(id) NULL;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='clients' AND column_name='white_label_plan'
  ) THEN
    ALTER TABLE clients ADD COLUMN white_label_plan VARCHAR(50) NULL;
  END IF;

  -- MultiOMEGA B2C: Budget & Plan fields
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='clients' AND column_name='monthly_budget_total'
  ) THEN
    ALTER TABLE clients ADD COLUMN monthly_budget_total DECIMAL(12,2) DEFAULT 0;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='clients' AND column_name='budget_operative_60'
  ) THEN
    ALTER TABLE clients ADD COLUMN budget_operative_60 DECIMAL(12,2) DEFAULT 0;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='clients' AND column_name='budget_reserve_40'
  ) THEN
    ALTER TABLE clients ADD COLUMN budget_reserve_40 DECIMAL(12,2) DEFAULT 0;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='clients' AND column_name='plan'
  ) THEN
    ALTER TABLE clients ADD COLUMN plan VARCHAR(50) DEFAULT 'basic';
  END IF;

  -- MultiOMEGA B2C: Human supervision
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='clients' AND column_name='human_supervision'
  ) THEN
    ALTER TABLE clients ADD COLUMN human_supervision BOOLEAN DEFAULT false;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='clients' AND column_name='human_hours_package'
  ) THEN
    ALTER TABLE clients ADD COLUMN human_hours_package VARCHAR(50) DEFAULT 'none';
  END IF;

  -- MultiOMEGA B2C: Stripe & Status
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='clients' AND column_name='stripe_customer_id'
  ) THEN
    ALTER TABLE clients ADD COLUMN stripe_customer_id VARCHAR(255);
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='clients' AND column_name='status'
  ) THEN
    ALTER TABLE clients ADD COLUMN status VARCHAR(50) DEFAULT 'active';
  END IF;

  -- MultiOMEGA B2C: Trial system
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='clients' AND column_name='trial_active'
  ) THEN
    ALTER TABLE clients ADD COLUMN trial_active BOOLEAN DEFAULT false;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='clients' AND column_name='trial_ends_at'
  ) THEN
    ALTER TABLE clients ADD COLUMN trial_ends_at TIMESTAMPTZ;
  END IF;
END $$;

-- MODIFICAR: tabla leads (agregar reseller_id)
-- Añadir columna reseller_id a leads existentes
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='leads' AND column_name='reseller_id'
  ) THEN
    ALTER TABLE leads ADD COLUMN reseller_id UUID REFERENCES resellers(id) NULL;
  END IF;
END $$;

-- ÍNDICES para optimizar queries
CREATE INDEX IF NOT EXISTS idx_resellers_slug ON resellers(slug);
CREATE INDEX IF NOT EXISTS idx_resellers_status ON resellers(status);
CREATE INDEX IF NOT EXISTS idx_clients_reseller_id ON clients(reseller_id);
CREATE INDEX IF NOT EXISTS idx_clients_status ON clients(status);
CREATE INDEX IF NOT EXISTS idx_clients_plan ON clients(plan);
CREATE INDEX IF NOT EXISTS idx_clients_trial_active ON clients(trial_active);
CREATE INDEX IF NOT EXISTS idx_leads_reseller_id ON leads(reseller_id);
CREATE INDEX IF NOT EXISTS idx_reseller_agents_reseller_id ON reseller_agents(reseller_id);

-- FUNCIÓN: Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ language 'plpgsql';

-- TRIGGERS para updated_at
DROP TRIGGER IF EXISTS update_resellers_updated_at ON resellers;
CREATE TRIGGER update_resellers_updated_at
  BEFORE UPDATE ON resellers
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_reseller_branding_updated_at ON reseller_branding;
CREATE TRIGGER update_reseller_branding_updated_at
  BEFORE UPDATE ON reseller_branding
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_reseller_agents_updated_at ON reseller_agents;
CREATE TRIGGER update_reseller_agents_updated_at
  BEFORE UPDATE ON reseller_agents
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- COMENTARIOS para documentación
COMMENT ON TABLE resellers IS 'Agencias que revenden OMEGA con white-label';
COMMENT ON TABLE reseller_branding IS 'Configuración de marca white-label por reseller';
COMMENT ON TABLE reseller_agents IS 'Agentes humanos del reseller para tareas manuales';

-- Resellers columns
COMMENT ON COLUMN resellers.omega_commission_rate IS 'Comisión que OMEGA cobra (default 30%)';
COMMENT ON COLUMN resellers.suspend_switch IS 'Switch manual de OMEGA para suspender reseller';
COMMENT ON COLUMN reseller_branding.hero_media_url IS 'URL del media del hero (video o imagen, max 15MB)';

-- Clients columns - MultiOMEGA B2C compatibility
COMMENT ON COLUMN clients.reseller_id IS 'NULL = cliente directo de OMEGA | UUID = cliente del reseller';
COMMENT ON COLUMN clients.monthly_budget_total IS 'Presupuesto total que paga el cliente (antes de split 60/40)';
COMMENT ON COLUMN clients.budget_operative_60 IS '60% del presupuesto - visible para agente humano como "100%"';
COMMENT ON COLUMN clients.budget_reserve_40 IS '40% reserva OMEGA - solo visible en Reserve Dashboard con PIN';
COMMENT ON COLUMN clients.plan IS 'Plan del cliente: basic/pro/enterprise (solo para clientes directos de OMEGA)';
COMMENT ON COLUMN clients.human_supervision IS 'Si el cliente tiene supervisión de agente humano activa';
COMMENT ON COLUMN clients.human_hours_package IS 'Paquete de horas contratado: none/10h/20h/40h/custom';
COMMENT ON COLUMN clients.status IS 'Estado del cliente: active/suspended/churned/trial';
COMMENT ON COLUMN clients.trial_active IS 'Si el cliente está en periodo de prueba (7 días)';
COMMENT ON COLUMN clients.trial_ends_at IS 'Fecha y hora de finalización del trial';
