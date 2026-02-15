# 🤖 PROMPTS AGENTES 9, 10, 11
## Crisis Manager + Report Generator + Growth Hacker

---

# ══════════════════════════════════════
# AGENTE 9: CRISIS MANAGER AGENT
# ══════════════════════════════════════

Implementa el **Crisis Manager Agent (Agente 9/15)**.
Mismo patrón de 3 archivos, todos <200 líneas, cero `any`.

## ARCHIVO 1: `backend/app/services/crisis_detector.py`

```python
class CrisisLevel(BaseModel):
    level: str              # "monitoring" | "alert" | "crisis" | "emergency"
    score: float            # 0.0 a 1.0
    triggers: list[str]

class CrisisSignals(BaseModel):
    negative_comment_percentage: float   # 0.0 a 1.0
    complaint_velocity: float            # complaints per hour
    sentiment_drop: float                # drop desde baseline
    reach_of_negative_content: int
    media_involvement: bool
    influencer_involvement: bool
    platform: str

class CrisisImpactAssessment(BaseModel):
    crisis_level: CrisisLevel
    estimated_reputation_damage: str    # "minimal" | "moderate" | "severe" | "critical"
    affected_platforms: list[str]
    estimated_recovery_time: str        # "days" | "weeks" | "months"
    brand_equity_impact: float          # -1.0 a 0.0
    requires_immediate_action: bool

class RecoveryStep(BaseModel):
    step_number: int
    action: str
    responsible: str                    # "agency" | "client" | "both"
    deadline: str                       # "immediate" | "24h" | "48h" | "1week"
    success_metric: str
```

Funciones puras:
- `calculate_crisis_score(signals: CrisisSignals) -> float`
- `classify_crisis_level(score: float) -> str`
- `estimate_recovery_time(damage: str, crisis_level: str) -> str`
- `requires_immediate_action(level: str) -> bool`

## ARCHIVO 2: `backend/app/agents/crisis_manager_agent.py`

Usa **Claude Opus 4** — mejor razonamiento para situaciones complejas de alto riesgo.

```python
async def assess_crisis(
    self,
    signals: CrisisSignals
) -> CrisisImpactAssessment:
    """Evalúa impacto y nivel de crisis con análisis profundo"""

async def generate_response_strategy(
    self,
    assessment: CrisisImpactAssessment,
    brand_profile: dict[str, str]
) -> dict[str, str | list[str]]:
    """Crea estrategia de respuesta adaptada a la marca"""

async def draft_official_statement(
    self,
    assessment: CrisisImpactAssessment,
    brand_voice: str,
    brand_name: str
) -> str:
    """Redacta comunicado oficial listo para publicar"""

async def create_recovery_plan(
    self,
    assessment: CrisisImpactAssessment
) -> list[RecoveryStep]:
    """Plan de recuperación paso a paso con responsables y plazos"""

async def recommend_immediate_actions(
    self,
    crisis_level: CrisisLevel
) -> list[str]:
    """Acciones a tomar en los próximos 60 minutos"""
```

## ARCHIVO 3: `backend/app/api/routes/crisis.py`

```
POST /api/v1/crisis/assess
POST /api/v1/crisis/response-strategy
POST /api/v1/crisis/draft-statement
POST /api/v1/crisis/recovery-plan
POST /api/v1/crisis/immediate-actions
GET  /api/v1/crisis/agent-status
```

Request bodies:
```python
class AssessCrisisRequest(BaseModel):
    signals: CrisisSignals

class ResponseStrategyRequest(BaseModel):
    assessment: CrisisImpactAssessment
    brand_profile: dict[str, str]

class DraftStatementRequest(BaseModel):
    assessment: CrisisImpactAssessment
    brand_voice: str
    brand_name: str

class RecoveryPlanRequest(BaseModel):
    assessment: CrisisImpactAssessment

class ImmediateActionsRequest(BaseModel):
    crisis_level: CrisisLevel
```

## Registrar en main.py:
```python
from app.api.routes import crisis
app.include_router(crisis.router, prefix="/api/v1/crisis", tags=["Crisis Manager"])
```

---

# ══════════════════════════════════════
# AGENTE 10: REPORT GENERATOR AGENT
# ══════════════════════════════════════

Implementa el **Report Generator Agent (Agente 10/15)**.
Este es el entregable principal de la agencia a sus clientes.

## ARCHIVO 1: `backend/app/services/report_builder.py`

