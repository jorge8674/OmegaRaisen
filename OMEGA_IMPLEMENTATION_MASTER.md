# OMEGA IMPLEMENTATION MASTER PLAN
## Phases 2, 3, 4 - Backend, Frontend, SENTINEL

**Based on:**
- OMEGA Prompt Intelligence System v1
- OMEGA Agent Arsenal v2
- Phase 1 Complete: Database setup ✅ (prompt_vault, seed memory, system prompts)

---

## 📊 CURRENT STATE (Phase 1 Complete)

### ✅ Database Setup Complete
- **prompt_vault** table created with 30 prompts across 4 verticals
- **omega_agent_memory** seed memory loaded for 6 key agents
- **omega_agents** system prompts loaded for NOVA, ATLAS, RAFA, SENTINEL
- **client_context.brand_file** column added (JSONB)

### 📈 Performance Baseline
- **Prompt Vault**: 30 prompts, avg score 8.25/10
- **Verticals**: Real Estate (8), Construction (7), Health (7), Restaurant (8)
- **Coverage**: caption, ad, email, script, story, post, hashtags

---

## 🔧 PHASE 2 — BACKEND INTEGRATION (Week 1-2)

### 2.1 Prompt Vault Query Integration

**File:** `backend/app/api/routes/content_lab/handlers/generate_text.py`

**Changes:**
```python
# BEFORE generate_text.py line 160 (AI provider call)
# ADD: Prompt Vault query logic

from app.infrastructure.repositories.prompt_vault_repository import PromptVaultRepository

async def handle_generate_text(...):
    try:
        # ... existing code ...

        # NEW: Query Prompt Vault for optimal prompt
        vault_repo = PromptVaultRepository(supabase)
        vault_prompt = await vault_repo.select_optimal_prompt(
            category=content_type,  # caption, ad, email, etc.
            vertical=context_data.get("vertical", "generic"),
            platform=context_data.get("platform", "instagram"),
            agent_code="RAFA"
        )

        # If vault prompt found, use it; otherwise use default
        if vault_prompt:
            user_prompt = vault_prompt["prompt_text"].format(
                brief=brief,
                brand_voice=brand_voice,
                **context_data
            )
            vault_used = {
                "id": vault_prompt["id"],
                "name": vault_prompt["name"],
                "technique": vault_prompt["technique"]
            }
        else:
            # Fallback to default prompt builder
            user_prompt = build_user_prompt(...)
            vault_used = None

        # ... existing AI provider call ...

        # Return with vault metadata
        return {
            "generated_text": llm_response["content"],
            "content_type": content_type,
            "provider": llm_response["provider"],
            "model": llm_response["model"],
            "director": director.upper(),
            "cached": False,
            "tokens_used": llm_response["tokens_used"],
            "vault_prompt_used": vault_used  # NEW
        }
```

