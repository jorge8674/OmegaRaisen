# 🤖 PROMPTS AGENTES 12, 13, 14, 15 — RECTA FINAL
## Video Production + Scheduling + A/B Testing + Orchestrator

---

# ══════════════════════════════════════
# AGENTE 12: VIDEO PRODUCTION AGENT
# ══════════════════════════════════════

Implementa el **Video Production Agent (Agente 12/15)**.

## ARCHIVO 1: `backend/app/services/video_pipeline.py`

```python
class VideoScene(BaseModel):
    scene_number: int
    duration_seconds: int
    narration: str
    visual_description: str
    text_overlay: str | None
    transition: str          # "cut" | "fade" | "slide"

class VideoScript(BaseModel):
    hook: str                # Primeros 3 segundos — crítico para retención
    scenes: list[VideoScene]
    call_to_action: str
    total_duration_seconds: int
    word_count: int

class VideoSpec(BaseModel):
    title: str
    duration_seconds: int    # 15 | 30 | 60 | 90 | 120
    platform: str            # "tiktok" | "instagram_reels" | "youtube_shorts" | "facebook_reels"
    aspect_ratio: str        # "9:16" | "1:1" | "16:9"
    style: str               # "educational" | "entertainment" | "promotional" | "behind_scenes" | "tutorial"
    visual_style: str        # "minimal" | "dynamic" | "luxury" | "raw" | "corporate"
    target_audience: str

class VideoProductionPlan(BaseModel):
    spec: VideoSpec
    script: VideoScript
    shot_list: list[str]
    text_overlays: list[dict[str, str]]
    audio_suggestions: list[str]
    estimated_production_hours: float
    production_tips: list[str]
```

Funciones puras:
- `calculate_scene_count(total_seconds: int, avg_scene_duration: int = 5) -> int`
- `validate_duration_for_platform(platform: str, duration: int) -> bool`
- `get_optimal_aspect_ratio(platform: str) -> str`
- `estimate_word_count(duration_seconds: int) -> int`

## ARCHIVO 2: `backend/app/agents/video_production_agent.py`

Usa **GPT-4** para scripting y **Claude Opus 4** para hooks y CTAs.

```python
async def write_video_script(
    self,
    spec: VideoSpec,
    brand_voice: str,
    key_message: str
) -> VideoScript:
    """Escribe script completo con hook poderoso y CTA claro"""

async def create_production_plan(
    self,
    spec: VideoSpec,
    script: VideoScript
) -> VideoProductionPlan:
    """Plan de producción detallado con shot list"""

async def optimize_hook(
    self,
    platform: str,
    niche: str,
    content_topic: str
) -> str:
    """Genera 3 opciones de hooks para los primeros 3 segundos"""

async def adapt_script_for_platform(
    self,
    script: VideoScript,
    target_platform: str
) -> VideoScript:
    """Adapta script existente a otro formato de plataforma"""

async def generate_video_ideas(
    self,
    niche: str,
    platform: str,
    content_pillars: list[str]
) -> list[dict[str, str]]:
    """Genera 5 ideas de video con title, hook y concepto"""
```

## ARCHIVO 3: `backend/app/api/routes/video_production.py`

```
POST /api/v1/video/write-script
POST /api/v1/video/production-plan
POST /api/v1/video/optimize-hook
POST /api/v1/video/adapt-platform
POST /api/v1/video/generate-ideas
GET  /api/v1/video/agent-status
```

## Registrar en main.py:
```python
from app.api.routes import video_production
app.include_router(video_production.router, prefix="/api/v1/video", tags=["Video Production"])
```

---

# ══════════════════════════════════════
# AGENTE 13: SCHEDULING & QUEUE AGENT
# ══════════════════════════════════════

Implementa el **Scheduling & Queue Agent (Agente 13/15)**.
Gestión completa de calendario y aprobación de contenido.

## ARCHIVO 1: `backend/app/services/queue_manager.py`

```python
class ScheduledPost(BaseModel):
    post_id: str
    client_id: str
    platform: str
    content_type: str        # "image" | "video" | "carousel" | "story" | "reel"
    caption: str
    hashtags: list[str]
    media_urls: list[str]
    scheduled_time: str      # ISO datetime
    timezone: str            # "America/New_York" | "America/Puerto_Rico" etc.
    status: str              # "draft" | "pending_approval" | "approved" | "scheduled" | "published" | "failed"
    priority: str            # "low" | "normal" | "high" | "urgent"
    created_by: str          # "ai_generated" | "human_created"
    approved_by: str | None
    approved_at: str | None
    notes: str | None

class PublicationQueue(BaseModel):
    client_id: str
    total_posts: int
    pending_approval: int
    scheduled_count: int
    published_today: int
    posts: list[ScheduledPost]
    next_publication: ScheduledPost | None

class OptimalTimingResult(BaseModel):
    platform: str
    recommended_slots: list[str]     # Lista de ISO datetimes
    reasoning: str
    expected_engagement_boost: float  # Multiplicador vs posting en mal momento
    audience_timezone: str
```

