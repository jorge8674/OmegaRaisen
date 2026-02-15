# OMEGA — PROMPT DE CONTEXTO COMPLETO v2
*Actualizado Febrero 2026 — Usar al inicio de cada nueva conversación*

---

## QUIÉN SOY
Soy Ibrain, CTO y fundador de OMEGA (Raisen Omega).
Raisen es una agencia boutique de marketing digital que opera con clientes reales,
community managers e influencers. Usábamos AI de terceros para producción de contenido.
OMEGA surge de consolidar todo eso en una sola plataforma propia y abrirla al mercado.
Filosofía: "No velocity, only precision." 8 años de experiencia empresarial.

---

## QUÉ ES OMEGA
Plataforma SaaS de marketing digital con AI para agencias y negocios.
- **URL producción:** https://r-omega.agency
- **Marca:** RAISEN. OMEGA
- **Stack:** Next.js/React (Lovable) + FastAPI (Railway) + Supabase
- **GitHub:** https://github.com/Software2026/OMEGA.git

---

## INFRAESTRUCTURA

### Frontend — Lovable
- URL: r-omega.agency
- Supabase Lovable: kbuwykooisxwkjazbadw.supabase.co
- ANON KEY Lovable: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtidXd5a29vaXN4d2tqYXpiYWR3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA5MzU0MDgsImV4cCI6MjA4NjUxMTQwOH0.EmfwGJrY9v0Nt86BEaw_eiJYzf_U9W0jeE5wu4hMy1c
- ⚠️ NO se puede cambiar el Supabase de Lovable ni acceder al service_role key
- ⚠️ Lovable NO accede a Supabase directamente para resellers → todo vía Railway API

### Backend — Railway (FastAPI)
- URL: https://omegaraisen-production.up.railway.app
- 95+ endpoints operacionales
- GitHub: push a main = redeploy automático
- Variables Railway configuradas:
  - SUPABASE_URL = https://jsxuhutiduxjjuqtyoml.supabase.co
  - SUPABASE_ANON_KEY = sb_publishable_SDPoCgHvC-NzMkBTGkc-TA_X2lq3yVJ
  - SUPABASE_SERVICE_ROLE_KEY = [configurado]

### Supabase Propio (Railway apunta aquí)
- URL: https://jsxuhutiduxjjuqtyoml.supabase.co
- Tablas activas: resellers, reseller_branding, reseller_agents
- Tablas pendientes: clients (con nuevos campos), leads con reseller_id
- Storage bucket: reseller-media (público, max 15MB)

---

## SISTEMA DE DISEÑO

```
Dark mode único. Sin light mode.
--background:  225 15% 5%   (#0D0E12)
--primary:     38 85% 55%   (Oro/Ámbar)
--secondary:   225 12% 14%
--card:        225 15% 8%
--border:      225 12% 16%
font-display: Syne | font-body: DM Sans
Cursor personalizado global (oro)
```

---

## ESTADO ACTUAL DEL PROYECTO

### Fase 1 — COMPLETADA ✅
| Página | Status |
|--------|--------|
| /dashboard | ✅ |
| /contenido | ✅ |
| /calendario | ✅ |
| /analytics | ✅ |
| /competitive | ✅ |
| /crisis-room | ✅ |
| /growth | ✅ |

### Fase 2 — EN PROGRESO 🔄
| Item | Status |
|------|--------|
| Tablas DB resellers | ✅ Migradas |
| 11 endpoints Railway resellers | ✅ Activos |
| /admin/resellers | ✅ Funcional |
| /reseller/dashboard | ✅ Funcional |
| /reseller/branding editor | ⏳ PENDIENTE |
| /landing/:slug pública | ⏳ PENDIENTE |
| Stripe + billing | ⏳ PENDIENTE URGENTE |
| Auth por roles | ⏳ PENDIENTE URGENTE |
| Instagram Publishing API | ⏳ Iniciar proceso aprobación |

---

## MODELO DE NEGOCIO

```
JERARQUÍA:
OMEGA Super-Admin (Ibrain) → ve TODO
  └── Reseller (Enterprise + White-Label $299/mes add-on)
        ├── Subdomain: {slug}.r-omega.agency
        ├── 100% white-label (OMEGA invisible)
        ├── Su propio Stripe para cobrar clientes
        ├── OMEGA cobra 30% de su revenue mensual
        └── 90 días sin pago → OMEGA hereda sus clientes

PLANES:
  Básico:     $97/mes  → 1 cuenta, 2 bloques/día
  Pro:        $197/mes → 5 cuentas, 6 bloques/día
  Enterprise: $497/mes → ilimitado, publicación automática
  Trial:      7 días   → acceso Pro, tarjeta requerida

ADD-ONS:
  Video Pack Starter (5):   $49/mes
  Video Pack Creator (15):  $129/mes
  Video Pack Agency (50):   $379/mes
  Video Pack Unlimited:     $799/mes
  Meta Ads Management:      $99/mes por ad account
```

---

## AGENTES AI DEL SISTEMA

