# OMEGA PHASE 3 — Frontend Requirements for Lovable
## Frontend Integration Specifications — 2026-02-24

**Purpose:** This document specifies the frontend components required to integrate with the completed Phase 2 backend infrastructure. These should be built using Lovable.

---

## 📋 OVERVIEW

### Backend APIs Available (Phase 2 Complete)
- ✅ Prompt Vault API: `/api/v1/prompt-vault/` (9 endpoints)
- ✅ Handoff Protocol API: `/api/v1/handoff/` (5 endpoints)
- ✅ Content Lab API: Enhanced with brand voice + vault prompts
- ✅ SENTINEL API: `/api/v1/sentinel/` (4 endpoints)

### Frontend Tasks
1. **Brand Voice Onboarding Component** — Capture brand voice during client setup
2. **Prompt Metadata Display** — Show which vault prompt was used
3. **Performance Tracking UI** — Send engagement data back to vault
4. **Handoff Dashboard** — View and manage inter-agent tasks (optional)

---

## 1️⃣ BRAND VOICE ONBOARDING COMPONENT

### Component Path
`src/components/onboarding/BrandVoiceForm.tsx`

### Purpose
Collect brand voice rules during client onboarding and save to `client_context.brand_file` (JSONB).

### User Story
> "As a new client, I want to define my brand's tone, style, and communication rules so that all generated content matches my brand identity."

### UI Layout

```
┌─────────────────────────────────────────────────────┐
│  Step 3: Define Your Brand Voice                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Primary Tone                                       │
│  ○ Professional  ○ Casual  ○ Aspirational         │
│                                                     │
│  Language Style                                     │
│  ○ Formal  ○ Semi-formal  ○ Colloquial            │
│                                                     │
│  Personality Traits (select multiple)               │
│  ☑ Trustworthy  ☑ Innovative  ☐ Friendly          │
│  ☐ Bold  ☐ Elegant  ☐ Playful                     │
│                                                     │
│  Allow Emojis in Content?                           │
│  ○ Yes  ○ No                                       │
│                                                     │
│  Writing Guidelines                                 │
│  ┌───────────────────────────────────────────────┐ │
│  │ Do (separate with Enter):                     │ │
│  │ • Use customer testimonials                   │ │
│  │ • Mention Puerto Rico location                │ │
│  │ • Include call-to-action in every post       │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │ Don't (separate with Enter):                  │ │
│  │ • Mention competitors by name                 │ │
│  │ • Use anglicisms or jargon                    │ │
│  │ • Make price comparisons                      │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│           [Skip for now]  [Save Brand Voice]       │
└─────────────────────────────────────────────────────┘
```

### API Integration

**Endpoint:** `PATCH /api/v1/clients/{client_id}/brand-voice`

**Request Body:**
```json
{
  "brand_file": {
    "voice": {
      "primary_tone": "professional",
      "language_style": "semiformal",
      "personality_traits": ["trustworthy", "innovative"],
      "emojis_allowed": true
    },
    "do": [
      "Use customer testimonials",
      "Mention Puerto Rico location",
      "Include call-to-action in every post"
    ],
    "dont": [
      "Mention competitors by name",
      "Use anglicisms or jargon",
      "Make price comparisons"
    ]
  }
}
```

**Note:** This endpoint may need to be created if it doesn't exist. Alternative: directly update `client_context` table via Supabase client.

### Technical Notes
- Use React Hook Form for state management
- Convert textarea input (line-separated) to string array
- Validate at least 1 "do" and 1 "don't" rule
- Save to `client_context.brand_file` JSONB column
- Show success toast: "Brand voice saved successfully"

---

## 2️⃣ PROMPT METADATA DISPLAY

### Component Path
`src/components/content-lab/ContentGeneratedCard.tsx`

### Purpose
Display which Prompt Vault template was used to generate content (for transparency and performance tracking).

### User Story
> "As a user, I want to see which AI prompt technique was used to generate my content so I can understand why certain content performs better."

### UI Enhancement

**Before (existing):**
```
┌────────────────────────────────────────┐
│ Instagram Caption                      │
│ Generated 2 minutes ago                │
│                                        │
│ "Your content here..."                 │
│                                        │
│ Provider: Anthropic (Claude Sonnet)   │
│ Tokens: 234                            │
└────────────────────────────────────────┘
```