Funciones puras:
- `generate_post_id() -> str`
- `validate_scheduled_time(scheduled_time: str, platform: str) -> bool`
- `sort_queue_by_priority(posts: list[ScheduledPost]) -> list[ScheduledPost]`
- `calculate_optimal_frequency(platform: str, account_size: str) -> dict[str, int]`

## ARCHIVO 2: `backend/app/agents/scheduling_agent.py`

```python
async def schedule_post(
    self,
    post_data: dict[str, str | list],
    client_preferences: dict[str, str]
) -> ScheduledPost:
    """Crea y agenda un post con timing óptimo"""

async def get_queue(
    self,
    client_id: str,
    status_filter: str | None,
    platform_filter: str | None
) -> PublicationQueue:
    """Retorna cola de publicación con filtros"""

async def approve_post(
    self,
    post_id: str,
    reviewer_id: str,
    approval_notes: str = ""
) -> ScheduledPost:
    """Aprueba post para publicación — flujo humano en el loop"""

async def calculate_optimal_times(
    self,
    platform: str,
    audience_timezone: str,
    content_type: str
) -> OptimalTimingResult:
    """Calcula mejores horarios basado en plataforma y audiencia"""

async def bulk_schedule(
    self,
    posts: list[dict[str, str | list]],
    client_id: str,
    spread_days: int = 7
) -> list[ScheduledPost]:
    """Agenda múltiples posts distribuyendo en el tiempo"""
```

## ARCHIVO 3: `backend/app/api/routes/scheduling.py`

```
POST /api/v1/scheduling/schedule-post
GET  /api/v1/scheduling/queue/{client_id}
POST /api/v1/scheduling/approve-post
POST /api/v1/scheduling/optimal-times
POST /api/v1/scheduling/bulk-schedule
GET  /api/v1/scheduling/agent-status
```

## Registrar en main.py:
```python
from app.api.routes import scheduling
app.include_router(scheduling.router, prefix="/api/v1/scheduling", tags=["Scheduling"])
```

---

# ══════════════════════════════════════
# AGENTE 14: A/B TESTING AGENT
# ══════════════════════════════════════

Implementa el **A/B Testing Agent (Agente 14/15)**.
Evidencia científica para justificar estrategias ante clientes.

## ARCHIVO 1: `backend/app/services/experiment_engine.py`

```python
class ABVariant(BaseModel):
    variant_id: str
    variant_name: str        # "A" | "B" | "C"
    description: str
    content: dict[str, str]  # El contenido a testear
    impressions: int
    engagements: int
    clicks: int
    conversions: int
    engagement_rate: float

class ABTestResult(BaseModel):
    test_id: str
    winner_variant: str | None
    statistical_significance: float  # 0.0 a 1.0
    confidence_level: float          # 0.90 | 0.95 | 0.99
    is_conclusive: bool
    sample_size_per_variant: int
    minimum_sample_needed: int
    recommendation: str
    insights: list[str]

class Experiment(BaseModel):
    experiment_id: str
    client_id: str
    hypothesis: str
    variable_tested: str     # "caption" | "image" | "posting_time" | "hashtags" | "cta" | "hook"
    variants: list[ABVariant]
    status: str              # "draft" | "running" | "completed" | "inconclusive"
    started_at: str
    completed_at: str | None
    target_sample_size: int
    platform: str
```

Funciones puras:
- `calculate_engagement_rate(engagements: int, impressions: int) -> float`
- `calculate_statistical_significance(control: ABVariant, test: ABVariant) -> float`
- `determine_minimum_sample_size(effect_size: float, confidence: float) -> int`
- `is_result_conclusive(significance: float, sample_size: int, minimum: int) -> bool`

## ARCHIVO 2: `backend/app/agents/ab_testing_agent.py`

Usa **GPT-4**.

```python
async def design_experiment(
    self,
    hypothesis: str,
    variable: str,
    base_content: dict[str, str],
    platform: str
) -> Experiment:
    """Diseña experimento científico con variantes claras"""

async def create_variants(
    self,
    base_content: dict[str, str],
    variable: str,
    client_niche: str
) -> list[ABVariant]:
    """Crea variantes A y B del contenido a testear"""

async def analyze_results(
    self,
    experiment: Experiment
) -> ABTestResult:
    """Analiza resultados con significancia estadística"""

async def generate_insights(
    self,
    results: list[ABTestResult],
    client_id: str
) -> list[str]:
    """Genera insights acumulados de múltiples experimentos"""

async def recommend_next_test(
    self,
    completed_experiments: list[Experiment],
    client_goals: list[str]
) -> dict[str, str]:
    """Recomienda próximo experimento basado en historial"""
```

