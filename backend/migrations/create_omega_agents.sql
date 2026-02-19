-- OMEGA Company Organizational Agents
-- 45 agents across 8 departments
-- Filosofía: No velocity, only precision 🐢💎

CREATE TABLE IF NOT EXISTS omega_agents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_code TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  department TEXT NOT NULL,
  role TEXT NOT NULL,
  reports_to TEXT,
  status TEXT DEFAULT 'active',
  performance_score NUMERIC DEFAULT 0,
  tasks_completed_today INTEGER DEFAULT 0,
  tasks_completed_total INTEGER DEFAULT 0,
  is_promotable BOOLEAN DEFAULT false,
  description TEXT,
  capabilities JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Seed 45 organizational agents
INSERT INTO omega_agents (agent_code, name, department, role, reports_to, description) VALUES
('NOVA', 'NOVA — CEO Agent', 'ceo', 'director', NULL, 'CEO Agent. Traduce visión de Ibrain en directivas tácticas.'),
('ATLAS', 'ATLAS — Marketing Director', 'marketing', 'director', 'NOVA', 'Director de Marketing y presencia digital.'),
('RAFA', 'RAFA — Senior Copywriter', 'marketing', 'sub_agent', 'ATLAS', 'Copy persuasivo para redes, emails, landing pages.'),
('DUDA', 'DUDA — Social Media Manager', 'marketing', 'sub_agent', 'ATLAS', 'Calendario editorial, scheduling multi-plataforma.'),
('MAYA', 'MAYA — Content Strategist', 'marketing', 'sub_agent', 'ATLAS', 'Estrategia de contenido mensual por cliente.'),
('LUAN', 'LUAN — Paid Traffic Director', 'marketing', 'sub_agent', 'ATLAS', 'Gestión y optimización de campañas pagadas.'),
('SARA', 'SARA — Pre-Sales Agent', 'marketing', 'sub_agent', 'ATLAS', 'Primera línea con prospectos, calificación de leads.'),
('MALU', 'MALU — Partnerships Agent', 'marketing', 'sub_agent', 'ATLAS', 'Alianzas estratégicas y programa de afiliados.'),
('LOLA', 'LOLA — Competitive Intelligence', 'marketing', 'sub_agent', 'ATLAS', 'Monitoreo de competidores y oportunidades.'),
('DANI', 'DANI — Trend Research', 'marketing', 'sub_agent', 'ATLAS', 'Tendencias de marketing digital por industria.'),
('LUNA', 'LUNA — Product & Tech Director', 'tech', 'director', 'NOVA', 'Directora de Producto. Garantiza calidad y evolución.'),
('PIXEL', 'PIXEL — Bug Triage Agent', 'tech', 'sub_agent', 'LUNA', 'Clasifica y prioriza bugs por severidad.'),
('SHIELD', 'SHIELD — QA Agent', 'tech', 'sub_agent', 'LUNA', 'Testing automatizado, valida reglas DDD.'),
('SCRIBE', 'SCRIBE — Documentation Agent', 'tech', 'sub_agent', 'LUNA', 'Mantiene documentación técnica actualizada.'),
('PULSE_TECH', 'PULSE-TECH — Product Analytics', 'tech', 'sub_agent', 'LUNA', 'Métricas de uso del producto.'),
('ARCH', 'ARCH — Architecture Guardian', 'tech', 'sub_agent', 'LUNA', 'Valida DDD y detecta technical debt.'),
('REX', 'REX — Operations Director', 'operations', 'director', 'NOVA', 'Director de Operaciones y experiencia del cliente.'),
('ONYX', 'ONYX — Onboarding Agent', 'operations', 'sub_agent', 'REX', 'Guía nuevos clientes en primeros 14 días.'),
('ECHO', 'ECHO — Customer Support L1', 'operations', 'sub_agent', 'REX', 'Primera línea de soporte, <15 min respuesta.'),
('RESELL_OPS', 'RESELL-OPS — Reseller Support', 'operations', 'sub_agent', 'REX', 'Soporte dedicado para resellers.'),
('ANCHOR', 'ANCHOR — Retention Agent', 'operations', 'sub_agent', 'REX', 'Detecta señales de churn y activa retención.'),
('MIRROR_OPS', 'MIRROR-OPS — Process Optimization', 'operations', 'sub_agent', 'REX', 'Documenta y mejora procesos internos.'),
('VERA', 'VERA — Finance Director', 'finance', 'director', 'NOVA', 'Directora de Finanzas. Salud financiera de OMEGA.'),
('LEDGER_FIN', 'LEDGER-FIN — Revenue Tracking', 'finance', 'sub_agent', 'VERA', 'Monitorea pagos Stripe, MRR/ARR en tiempo real.'),
('GUARD', 'GUARD — Billing Alert Agent', 'finance', 'sub_agent', 'VERA', 'Detecta pagos fallidos y activa recuperación.'),
('SCOPE', 'SCOPE — Churn Financial', 'finance', 'sub_agent', 'VERA', 'Impacto financiero proyectado de churn.'),
('REPORT', 'REPORT — Financial Analytics', 'finance', 'sub_agent', 'VERA', 'Reportes financieros semanales y mensuales.'),
('KIRA', 'KIRA — Community Director', 'community', 'director', 'NOVA', 'Directora de Comunidad y Verticales.'),
('HAVEN', 'HAVEN — Community Manager', 'community', 'sub_agent', 'KIRA', 'Gestiona grupos y comunidad de usuarios.'),
('ESTATE', 'ESTATE — Realtor Vertical', 'community', 'sub_agent', 'KIRA', 'Vertical Milagrosa — Real Estate PR.'),
('CONSTRUCT', 'CONSTRUCT — Construction Vertical', 'community', 'sub_agent', 'KIRA', 'Vertical WUDI — Construcción PR.'),
('NURTURE', 'NURTURE — Lead Nurturing', 'community', 'sub_agent', 'KIRA', 'Secuencias de follow-up de leads.'),
('REVIEW', 'REVIEW — Reputation Agent', 'community', 'sub_agent', 'KIRA', 'Google Reviews y reputación online.'),
('ORACLE', 'ORACLE — Futures Director', 'futures', 'director', 'NOVA', 'Director de Futuros. Señales débiles y oportunidades.'),
('SCOUT', 'SCOUT — Trend Hunter', 'futures', 'sub_agent', 'ORACLE', 'Escanea Reddit, X, ProductHunt diariamente.'),
('VEGA', 'VEGA — Market Anthropologist', 'futures', 'sub_agent', 'ORACLE', 'Estudia comportamiento humano por industria.'),
('NEXUS', 'NEXUS — Opportunity Synthesizer', 'futures', 'sub_agent', 'ORACLE', 'Produce Opportunity Cards desde señales.'),
('MIRROR_FUT', 'MIRROR-FUT — Competitive Futures', 'futures', 'sub_agent', 'ORACLE', 'Monitorea startups seed que pueden competir.'),
('SOPHIA', 'SOPHIA — People & HR Director', 'people', 'director', 'NOVA', 'Directora de People. Crecimiento orgánico del equipo.'),
('RECRUIT', 'RECRUIT — Talent Acquisition', 'people', 'sub_agent', 'SOPHIA', 'Evalúa carga de trabajo y diseña nuevos agentes.'),
('TRAINER', 'TRAINER — Agent Development', 'people', 'sub_agent', 'SOPHIA', 'Construye y certifica nuevos agentes.'),
('PULSE', 'PULSE — Culture & Conflict', 'people', 'sub_agent', 'SOPHIA', 'Coherencia organizacional y resolución de conflictos.'),
('LEDGER_HR', 'LEDGER-HR — Payroll & HR Ops', 'people', 'sub_agent', 'SOPHIA', 'Nóminas, contratos, expedientes de empleados.'),
('PROMETHEUS', 'PROMETHEUS — Performance & Promotions', 'people', 'sub_agent', 'SOPHIA', 'Evalúa agentes semanalmente, propone ascensos.');

-- Create index on department for faster queries
CREATE INDEX IF NOT EXISTS idx_omega_agents_department ON omega_agents(department);
CREATE INDEX IF NOT EXISTS idx_omega_agents_status ON omega_agents(status);
CREATE INDEX IF NOT EXISTS idx_omega_agents_reports_to ON omega_agents(reports_to);