**After (with vault metadata):**
```
┌────────────────────────────────────────┐
│ Instagram Caption  🎯 Vault Prompt     │
│ Generated 2 minutes ago                │
│                                        │
│ "Your content here..."                 │
│                                        │
│ ┌────────────────────────────────────┐ │
│ │ Prompt: Hook-First Storytelling    │ │
│ │ Technique: AIDA Framework          │ │
│ │ Performance: ⭐⭐⭐⭐ (8.2/10)       │ │
│ │ [View Full Prompt]                 │ │
│ └────────────────────────────────────┘ │
│                                        │
│ Provider: Anthropic (Claude Sonnet)   │
│ Tokens: 234                            │
└────────────────────────────────────────┘
```

### API Data Source

Content Lab API response already includes:
```json
{
  "generated_text": "...",
  "vault_prompt_used": {
    "id": "uuid-here",
    "name": "Hook-First Storytelling",
    "technique": "AIDA Framework",
    "performance_score": 8.2
  }
}
```

### Technical Notes
- Check if `vault_prompt_used` exists in response
- If null: show "Default Prompt" badge instead
- Performance score display: ⭐ (0-2), ⭐⭐ (2-4), ⭐⭐⭐ (4-7), ⭐⭐⭐⭐ (7-9), ⭐⭐⭐⭐⭐ (9-10)
- "View Full Prompt" button opens modal with full `prompt_text`

---

## 3️⃣ PERFORMANCE TRACKING UI

### Component Path
`src/components/analytics/EngagementTracker.tsx`

### Purpose
After content is published and has engagement data, send performance metrics back to Prompt Vault for learning.

### User Story
> "As the system, I want to learn from real engagement data so that high-performing prompts are used more often in the future."

### User Flow

1. Content is generated using vault prompt (stored in DB with `vault_prompt_id`)
2. Content is published to social media
3. After 24-48 hours, engagement data is collected
4. System calculates `engagement_rate` (likes + comments + shares) / impressions
5. Frontend sends engagement rate to backend
6. Backend updates prompt's `performance_score` using weighted formula

### API Integration

**Endpoint:** `POST /api/v1/prompt-vault/{vault_prompt_id}/performance`

**Request Body:**
```json
{
  "engagement_rate": 0.045
}
```

**Response:**
```json
{
  "prompt_id": "uuid-here",
  "engagement_rate": 0.045,
  "new_performance_score": 8.5,
  "engagement_avg": 0.042,
  "times_used": 127,
  "updated": true
}
```

### UI Implementation

**Option A: Automatic (Recommended)**
- Background job runs daily at 3 AM
- Queries all published content from last 48 hours
- Fetches engagement data from social platforms
- Automatically sends performance updates
- No UI required

**Option B: Manual Trigger**
```
┌─────────────────────────────────────────┐
│ Published Content Performance           │
├─────────────────────────────────────────┤
│                                         │
│ Post: "Your content here..."            │
│ Published: 2 days ago                   │
│                                         │
│ Engagement Data:                        │
│ • Impressions: 2,450                    │
│ • Likes: 87                             │
│ • Comments: 12                          │
│ • Shares: 11                            │
│ • Engagement Rate: 4.5%                 │
│                                         │
│ [Update Prompt Performance] ← Button   │
└─────────────────────────────────────────┘
```

### Technical Notes
- Only send if `vault_prompt_id` is not null
- Calculate: `engagement_rate = (likes + comments + shares) / impressions`
- Show success toast: "Prompt performance updated — helping AI learn!"
- Backend handles weighted score calculation automatically

---

## 4️⃣ HANDOFF DASHBOARD (Optional)

### Component Path
`src/components/admin/HandoffDashboard.tsx`

### Purpose
View and manage inter-agent task delegations (for advanced users/admins).

### User Story
> "As an admin, I want to see all pending tasks between AI agents so I can monitor the delegation workflow."

### UI Layout