## ARCHIVO 3: `backend/app/api/routes/ab_testing.py`

```
POST /api/v1/ab-testing/design-experiment
POST /api/v1/ab-testing/create-variants
POST /api/v1/ab-testing/analyze-results
POST /api/v1/ab-testing/generate-insights
POST /api/v1/ab-testing/recommend-next
GET  /api/v1/ab-testing/agent-status
```

## Registrar en main.py:
```python
from app.api.routes import ab_testing
app.include_router(ab_testing.router, prefix="/api/v1/ab-testing", tags=["A/B Testing"])
```

---

# ══════════════════════════════════════
# AGENTE 15: ORCHESTRATOR AGENT ⭐
# ══════════════════════════════════════

Implementa el **Orchestrator Agent (Agente 15/15)** — el cerebro del sistema.
Este agente coordina los 14 agentes anteriores en workflows automáticos.

## ARCHIVO 1: `backend/app/services/task_router.py`

```python
class AgentTask(BaseModel):
    task_id: str
    workflow_id: str | None
    task_type: str           # "generate_content" | "validate_brand" | "analyze_metrics" | etc.
    assigned_agent: str      # "content_creator" | "brand_voice" | "analytics" | etc.
    priority: str            # "low" | "normal" | "high" | "critical"
    payload: dict[str, str | int | float | list | dict]
    status: str              # "queued" | "processing" | "completed" | "failed"
    created_at: str
    started_at: str | None
    completed_at: str | None
    result: dict[str, str | int | float | list] | None
    error: str | None

class WorkflowStep(BaseModel):
    step_id: str
    agent: str
    action: str
    depends_on: list[str]    # step_ids que deben completarse antes
    parallel_with: list[str] # step_ids que pueden correr simultáneamente

class WorkflowExecution(BaseModel):
    workflow_id: str
    workflow_name: str
    client_id: str
    status: str              # "running" | "completed" | "failed" | "paused"
    steps: list[WorkflowStep]
    completed_steps: list[str]
    current_step: str | None
    started_at: str
    estimated_completion: str | None
    results: dict[str, dict]  # step_id -> result

class OrchestratorState(BaseModel):
    active_workflows: int
    queued_tasks: int
    agents_online: int
    agents_status: dict[str, str]
    system_load: float        # 0.0 a 1.0
    last_health_check: str
```

Funciones puras:
- `generate_task_id() -> str`
- `generate_workflow_id() -> str`
- `get_next_available_step(workflow: WorkflowExecution) -> WorkflowStep | None`
- `calculate_system_load(active_workflows: int, queued_tasks: int) -> float`

## ARCHIVO 2: `backend/app/agents/orchestrator_agent.py`

Workflows predefinidos para la agencia:

```python
WORKFLOWS = {
    "full_content_pipeline": [
        # Brief → Content Creator → Brand Voice → Scheduling
        "generate_content", "validate_brand_voice", "schedule_post"
    ],
    "crisis_response": [
        # Detection → Crisis Manager → Engagement → Monitor
        "assess_crisis", "draft_statement", "respond_comments", "monitor_recovery"
    ],
    "weekly_client_report": [
        # Analytics → Growth → Report Generator
        "analyze_weekly_metrics", "identify_growth_opportunities", "generate_report"
    ],
    "trend_to_content": [
        # Trend Hunter → Strategy → Content Creator → Brand Voice → Scheduling
        "hunt_trends", "create_strategy", "generate_content", "validate_brand", "schedule"
    ],
    "competitive_analysis": [
        # Competitive Intel → Analytics → Strategy → Report
        "analyze_competitors", "benchmark_performance", "update_strategy", "generate_report"
    ]
}
```

Métodos:
```python
async def execute_workflow(
    self,
    workflow_name: str,
    client_id: str,
    params: dict[str, str | int | list]
) -> WorkflowExecution:
    """Ejecuta workflow completo coordinando agentes"""

async def route_task(
    self,
    task_type: str,
    payload: dict[str, str | int | list | dict]
) -> AgentTask:
    """Enruta tarea al agente correcto automáticamente"""

async def get_system_state(self) -> OrchestratorState:
    """Estado completo del sistema en tiempo real"""

async def pause_workflow(
    self,
    workflow_id: str,
    reason: str
) -> WorkflowExecution:
    """Pausa workflow (útil para aprobación humana)"""

async def get_workflow_status(
    self,
    workflow_id: str
) -> WorkflowExecution:
    """Estado actual de un workflow específico"""
```