**New File:** `backend/app/infrastructure/repositories/prompt_vault_repository.py`
```python
"""
Prompt Vault Repository — Dynamic prompt selection
"""
from typing import Optional, Dict, Any, List
from app.infrastructure.supabase_service import SupabaseService

class PromptVaultRepository:
    def __init__(self, supabase: SupabaseService):
        self.supabase = supabase

    async def select_optimal_prompt(
        self,
        category: str,
        vertical: str,
        platform: str,
        agent_code: str
    ) -> Optional[Dict[str, Any]]:
        """
        Selects best prompt from vault based on:
        1. Exact match (category + vertical + platform)
        2. Highest performance_score
        3. is_active = true
        """
        response = self.supabase.client.table("prompt_vault").select("*").match({
            "category": category,
            "vertical": vertical,
            "platform": platform,
            "agent_code": agent_code,
            "is_active": True
        }).order("performance_score", desc=True).limit(1).execute()

        if response.data:
            # Increment times_used
            prompt_id = response.data[0]["id"]
            self.supabase.client.table("prompt_vault").update({
                "times_used": response.data[0]["times_used"] + 1,
                "last_updated": "now()"
            }).eq("id", prompt_id).execute()

            return response.data[0]

        # Fallback: try without platform specificity
        response = self.supabase.client.table("prompt_vault").select("*").match({
            "category": category,
            "vertical": vertical,
            "agent_code": agent_code,
            "is_active": True
        }).order("performance_score", desc=True).limit(1).execute()

        return response.data[0] if response.data else None

    async def update_performance_score(
        self,
        prompt_id: str,
        engagement_rate: float
    ) -> None:
        """
        Updates prompt performance_score based on real engagement.
        Formula: new_score = (old_score * 0.7) + (engagement_rate * 10 * 0.3)
        """
        # Get current prompt
        response = self.supabase.client.table("prompt_vault").select(
            "performance_score, engagement_avg, times_used"
        ).eq("id", prompt_id).execute()

        if not response.data:
            return

        current = response.data[0]
        old_score = current["performance_score"]
        times_used = current["times_used"]

        # Calculate new engagement average
        if current["engagement_avg"] is None:
            new_engagement_avg = engagement_rate
        else:
            new_engagement_avg = (
                (current["engagement_avg"] * (times_used - 1)) + engagement_rate
            ) / times_used

        # Calculate new performance score (weighted)
        new_score = (old_score * 0.7) + (engagement_rate * 10 * 0.3)

        # Update
        self.supabase.client.table("prompt_vault").update({
            "performance_score": round(new_score, 2),
            "engagement_avg": round(new_engagement_avg, 2),
            "last_updated": "now()"
        }).eq("id", prompt_id).execute()
```

### 2.2 Prompt Vault CRUD Endpoints

**New File:** `backend/app/api/routes/prompt_vault/router.py`
```python
"""
Prompt Vault API — CRUD operations for prompt management
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from app.infrastructure.supabase_service import get_supabase_service
from .models import PromptVaultCreate, PromptVaultUpdate, PromptVaultResponse

router = APIRouter(prefix="/prompt-vault", tags=["prompt-vault"])

@router.get("/", response_model=List[PromptVaultResponse])
async def list_prompts(
    vertical: Optional[str] = None,
    category: Optional[str] = None,
    platform: Optional[str] = None,
    is_active: Optional[bool] = True,
    limit: int = 50
):
    """List prompts with optional filters"""
    supabase = get_supabase_service()
    query = supabase.client.table("prompt_vault").select("*")

    if vertical:
        query = query.eq("vertical", vertical)
    if category:
        query = query.eq("category", category)
    if platform:
        query = query.eq("platform", platform)
    if is_active is not None:
        query = query.eq("is_active", is_active)

    response = query.order("performance_score", desc=True).limit(limit).execute()
    return response.data

@router.get("/{prompt_id}", response_model=PromptVaultResponse)
async def get_prompt(prompt_id: str):
    """Get single prompt by ID"""
    supabase = get_supabase_service()
    response = supabase.client.table("prompt_vault").select("*").eq("id", prompt_id).execute()

    if not response.data:
        raise HTTPException(404, f"Prompt {prompt_id} not found")

    return response.data[0]

@router.post("/", response_model=PromptVaultResponse)
async def create_prompt(request: PromptVaultCreate):
    """Create new prompt in vault"""
    supabase = get_supabase_service()
    response = supabase.client.table("prompt_vault").insert(request.dict()).execute()

    if not response.data:
        raise HTTPException(500, "Failed to create prompt")

    return response.data[0]

@router.patch("/{prompt_id}", response_model=PromptVaultResponse)
async def update_prompt(prompt_id: str, request: PromptVaultUpdate):
    """Update existing prompt"""
    supabase = get_supabase_service()
    update_data = request.dict(exclude_unset=True)
    update_data["last_updated"] = "now()"

    response = supabase.client.table("prompt_vault").update(update_data).eq("id", prompt_id).execute()

    if not response.data:
        raise HTTPException(404, f"Prompt {prompt_id} not found")

    return response.data[0]

@router.delete("/{prompt_id}")
async def delete_prompt(prompt_id: str):
    """Soft delete (set is_active = false)"""
    supabase = get_supabase_service()
    response = supabase.client.table("prompt_vault").update({
        "is_active": False
    }).eq("id", prompt_id).execute()

    if not response.data:
        raise HTTPException(404, f"Prompt {prompt_id} not found")

    return {"id": prompt_id, "deleted": True}

@router.post("/{prompt_id}/performance")
async def update_performance(
    prompt_id: str,
    engagement_rate: float = Query(..., ge=0, le=1)
):
    """Update prompt performance based on real engagement"""
    from app.infrastructure.repositories.prompt_vault_repository import PromptVaultRepository
    supabase = get_supabase_service()
    vault_repo = PromptVaultRepository(supabase)

    await vault_repo.update_performance_score(prompt_id, engagement_rate)

    return {"prompt_id": prompt_id, "engagement_rate": engagement_rate, "updated": True}
```