```
┌────────────────────────────────────────────────────────┐
│  Inter-Agent Handoffs  🤝                              │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Filter: [All Agents ▼]  Status: [Pending ▼]         │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │ TASK-a3f7c8d9  🔥 HIGH                           │ │
│  │ NOVA → ATLAS                                     │ │
│  │ Type: content_brief                              │ │
│  │ Created: 2 hours ago                             │ │
│  │                                                  │ │
│  │ Payload: Generate LinkedIn content series...    │ │
│  │                                                  │ │
│  │ Status: PENDING                                  │ │
│  │ [View Details]                                   │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │ TASK-b2e8f1a0  ✅ NORMAL                         │ │
│  │ SENTINEL → NOVA                                  │ │
│  │ Type: security_alert                             │ │
│  │ Created: 5 hours ago                             │ │
│  │                                                  │ │
│  │ Payload: Security score dropped to 72...        │ │
│  │                                                  │ │
│  │ Status: COMPLETED                                │ │
│  │ [View Details]                                   │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### API Integration

**Get Pending Handoffs:**
`GET /api/v1/handoff/pending/{agent_code}`

**Response:**
```json
{
  "handoffs": [
    {
      "task_id": "TASK-a3f7c8d9",
      "from_agent": "NOVA",
      "to_agent": "ATLAS",
      "task_type": "content_brief",
      "payload": { ... },
      "priority": "HIGH",
      "status": "PENDING",
      "created_at": "2026-02-24T10:30:00Z"
    }
  ],
  "count": 1
}
```

### Technical Notes
- Poll endpoint every 30 seconds for real-time updates
- Color-code priority: 🔥 URGENT (red), 🔥 HIGH (orange), ✅ NORMAL (green), ⬇️ LOW (gray)
- Status badges: PENDING (yellow), IN_PROGRESS (blue), COMPLETED (green)
- Only show to admin users

---

## 📦 COMPONENT DEPENDENCIES

### Required Libraries
```bash
# If not already installed
npm install react-hook-form zod
npm install @radix-ui/react-dialog  # For modals
npm install lucide-react  # For icons
```

### API Client Setup
```typescript
// src/lib/api/promptVault.ts
export async function updatePromptPerformance(
  promptId: string,
  engagementRate: number
) {
  const res = await fetch(`/api/v1/prompt-vault/${promptId}/performance`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ engagement_rate: engagementRate })
  });
  return res.json();
}
```

---

## 🎯 IMPLEMENTATION PRIORITY

### Must-Have (Phase 3.1)
1. **Brand Voice Form** — Core feature for brand consistency
2. **Prompt Metadata Display** — User transparency

### Nice-to-Have (Phase 3.2)
3. **Performance Tracking** — Can start with automatic background job
4. **Handoff Dashboard** — Admin-only feature, not critical for MVP

---

## ✅ ACCEPTANCE CRITERIA

### Brand Voice Form
- [ ] Form saves to `client_context.brand_file` JSONB
- [ ] At least 1 "do" and 1 "don't" rule required
- [ ] Success/error toast notifications
- [ ] Skippable (saves empty object if skipped)

### Prompt Metadata Display
- [ ] Shows vault prompt name, technique, score when available
- [ ] Shows "Default Prompt" badge when vault_prompt_used is null
- [ ] Star rating visualization for performance_score
- [ ] "View Full Prompt" modal shows complete prompt_text

### Performance Tracking
- [ ] Engagement rate calculated correctly
- [ ] API call only sent if vault_prompt_id exists
- [ ] Success confirmation shown to user
- [ ] Error handling for failed API calls

---

## 📊 DATA FLOW DIAGRAM

```
┌──────────────────┐
│  User Onboards   │
└────────┬─────────┘
         │
         ▼
┌──────────────────────┐
│ BrandVoiceForm.tsx   │ → PATCH /api/v1/clients/{id}
│ Saves brand_file     │   (or direct Supabase update)
└──────────────────────┘

         ↓

┌──────────────────────┐
│  User Generates      │
│  Content             │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Backend selects vault prompt    │
│ (brand voice included in system  │
│  prompt automatically)           │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ ContentGeneratedCard.tsx         │
│ Displays vault_prompt_used       │
└────────┬─────────────────────────┘
         │
         ▼ (24-48 hours later)
┌──────────────────────────────────┐
│ Engagement data collected        │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ POST /api/v1/prompt-vault/{id}/  │
│ performance                      │
│ (updates performance_score)      │
└──────────────────────────────────┘
```

---

## 🛠️ TECHNICAL NOTES FOR LOVABLE

### Supabase Direct Access
If creating new endpoints is difficult, you can directly update `client_context` table:

```typescript
const { data, error } = await supabase
  .from('client_context')
  .update({
    brand_file: brandVoiceData
  })
  .eq('client_id', clientId);
```

### TypeScript Types

```typescript
interface BrandVoice {
  voice: {
    primary_tone: 'professional' | 'casual' | 'aspiracional';
    language_style: 'formal' | 'semiformal' | 'coloquial';
    personality_traits: string[];
    emojis_allowed: boolean;
  };
  do: string[];
  dont: string[];
}

interface VaultPromptMetadata {
  id: string;
  name: string;
  technique: string;
  performance_score: number;
}
```

---

**Philosophy:** No velocity, only precision 🐢💎

**OMEGA AI Company** — Intelligence that learns from every generation