```python
class ReportMetric(BaseModel):
    metric_name: str
    current_value: float
    previous_value: float
    change_percentage: float
    trend: str              # "up" | "down" | "stable"
    is_positive: bool       # depende del metric (reach up = positive, unfollow up = negative)

class ReportSection(BaseModel):
    title: str
    summary: str
    metrics: list[ReportMetric]
    insights: list[str]
    recommendations: list[str]

class ExecutiveReport(BaseModel):
    client_name: str
    report_type: str        # "monthly" | "weekly" | "quarterly" | "campaign"
    period_start: str       # ISO date
    period_end: str         # ISO date
    generated_at: str
    executive_summary: str
    overall_score: float    # 0.0 a 10.0
    key_wins: list[str]
    key_challenges: list[str]
    sections: list[ReportSection]
    next_period_goals: list[str]
    agency_notes: str       # Notas personalizadas de la agencia

class ReportTemplate(BaseModel):
    template_id: str
    name: str               # "monthly_performance" | "campaign_results" | "quarterly_review"
    required_sections: list[str]
    tone: str               # "formal" | "friendly" | "executive"
```

Funciones puras:
- `calculate_change_percentage(current: float, previous: float) -> float`
- `determine_trend(changes: list[float]) -> str`
- `calculate_overall_score(metrics: list[ReportMetric]) -> float`
- `format_period_string(start: str, end: str) -> str`

## ARCHIVO 2: `backend/app/agents/report_generator_agent.py`

Usa **GPT-4** para narrativa ejecutiva profesional.

```python
async def generate_monthly_report(
    self,
    client_name: str,
    metrics_data: dict[str, float],
    previous_period_data: dict[str, float],
    agency_notes: str = ""
) -> ExecutiveReport:
    """Genera reporte mensual completo con narrativa ejecutiva"""

async def generate_campaign_report(
    self,
    client_name: str,
    campaign_name: str,
    campaign_data: dict[str, float],
    goals: dict[str, float]
) -> ExecutiveReport:
    """Reporte de resultados de campaña específica"""

async def write_executive_summary(
    self,
    metrics: list[ReportMetric],
    client_name: str,
    period: str
) -> str:
    """Narrativa ejecutiva de 2-3 párrafos, profesional y clara"""

async def identify_key_wins(
    self,
    metrics: list[ReportMetric]
) -> list[str]:
    """Identifica los 3-5 logros más destacados del período"""

async def format_as_markdown(
    self,
    report: ExecutiveReport
) -> str:
    """Convierte reporte a Markdown bien estructurado para enviar al cliente"""
```

## ARCHIVO 3: `backend/app/api/routes/reports.py`

```
POST /api/v1/reports/generate-monthly
POST /api/v1/reports/generate-campaign
POST /api/v1/reports/executive-summary
POST /api/v1/reports/format-markdown
GET  /api/v1/reports/templates
GET  /api/v1/reports/agent-status
```

Request bodies:
```python
class MonthlyReportRequest(BaseModel):
    client_name: str
    metrics_data: dict[str, float]
    previous_period_data: dict[str, float]
    agency_notes: str = ""

class CampaignReportRequest(BaseModel):
    client_name: str
    campaign_name: str
    campaign_data: dict[str, float]
    goals: dict[str, float]

class ExecutiveSummaryRequest(BaseModel):
    metrics: list[ReportMetric]
    client_name: str
    period: str

class FormatMarkdownRequest(BaseModel):
    report: ExecutiveReport
```

## Registrar en main.py:
```python
from app.api.routes import reports
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
```

---

# ══════════════════════════════════════
# AGENTE 11: GROWTH HACKER AGENT
# ══════════════════════════════════════

Implementa el **Growth Hacker Agent (Agente 11/15)**.

## ARCHIVO 1: `backend/app/services/growth_analyzer.py`

```python
class GrowthOpportunity(BaseModel):
    opportunity_id: str
    opportunity_type: str    # "collaboration" | "trending_format" | "cross_platform" | "audience_gap" | "repurpose"
    title: str
    description: str
    potential_impact: str    # "low" | "medium" | "high" | "explosive"
    effort_required: str     # "low" | "medium" | "high"
    estimated_roi: float     # Multiplicador esperado (2.0 = 2x)
    implementation_steps: list[str]
    time_to_results: str     # "days" | "weeks" | "months"
    platform: str

class GrowthExperiment(BaseModel):
    experiment_id: str
    hypothesis: str
    variable_tested: str     # "caption_length" | "posting_time" | "content_format" | "hashtag_count"
    control_description: str
    test_description: str
    success_metric: str
    target_improvement_percent: float
    duration_days: int
    status: str              # "planned" | "running" | "completed"

class GrowthReport(BaseModel):
    client_id: str
    current_growth_rate: float        # % mensual
    benchmark_growth_rate: float      # promedio industria
    growth_gap: float
    top_opportunities: list[GrowthOpportunity]
    recommended_experiments: list[GrowthExperiment]
    quick_wins: list[str]             # Acciones de <48h
    estimated_potential: str          # "conservative" | "moderate" | "aggressive"
```