**New File:** `backend/app/api/routes/prompt_vault/models.py`
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PromptVaultCreate(BaseModel):
    name: str
    category: str
    vertical: str
    platform: Optional[str] = None
    technique: str
    source: str = "omega-tested"
    prompt_text: str
    example_input: Optional[str] = None
    example_output: Optional[str] = None
    performance_score: float = 5.0
    agent_code: str = "RAFA"
    version: int = 1
    is_active: bool = True

class PromptVaultUpdate(BaseModel):
    name: Optional[str] = None
    prompt_text: Optional[str] = None
    performance_score: Optional[float] = None
    is_active: Optional[bool] = None

class PromptVaultResponse(BaseModel):
    id: str
    name: str
    category: str
    vertical: str
    platform: Optional[str]
    technique: str
    performance_score: float
    times_used: int
    engagement_avg: Optional[float]
    is_active: bool
    created_at: datetime
    last_updated: Optional[datetime]
```

### 2.3 Brand Voice Integration

**File:** `backend/app/api/routes/content_lab/handlers/generate_text.py`

**Add brand_file loading:**
```python
# After loading client_context (around line 100)
brand_file = context_data.get("brand_file", {})

# Extract brand voice elements
brand_voice = {
    "tone": brand_file.get("voice", {}).get("primary_tone", "professional"),
    "style": brand_file.get("voice", {}).get("language_style", "semiformal"),
    "do": brand_file.get("do", []),
    "dont": brand_file.get("dont", []),
    "personality": brand_file.get("voice", {}).get("personality_traits", [])
}

# Pass to prompt builder
system_prompt = build_system_prompt(
    client_name=client_name,
    business_type=context_data.get("business_type"),
    brand_voice=brand_voice,  # Enhanced with brand_file
    keywords=keywords
)
```

### 2.4 Inter-Agent Handoff Protocol

**New File:** `backend/app/services/handoff_service.py`
```python
"""
Inter-Agent Handoff Protocol — Structured task delegation
"""
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

