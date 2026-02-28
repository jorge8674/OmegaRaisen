-- Add SENTINEL agent to omega_agents
-- Security Director - Sistema inmune de OMEGA Company
-- Filosofía: No velocity, only precision 🐢💎

INSERT INTO omega_agents (
  agent_code,
  name,
  department,
  role,
  reports_to,
  status,
  description,
  performance_score,
  tasks_completed_today,
  tasks_completed_total,
  is_promotable
) VALUES (
  'SENTINEL',
  'SENTINEL — Security Director',
  'security',
  'director',
  'NOVA',
  'active',
  'Director de Seguridad. Sistema inmune de OMEGA. Vigila código, base de datos y endpoints 24/7. Ejecuta scans automáticos: VAULT (secrets), PULSE (health checks), DB_GUARDIAN (integridad).',
  100,
  0,
  0,
  false
)
ON CONFLICT (agent_code) DO UPDATE SET
  name = EXCLUDED.name,
  description = EXCLUDED.description,
  updated_at = now();

-- Add index for security department if not exists
CREATE INDEX IF NOT EXISTS idx_omega_agents_security_dept
ON omega_agents(department)
WHERE department = 'security';