Funciones puras:
- `calculate_growth_gap(current: float, benchmark: float) -> float`
- `rank_opportunities_by_roi(opportunities: list[GrowthOpportunity]) -> list[GrowthOpportunity]`
- `estimate_experiment_duration(variable: str) -> int`

## ARCHIVO 2: `backend/app/agents/growth_hacker_agent.py`

Usa **GPT-4**.

```python
async def identify_opportunities(
    self,
    account_data: dict[str, float | str | list],
    niche: str,
    platform: str
) -> list[GrowthOpportunity]:
    """Identifica top 5 oportunidades de crecimiento"""

async def design_experiment(
    self,
    opportunity: GrowthOpportunity
) -> GrowthExperiment:
    """Diseña experimento científico para validar la oportunidad"""

async def analyze_growth_trajectory(
    self,
    historical_data: list[dict[str, float]],
    industry_benchmarks: dict[str, float]
) -> GrowthReport:
    """Analiza trayectoria y genera reporte completo de crecimiento"""

async def generate_quick_wins(
    self,
    account_data: dict[str, float | str],
    platform: str
) -> list[str]:
    """5 acciones de menos de 48 horas para boost inmediato"""
```

## ARCHIVO 3: `backend/app/api/routes/growth.py`

```
POST /api/v1/growth/identify-opportunities
POST /api/v1/growth/design-experiment
POST /api/v1/growth/analyze-trajectory
POST /api/v1/growth/quick-wins
GET  /api/v1/growth/agent-status
```

## Registrar en main.py:
```python
from app.api.routes import growth
app.include_router(growth.router, prefix="/api/v1/growth", tags=["Growth Hacker"])
```

---

# ══════════════════════════════════════
# VERIFICACIÓN FINAL — main.py completo
# ══════════════════════════════════════

Verifica que main.py tenga estos 11 routers:

```python
from app.api.routes import (
    content, strategy, analytics, engagement,
    monitor, brand_voice, competitive, trends,
    crisis, reports, growth
)

app.include_router(content.router,    prefix="/api/v1/content",     tags=["Content"])
app.include_router(strategy.router,   prefix="/api/v1/strategy",    tags=["Strategy"])
app.include_router(analytics.router,  prefix="/api/v1/analytics",   tags=["Analytics"])
app.include_router(engagement.router, prefix="/api/v1/engagement",  tags=["Engagement"])
app.include_router(monitor.router,    prefix="/api/v1/monitor",     tags=["Monitor"])
app.include_router(brand_voice.router,prefix="/api/v1/brand-voice", tags=["Brand Voice"])
app.include_router(competitive.router,prefix="/api/v1/competitive", tags=["Competitive"])
app.include_router(trends.router,     prefix="/api/v1/trends",      tags=["Trends"])
app.include_router(crisis.router,     prefix="/api/v1/crisis",      tags=["Crisis Manager"])
app.include_router(reports.router,    prefix="/api/v1/reports",     tags=["Reports"])
app.include_router(growth.router,     prefix="/api/v1/growth",      tags=["Growth Hacker"])
```

## PROGRESS.md al completar:

```markdown
## 📊 Agentes: 11/15 (73%)

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

⏳ Agente 12: Video Production
⏳ Agente 13: Scheduling & Queue
⏳ Agente 14: A/B Testing
⏳ Agente 15: Orchestrator

🎯 Endpoints: 60/75 (80%)
🏆 73% COMPLETADO — RECTA FINAL
```

## REGLAS:
1. ✅ Max 200 líneas por archivo
2. ✅ CERO `any`
3. ✅ Claude Opus 4 para Crisis Manager (razonamiento complejo)
4. ✅ GPT-4 para Reports y Growth
5. ✅ Error handling en todos los endpoints
6. ✅ Commit y push al terminar los 3

🐢💎 No velocity, only precision.
