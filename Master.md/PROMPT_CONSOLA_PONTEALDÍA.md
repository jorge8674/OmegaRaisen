# PROMPT — AGENTE CONSOLA (Backend/Railway)
## Ponte al día y continúa

---

Lee todo esto antes de hacer cualquier cosa.

## CONTEXTO DEL PROYECTO

Soy Ibrain, CTO de Raisen Omega (OMEGA).
Stack: FastAPI en Railway + Supabase + GitHub.
GitHub: https://github.com/Software2026/OMEGA.git
Railway: https://omegaraisen-production.up.railway.app

## ESTADO ACTUAL DEL BACKEND

Lo que YA está funcionando en producción:
- 84 endpoints de agentes AI (/api/v1/content, /analytics, etc.)
- 11 endpoints de resellers (/api/v1/resellers/*)
- Supabase conectado: jsxuhutiduxjjuqtyoml.supabase.co
- Tablas activas: resellers, reseller_branding, reseller_agents
- Lazy initialization de supabase_service.py ✅
- email-validator==2.1.0 ✅
- supabase==2.7.0 ✅
- Railway verde y saludable ✅

## LO QUE NECESITO AHORA — EN ORDEN

### TAREA 1 — Verificar estado actual
Haz esto primero:
1. Lee backend/app/main.py — lista todos los routers registrados
2. Lee backend/app/api/routes/resellers.py — confirma los 11 endpoints
3. Haz curl a:
   https://omegaraisen-production.up.railway.app/api/v1/resellers/all
   Debe responder 200 con lista vacía.

Reporta el estado antes de continuar.

### TAREA 2 — Nuevo endpoint que hace falta para /reseller/branding

El frontend necesita guardar el branding completo del reseller.
El endpoint POST /api/v1/resellers/{id}/branding ya existe,
pero necesito verificar que acepta este body exacto:

```json
{
  "logo_url": "string | null",
  "hero_media_url": "string | null",
  "hero_media_type": "image | video",
  "primary_color": "38 85% 55%",
  "secondary_color": "225 12% 14%",
  "agency_tagline": "string",
  "badge_text": "string",
  "hero_cta_text": "string",
  "pain_items": ["string"],
  "solution_items": ["string"],
  "services": [{"title": "string", "description": "string", "icon": "string"}],
  "metrics": [{"value": "string", "label": "string"}],
  "process_steps": [{"step": 1, "title": "string", "description": "string"}],
  "testimonials": [{"name": "string", "company": "string", "text": "string"}],
  "footer_email": "string",
  "footer_phone": "string",
  "social_links": [{"platform": "string", "url": "string"}],
  "legal_pages": [{"title": "string", "content": "string"}]
}
```

Si el modelo Pydantic no tiene todos estos campos, agrégalos.
Si ya los tiene, confirma el schema exacto para dárselo a Lovable.

### TAREA 3 — Endpoint público para landing

El endpoint GET /api/v1/resellers/slug/{slug} ya existe.
Verifica que devuelve:
- Datos del reseller (agency_name, status)
- Branding completo (todo el objeto de reseller_branding)
- CORS abierto para * (es público, cualquier dominio accede)

Si CORS no está configurado para este endpoint específico → agrégalo.

### TAREA 4 — Nuevo endpoint: crear lead desde landing

La landing pública del reseller tiene un formulario de contacto.
Cuando alguien llena el formulario → debe guardarse como lead
asociado a ese reseller.

Crea este endpoint:
POST /api/v1/resellers/slug/{slug}/lead

Body:
```json
{
  "name": "string",
  "email": "string",
  "phone": "string | null",
  "message": "string | null",
  "source": "landing_page"
}
```

Guarda en la tabla leads (si existe) o en una tabla
leads_reseller con: reseller_id, name, email, phone, message, source, created_at

Response: {"success": true, "message": "Lead recibido"}

### TAREA 5 — Commit y push

Después de cada tarea:
git add .
git commit -m "feat: [descripción del cambio]"
git push origin main

Espera que Railway redeploy (verde) antes de confirmar.

## DESPUÉS DE ESTAS TAREAS

Reporta:
1. ✅ o ❌ de cada tarea
2. Schema EXACTO del modelo CreateResellerBrandingRequest
3. Confirmación de que /slug/{slug} devuelve branding completo
4. URL del nuevo endpoint de leads
5. Estado de Railway (verde/rojo)

Entonces Lovable puede conectar el frontend.