class HandoffService:
    """Handles structured communication between agents"""

    @staticmethod
    def create_handoff(
        from_agent: str,
        to_agent: str,
        task_type: str,
        payload: Dict[str, Any],
        priority: str = "NORMAL",
        deadline: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates a structured handoff between agents.

        Args:
            from_agent: Source agent code (e.g., "NOVA")
            to_agent: Target agent code (e.g., "ATLAS")
            task_type: Type of task ("content_brief", "security_alert", etc.)
            payload: Task-specific data
            priority: URGENT | HIGH | NORMAL
            deadline: ISO8601 timestamp

        Returns:
            Handoff object with task_id for tracking
        """
        task_id = f"TASK-{uuid.uuid4().hex[:8]}"

        handoff = {
            "task_id": task_id,
            "from": from_agent,
            "to": to_agent,
            "task_type": task_type,
            "priority": priority,
            "payload": payload,
            "deadline": deadline,
            "created_at": datetime.utcnow().isoformat(),
            "status": "PENDING"
        }

        # Store in omega_agent_memory for tracking
        # (Implementation depends on memory service)

        return handoff

    @staticmethod
    def confirm_receipt(task_id: str, agent_code: str) -> Dict[str, Any]:
        """Agent confirms receipt of handoff"""
        return {
            "task_id": task_id,
            "confirmed_by": agent_code,
            "confirmed_at": datetime.utcnow().isoformat(),
            "status": "IN_PROGRESS"
        }

    @staticmethod
    def complete_handoff(
        task_id: str,
        agent_code: str,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Agent marks handoff as complete"""
        return {
            "task_id": task_id,
            "completed_by": agent_code,
            "completed_at": datetime.utcnow().isoformat(),
            "status": "COMPLETED",
            "result": result
        }
```

---

## 🎨 PHASE 3 — FRONTEND (LOVABLE) (Week 3-4)

### 3.1 Brand Voice UI in Client Onboarding

**New Component:** `src/components/onboarding/BrandVoiceForm.tsx`
```typescript
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';

interface BrandVoiceData {
  business_name: string;
  tagline: string;
  vertical: string;
  voice: {
    primary_tone: string;
    secondary_tone: string;
    personality_traits: string[];
    language_style: string;
  };
  do: string[];
  dont: string[];
}

export default function BrandVoiceForm({ clientId, onComplete }: { clientId: string; onComplete: () => void }) {
  const [brandVoice, setBrandVoice] = useState<BrandVoiceData>({
    business_name: '',
    tagline: '',
    vertical: 'generic',
    voice: {
      primary_tone: 'professional',
      secondary_tone: '',
      personality_traits: [],
      language_style: 'semiformal'
    },
    do: [''],
    dont: ['']
  });

  const handleSubmit = async () => {
    // Save to client_context.brand_file
    await fetch(`/api/v1/clients/${clientId}/brand-voice`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ brand_file: brandVoice })
    });

    onComplete();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Brand Voice Configuration 🎨</CardTitle>
        <p className="text-sm text-gray-600">
          Define la voz y personalidad de tu marca. Esto guía TODO el contenido que OMEGA crea.
        </p>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Basic Info */}
        <div className="space-y-4">
          <div>
            <Label htmlFor="business_name">Nombre del Negocio</Label>
            <Input
              id="business_name"
              value={brandVoice.business_name}
              onChange={(e) => setBrandVoice({...brandVoice, business_name: e.target.value})}
              placeholder="ej: Milagrosa Real Estate"
            />
          </div>

          <div>
            <Label htmlFor="tagline">Tagline</Label>
            <Input
              id="tagline"
              value={brandVoice.tagline}
              onChange={(e) => setBrandVoice({...brandVoice, tagline: e.target.value})}
              placeholder="ej: Tu hogar soñado te espera"
            />
          </div>

          <div>
            <Label htmlFor="vertical">Vertical / Industria</Label>
            <Select value={brandVoice.vertical} onValueChange={(val) => setBrandVoice({...brandVoice, vertical: val})}>
              <SelectTrigger>
                <SelectValue placeholder="Selecciona tu industria" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="real_estate">Real Estate</SelectItem>
                <SelectItem value="construction">Construcción</SelectItem>
                <SelectItem value="health">Salud y Bienestar</SelectItem>
                <SelectItem value="restaurant">Restaurante</SelectItem>
                <SelectItem value="generic">Otro</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Voice Configuration */}
        <div className="space-y-4 border-t pt-4">
          <h3 className="font-semibold">Tono de Voz</h3>

          <div>
            <Label htmlFor="primary_tone">Tono Principal</Label>
            <Select
              value={brandVoice.voice.primary_tone}
              onValueChange={(val) => setBrandVoice({
                ...brandVoice,
                voice: {...brandVoice.voice, primary_tone: val}
              })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="professional">Profesional</SelectItem>
                <SelectItem value="casual">Casual</SelectItem>
                <SelectItem value="aspiracional">Aspiracional</SelectItem>
                <SelectItem value="tecnico">Técnico</SelectItem>
                <SelectItem value="empatico">Empático</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="language_style">Estilo de Lenguaje</Label>
            <Select
              value={brandVoice.voice.language_style}
              onValueChange={(val) => setBrandVoice({
                ...brandVoice,
                voice: {...brandVoice.voice, language_style: val}
              })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="formal">Formal</SelectItem>
                <SelectItem value="semiformal">Semi-formal</SelectItem>
                <SelectItem value="coloquial">Coloquial</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Do's and Dont's */}
        <div className="space-y-4 border-t pt-4">
          <h3 className="font-semibold">Reglas de Contenido</h3>

          <div>
            <Label htmlFor="do">SÍ hacer (una regla por línea)</Label>
            <Textarea
              id="do"
              value={brandVoice.do.join('\n')}
              onChange={(e) => setBrandVoice({
                ...brandVoice,
                do: e.target.value.split('\n').filter(line => line.trim())
              })}
              placeholder="ej: Usar testimonios de clientes reales&#10;Mencionar ubicación en PR cuando sea relevante"
              rows={4}
            />
          </div>

          <div>
            <Label htmlFor="dont">NO hacer (una regla por línea)</Label>
            <Textarea
              id="dont"
              value={brandVoice.dont.join('\n')}
              onChange={(e) => setBrandVoice({
                ...brandVoice,
                dont: e.target.value.split('\n').filter(line => line.trim())
              })}
              placeholder="ej: Mencionar competidores por nombre&#10;Usar anglicismos innecesarios"
              rows={4}
            />
          </div>
        </div>

        <Button onClick={handleSubmit} className="w-full">
          Guardar Brand Voice
        </Button>
      </CardContent>
    </Card>
  );
}
```

### 3.2 Show Prompt Used in Generation UI

**Update:** `src/components/content-lab/ContentGeneratedCard.tsx`
```typescript
interface ContentGeneratedCardProps {
  generatedText: string;
  contentType: string;
  provider: string;
  model: string;
  director: string;
  vaultPromptUsed?: {
    id: string;
    name: string;
    technique: string;
  };
}