```
ACTIVOS (15): Content, ImagePrompt, Hashtag, Analytics, Competitive,
              TrendDetector, CrisisDetector, CrisisResponse, GrowthStrategy,
              BrandVoice, ABTesting, ReportGenerator, ScriptWriter,
              Orchestrator, Monitor

PLANIFICADOS FASE 3 (22 nuevos):
  Video: Kling, Veo3, Runway, Pika, Sora, VideoCaptions
  Optimización: PromptOptimizer, PromptRepository, ContentAdaptor, FormatOptimizer
  Contexto: ClientContext, WebScraper, SocialAnalyzer, CompetitorWatch
  Publicación: Instagram, TikTok, Facebook, LinkedIn, Twitter, Scheduler
  Analytics: PostPerformance, EngagementTracker, ROICalculator, ViralPredictor

TOTAL OBJETIVO: 37 agentes / 150+ endpoints
```

---

## SISTEMAS DISEÑADOS (documentados, listos para activar)

### NEXUS — Super Agente de Inteligencia Colectiva
- Absorbe TODA la data de todos los clientes
- Detecta patrones, los valida, los distribuye a todos los agentes
- Multiplication Score: 5x→10x→500x con el volumen de clientes
- Dashboard exclusivo: /superadmin/nexus
- Activar cuando: 100+ clientes

### GUARDIAN — Ejército de Seguridad Autónomo
- 7 escuadrones: SENTINEL, INSPECTOR, MEDIC, COMPLIANCE, PERFORMANCE, PROPHET, CHRONICLER
- Monitoreo 24/7, auto-reparación, reportes diarios a Ibrain
- Reporte diario 7am con estado del sistema
- Activar: GUARDIAN-0 antes del primer cliente real

### META API — Integración Facebook/Instagram
- Sub-Fase A: Infraestructura lista (hacer ahora, gratis)
- Sub-Fase B: Publicación orgánica automática (con 10+ clientes)
- Sub-Fase C: Analytics con datos reales → NEXUS
- Sub-Fase D: Anuncios pagados gestionados por OMEGA
- Activar cuando: 10+ clientes pagando

### MULTI-CUENTA + SELECTOR DE CONTEXTO
- Selector cascada: Cliente → Cuenta → Nicho/Perfil
- Contexto persistente por cuenta y nicho
- AI aprende de cada cuenta con el tiempo
- Límites por plan (1/5/ilimitado cuentas)

---

## ENDPOINTS ACTIVOS

```
BASE: https://omegaraisen-production.up.railway.app

RESELLERS:
POST   /api/v1/resellers/create
GET    /api/v1/resellers/all
GET    /api/v1/resellers/{id}/dashboard
PATCH  /api/v1/resellers/{id}/status
POST   /api/v1/resellers/{id}/branding
GET    /api/v1/resellers/{id}/branding
GET    /api/v1/resellers/{id}/clients
POST   /api/v1/resellers/{id}/clients/add
GET    /api/v1/resellers/slug/{slug}
POST   /api/v1/resellers/{id}/upload-hero-media

AI AGENTS (84 endpoints):
/api/v1/content/*, /api/v1/analytics/*, /api/v1/competitive/*
/api/v1/trends/*, /api/v1/growth/*, /api/v1/brand-voice/*
/api/v1/ab-testing/*, /api/v1/crisis/*, /api/v1/orchestrator/*
/api/v1/reports/*
```

---

## DOCUMENTOS DEL PROYECTO

```
OMEGA_MASTER_ARCHITECTURE.md  → Arquitectura completa
OMEGA_CONTEXT_PROMPT.md       → Este documento
OMEGA_PRECEDENTS.md           → Memoria institucional + decisiones
Master_contenido.md           → Sistema de contenido ultra avanzado (11 módulos)
OMEGA_SUPER_AGENT.md          → NEXUS: inteligencia colectiva
OMEGA_GUARDIAN.md             → Ejército de seguridad autónomo
OMEGA_META_API.md             → Meta API: 4 sub-fases preparadas
```

---

## REGLAS DE DESARROLLO

```
1. Page-by-page: no avanzar hasta 100% funcional
2. Button-by-button: cada botón probado
3. Consola primero (backend) → Lovable conecta (frontend)
4. Payloads deben matchear EXACTAMENTE los modelos Pydantic
5. Error 422 → pedir schema exacto al Agente Consola
6. Lovable NO accede Supabase directamente para resellers
7. Archivos máximo 200 líneas
8. Commit descriptivo después de cada cambio funcional
9. Push a main = redeploy automático Railway
```

---

## PRÓXIMOS PASOS — EN ORDEN

```
PRIORIDAD 1 (HOY):
  □ /reseller/branding — Editor visual 5 tabs
  □ /landing/:slug — Landing pública white-label

PRIORIDAD 2 (ESTA SEMANA):
  □ Stripe + billing → poder cobrar
  □ Auth por roles → poder dar acceso real

PRIORIDAD 3 (PRÓXIMAS 2 SEMANAS):
  □ Primer reseller de prueba end-to-end
  □ Primer cliente pagando

PRIORIDAD 4 (MES 1-2):
  □ GUARDIAN-0: auth_guardian + rate_limiter + health_monitor
  □ Meta Developer App creada (Sub-Fase META-A)
  □ Contexto de cliente (client_context en DB)
  □ Selector de cuenta en /contenido
```