## ARCHIVO 3: `backend/app/api/routes/orchestrator.py`

```
POST /api/v1/orchestrator/execute-workflow
POST /api/v1/orchestrator/route-task
GET  /api/v1/orchestrator/system-state
GET  /api/v1/orchestrator/workflow/{workflow_id}
POST /api/v1/orchestrator/pause-workflow
GET  /api/v1/orchestrator/agent-status
```

## Registrar en main.py:
```python
from app.api.routes import orchestrator
app.include_router(orchestrator.router, prefix="/api/v1/orchestrator", tags=["Orchestrator"])
```

---

# ══════════════════════════════════════
# main.py FINAL — 15 ROUTERS COMPLETOS
# ══════════════════════════════════════

```python
"""
OmegaRaisen API - Main Application
15 AI Agents | 75+ Endpoints | Agencia Boutique Enterprise
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import (
    content, strategy, analytics, engagement,
    monitor, brand_voice, competitive, trends,
    crisis, reports, growth,
    video_production, scheduling, ab_testing, orchestrator
)

app = FastAPI(
    title="OmegaRaisen API",
    description="Social Media Automation — Agencia Boutique Enterprise",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core Agents
app.include_router(content.router,          prefix="/api/v1/content",       tags=["Content Creator"])
app.include_router(strategy.router,         prefix="/api/v1/strategy",      tags=["Strategy"])
app.include_router(analytics.router,        prefix="/api/v1/analytics",     tags=["Analytics"])
app.include_router(engagement.router,       prefix="/api/v1/engagement",    tags=["Engagement"])
app.include_router(monitor.router,          prefix="/api/v1/monitor",       tags=["Monitor"])

# Intelligence Agents
app.include_router(brand_voice.router,      prefix="/api/v1/brand-voice",   tags=["Brand Voice"])
app.include_router(competitive.router,      prefix="/api/v1/competitive",   tags=["Competitive Intel"])
app.include_router(trends.router,           prefix="/api/v1/trends",        tags=["Trend Hunter"])
app.include_router(crisis.router,           prefix="/api/v1/crisis",        tags=["Crisis Manager"])

# Production Agents
app.include_router(reports.router,          prefix="/api/v1/reports",       tags=["Report Generator"])
app.include_router(growth.router,           prefix="/api/v1/growth",        tags=["Growth Hacker"])
app.include_router(video_production.router, prefix="/api/v1/video",         tags=["Video Production"])
app.include_router(scheduling.router,       prefix="/api/v1/scheduling",    tags=["Scheduling"])
app.include_router(ab_testing.router,       prefix="/api/v1/ab-testing",    tags=["A/B Testing"])

# Master Orchestrator
app.include_router(orchestrator.router,     prefix="/api/v1/orchestrator",  tags=["Orchestrator ⭐"])

@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "OmegaRaisen API",
        "version": "2.0.0",
        "status": "running",
        "agents": "15/15",
        "docs": "/docs"
    }

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "version": "2.0.0", "agents": "15"}
```

---

# PROGRESS.md FINAL:

```markdown
## 🏆 BACKEND COMPLETO: 15/15 AGENTES (100%)

✅ Agente 1:  Content Creator         - 5 endpoints
✅ Agente 2:  Strategy                - 5 endpoints
✅ Agente 3:  Analytics               - 6 endpoints
✅ Agente 4:  Engagement              - 6 endpoints
✅ Agente 5:  Monitor                 - 6 endpoints
✅ Agente 6:  Brand Voice             - 5 endpoints
✅ Agente 7:  Competitive Intel       - 5 endpoints
✅ Agente 8:  Trend Hunter            - 5 endpoints
✅ Agente 9:  Crisis Manager          - 6 endpoints
✅ Agente 10: Report Generator        - 6 endpoints
✅ Agente 11: Growth Hacker           - 5 endpoints
✅ Agente 12: Video Production        - 6 endpoints
✅ Agente 13: Scheduling & Queue      - 6 endpoints
✅ Agente 14: A/B Testing             - 6 endpoints
✅ Agente 15: Orchestrator ⭐         - 6 endpoints

🎯 Endpoints: 84/75+ SUPERADO
🏆 BACKEND 100% COMPLETO

SIGUIENTE FASE: Frontend en Lovable
Conectar los 84 endpoints con UI profesional
```

## REGLAS FINALES:
1. ✅ Max 200 líneas por archivo
2. ✅ CERO `any`
3. ✅ Claude Opus 4 para Crisis Manager
4. ✅ GPT-4 para los demás
5. ✅ main.py final con 15 routers
6. ✅ Commit y push — Backend completado

🐢💎 No velocity, only precision.
🎉 Al completar esto, el backend de OmegaRaisen estará 100% terminado.
```