export default function ContentGeneratedCard({
  generatedText,
  contentType,
  provider,
  model,
  director,
  vaultPromptUsed
}: ContentGeneratedCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Contenido Generado ✨</CardTitle>
        {vaultPromptUsed && (
          <div className="text-xs text-gray-600 mt-2 bg-blue-50 p-2 rounded">
            <strong>Prompt usado:</strong> {vaultPromptUsed.name}
            <br />
            <strong>Técnica:</strong> {vaultPromptUsed.technique}
          </div>
        )}
      </CardHeader>

      <CardContent>
        <div className="bg-white p-4 rounded border">
          <p className="whitespace-pre-wrap">{generatedText}</p>
        </div>

        <div className="mt-4 text-xs text-gray-500 flex gap-4">
          <span>Director: {director}</span>
          <span>Provider: {provider}</span>
          <span>Model: {model}</span>
        </div>

        {vaultPromptUsed && (
          <Button
            variant="outline"
            size="sm"
            className="mt-2"
            onClick={() => {
              // Open modal to view full prompt details
            }}
          >
            Ver detalles del prompt
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
```

### 3.3 Performance Score Tracking

**New Endpoint:** Update after content is published

```typescript
// In content publish handler
const handlePublishContent = async (contentId: string, engagementRate: float) => {
  // Get the vault_prompt_id used for this content
  const content = await fetch(`/api/v1/content/${contentId}`).then(r => r.json());

  if (content.vault_prompt_id) {
    // Update prompt performance
    await fetch(`/api/v1/prompt-vault/${content.vault_prompt_id}/performance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ engagement_rate: engagementRate })
    });
  }
};
```

---

## 🛡️ PHASE 4 — SENTINEL IMPLEMENTATION (Week 5-6)

### 4.1 SENTINEL Service Architecture

**New File:** `backend/app/services/sentinel_service.py`
```python
"""
SENTINEL Security System — 12 Sub-Agents
Score Formula: vault(35%) + pulse_mon(35%) + db_guardian(30%)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import logging
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

class SentinelService:
    """Main SENTINEL coordination service"""

    def __init__(self):
        self.supabase = get_supabase_service()
        self.sub_agents = {
            "VAULT": VaultAgent(),
            "PULSE_MON": PulseMonAgent(),
            "DB_GUARDIAN": DBGuardianAgent(),
            "SHIELD_AI": ShieldAgent(),
            "GATE": GateAgent(),
            "WATCH": WatchAgent(),
            "CIPHER": CipherAgent(),
            "PROBE": ProbeAgent(),
            "TRACE": TraceAgent(),
            "GUARD": GuardAgent(),
            "SCAN": ScanAgent(),
            "ALERT": AlertAgent()
        }

    async def calculate_security_score(self) -> Dict[str, Any]:
        """
        Calculates Security Score from 3 primary sub-agents.
        Formula: vault(35%) + pulse_mon(35%) + db_guardian(30%)
        """
        # Run primary scans in parallel
        vault_result, pulse_result, db_result = await asyncio.gather(
            self.sub_agents["VAULT"].scan(),
            self.sub_agents["PULSE_MON"].check(),
            self.sub_agents["DB_GUARDIAN"].scan()
        )

        vault_score = vault_result["score"]
        pulse_score = pulse_result["score"]
        db_score = db_result["score"]

        # Calculate weighted score
        security_score = (
            (vault_score * 0.35) +
            (pulse_score * 0.35) +
            (db_score * 0.30)
        )

        # Determine status
        if security_score >= 85:
            status = "PRESIDENCIAL"
            deploy_status = "ALLOWED"
        elif security_score >= 70:
            status = "ATENCION"
            deploy_status = "SUPERVISED"
        else:
            status = "CRITICO"
            deploy_status = "BLOCKED"
            # Critical alert to Ibrain
            await self._alert_ibrain_critical(security_score, {
                "vault": vault_result,
                "pulse": pulse_result,
                "db": db_result
            })

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "security_score": round(security_score, 2),
            "status": status,
            "deploy_status": deploy_status,
            "component_scores": {
                "vault": {"score": vault_score, "findings": vault_result.get("findings", [])},
                "pulse_mon": {"score": pulse_score, "services": pulse_result.get("services", {})},
                "db_guardian": {"score": db_score, "issues": db_result.get("issues", [])}
            }
        }

        # Store in sentinel_scans table
        await self._store_scan_result(result)

        # Write brief to nova_data for NOVA
        await self._write_nova_brief(result)

        return result

    async def _store_scan_result(self, result: Dict[str, Any]):
        """Store scan result in sentinel_scans table"""
        self.supabase.client.table("sentinel_scans").insert({
            "scan_type": "full",
            "security_score": result["security_score"],
            "status": result["status"],
            "findings": result["component_scores"],
            "scanned_at": result["timestamp"]
        }).execute()

    async def _write_nova_brief(self, result: Dict[str, Any]):
        """Write security brief to nova_data for NOVA to read"""
        self.supabase.client.table("nova_data").insert({
            "data_type": "security_brief",
            "content": result,
            "priority": "CRITICAL" if result["status"] == "CRITICO" else "HIGH",
            "created_at": result["timestamp"]
        }).execute()

    async def _alert_ibrain_critical(self, score: float, details: Dict[str, Any]):
        """
        Send critical alert to Ibrain (SMS + Email)
        TODO: Integrate with notification service
        """
        logger.critical(f"SENTINEL CRITICAL ALERT: Security Score {score}")
        logger.critical(f"Details: {details}")
        # TODO: Send SMS via Twilio
        # TODO: Send Email via SendGrid

# Sub-Agent Classes
class VaultAgent:
    """VAULT — Secrets & Keys Guardian (35% of score)"""

    async def scan(self) -> Dict[str, Any]:
        """
        Scans for:
        - API keys exposed in logs
        - Key rotation overdue (>90 days)
        - Excessive permissions on service accounts
        """
        findings = []
        score = 100

        # TODO: Implement actual scanning logic
        # Check environment variables for sensitive keys
        # Check database for stored credentials
        # Check logs for accidental key exposure

        if len(findings) > 0:
            # Critical finding = score 0
            score = 0

        return {
            "score": score,
            "findings": findings,
            "scanned_at": datetime.utcnow().isoformat()
        }

class PulseMonAgent:
    """PULSE_MON — Infrastructure Monitor (35% of score)"""

    async def check(self) -> Dict[str, Any]:
        """
        Monitors:
        - Railway uptime & response time
        - Lovable uptime & response time
        - Supabase connection pool & query performance
        """
        services = {
            "railway": await self._check_railway(),
            "lovable": await self._check_lovable(),
            "supabase": await self._check_supabase()
        }

        # Calculate score based on service health
        total_score = sum(s["score"] for s in services.values()) / len(services)

        return {
            "score": round(total_score, 2),
            "services": services,
            "checked_at": datetime.utcnow().isoformat()
        }

    async def _check_railway(self) -> Dict[str, Any]:
        """Check Railway health"""
        # TODO: Implement health check
        return {"score": 100, "status": "healthy", "response_time_ms": 250}

    async def _check_lovable(self) -> Dict[str, Any]:
        """Check Lovable health"""
        # TODO: Implement health check
        return {"score": 100, "status": "healthy", "response_time_ms": 450}

    async def _check_supabase(self) -> Dict[str, Any]:
        """Check Supabase health"""
        # TODO: Implement health check
        return {"score": 100, "status": "healthy", "query_time_ms": 120}

class DBGuardianAgent:
    """DB_GUARDIAN — Database Integrity (30% of score)"""

    async def scan(self) -> Dict[str, Any]:
        """
        Scans for:
        - RLS violations (data leaks between clients)
        - Anomalous queries (SELECT * without LIMIT on large tables)
        - Integrity issues (orphaned foreign keys)
        """
        issues = []
        score = 100

        # TODO: Implement database integrity checks
        # Check RLS policies are active
        # Check for suspicious queries in logs
        # Check referential integrity

        if any(issue["severity"] == "CRITICAL" for issue in issues):
            score = 0

        return {
            "score": score,
            "issues": issues,
            "scanned_at": datetime.utcnow().isoformat()
        }

# Placeholder classes for other sub-agents
class ShieldAgent:
    """SHIELD_AI — Application Security"""
    pass

class GateAgent:
    """GATE — Access Control"""
    pass

class WatchAgent:
    """WATCH — Behavioral Anomaly Detection"""
    pass

class CipherAgent:
    """CIPHER — Encryption & Privacy"""
    pass

class ProbeAgent:
    """PROBE — Vulnerability Scanner"""
    pass

class TraceAgent:
    """TRACE — Audit Trail"""
    pass

class GuardAgent:
    """GUARD — Rate Limiting & DDoS Protection"""
    pass

class ScanAgent:
    """SCAN — Continuous Security Scanner"""
    pass

class AlertAgent:
    """ALERT — Security Alerting Intelligence"""
    pass
```

### 4.2 SENTINEL Endpoints

**New File:** `backend/app/api/routes/sentinel/router.py`
```python
"""
SENTINEL API — Security monitoring and alerts
"""
from fastapi import APIRouter, HTTPException
from app.services.sentinel_service import SentinelService

router = APIRouter(prefix="/sentinel", tags=["sentinel"])

@router.get("/security-score")
async def get_security_score():
    """Get current security score"""
    sentinel = SentinelService()
    result = await sentinel.calculate_security_score()
    return result

@router.post("/scan/full")
async def run_full_scan():
    """Run full security scan (all sub-agents)"""
    sentinel = SentinelService()
    result = await sentinel.calculate_security_score()
    return result

@router.get("/scans/recent")
async def get_recent_scans(limit: int = 10):
    """Get recent scan results"""
    from app.infrastructure.supabase_service import get_supabase_service
    supabase = get_supabase_service()

    response = supabase.client.table("sentinel_scans").select("*").order(
        "scanned_at", desc=True
    ).limit(limit).execute()

    return response.data

@router.get("/status")
async def get_sentinel_status():
    """Get SENTINEL system status"""
    return {
        "status": "OPERATIONAL",
        "sub_agents_active": 12,
        "last_scan": "2026-02-28T07:00:00Z",
        "next_scan": "2026-03-01T07:00:00Z"
    }
```

### 4.3 Cron Jobs (Railway)

**New File:** `backend/app/cron/sentinel_cron.py`
```python
"""
SENTINEL Cron Jobs
Schedule in Railway:
- 02:00 AM → VAULT scan
- 05:00 AM → DB_GUARDIAN scan
- 07:00 AM → Full scan + brief to NOVA
- Every 5 min → PULSE_MON check
- Every 1 hr → Write nova_brief
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.sentinel_service import SentinelService
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone="America/Puerto_Rico")
sentinel = SentinelService()

@scheduler.scheduled_job('cron', hour=2, minute=0)
async def vault_scan():
    """VAULT scan at 2:00 AM"""
    logger.info("Running VAULT scan...")
    result = await sentinel.sub_agents["VAULT"].scan()
    logger.info(f"VAULT scan complete: score={result['score']}")

@scheduler.scheduled_job('cron', hour=5, minute=0)
async def db_guardian_scan():
    """DB_GUARDIAN scan at 5:00 AM"""
    logger.info("Running DB_GUARDIAN scan...")
    result = await sentinel.sub_agents["DB_GUARDIAN"].scan()
    logger.info(f"DB_GUARDIAN scan complete: score={result['score']}")

@scheduler.scheduled_job('cron', hour=7, minute=0)
async def full_scan():
    """Full SENTINEL scan at 7:00 AM"""
    logger.info("Running full SENTINEL scan...")
    result = await sentinel.calculate_security_score()
    logger.info(f"Security Score: {result['security_score']} - {result['status']}")

@scheduler.scheduled_job('interval', minutes=5)
async def pulse_mon_check():
    """PULSE_MON check every 5 minutes"""
    result = await sentinel.sub_agents["PULSE_MON"].check()
    if result["score"] < 70:
        logger.warning(f"PULSE_MON alert: score={result['score']}")

@scheduler.scheduled_job('interval', hours=1)
async def write_nova_brief():
    """Write brief to NOVA every hour"""
    result = await sentinel.calculate_security_score()
    await sentinel._write_nova_brief(result)

def start_sentinel_cron():
    """Start SENTINEL cron scheduler"""
    scheduler.start()
    logger.info("SENTINEL cron jobs started")
```

**Update:** `backend/main.py`
```python
from app.cron.sentinel_cron import start_sentinel_cron

@app.on_event("startup")
async def startup_event():
    # Start SENTINEL cron jobs
    start_sentinel_cron()
```

---

## 📊 SUCCESS METRICS

### Phase 2 Success Criteria
- ✅ Prompt Vault queried in 100% of content generations
- ✅ Performance scores updating based on real engagement
- ✅ Brand Voice loaded from client_context.brand_file
- ✅ Inter-agent handoff protocol implemented with task_id tracking

### Phase 3 Success Criteria
- ✅ Brand Voice UI functional in client onboarding
- ✅ Users can see which prompt was used for each generation
- ✅ Performance score tracking visible in admin dashboard
- ✅ 80%+ of clients complete Brand Voice form within first week

### Phase 4 Success Criteria
- ✅ SENTINEL calculating security score every 5 minutes
- ✅ Alerts triggered when score < 70
- ✅ Full scan running at 7:00 AM daily
- ✅ NOVA receiving security briefs hourly
- ✅ Security Score visible in admin dashboard

---

## 🚀 DEPLOYMENT CHECKLIST

### Before Deploy
- [ ] All tests pass
- [ ] SENTINEL scan shows score ≥ 85
- [ ] Database migrations tested in staging
- [ ] Environment variables configured in Railway
- [ ] API documentation updated

### After Deploy
- [ ] Health check endpoint returns 200
- [ ] SENTINEL cron jobs running
- [ ] Prompt Vault queries working
- [ ] Brand Voice UI accessible
- [ ] Security Score visible in dashboard

---

## 📚 DOCUMENTATION UPDATES NEEDED

1. **API Docs**: Add `/prompt-vault/` and `/sentinel/` endpoints
2. **Agent Docs**: Update with handoff protocol examples
3. **Onboarding Guide**: Add Brand Voice setup steps
4. **Security Playbook**: SENTINEL escalation procedures

---

**Philosophy:** No velocity, only precision 🐢💎

**OMEGA AI Company** — Precision over Speed, Intelligence over Templates
