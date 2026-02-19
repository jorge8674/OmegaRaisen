# OMEGA — CONSOLA (BACKEND) SESSION CONTEXT
## Proyecto: OMEGA by Raisen | omegaraisen-production.up.railway.app
## Filosofía: No velocity, only precision 🐢💎

---

## IDENTIDAD DEL PROYECTO

- **Producto:** OMEGA — SaaS marketing platform para agencias y resellers
- **Backend:** FastAPI + Python 3.11 (Railway) → repo: jorge8674/OmegaRaisen.git
- **DB:** Supabase (PostgreSQL) via `app/infrastructure/supabase_service.py`
- **Auth:** JWT (python-jose) + bcrypt en tabla `clients`
- **Deployment:** Railway — `omegaraisen-production.up.railway.app`
- **Python path:** `backend/app/`

---

## ⛔ STOP — LEE ESTO ANTES DE ESCRIBIR UNA SOLA LÍNEA

Si tu respuesta va a violar cualquiera de las reglas de abajo:
**PARA. No escribas el código. Explica el problema y propón la solución correcta.**

Un archivo de 201 líneas es una violación.
Un `Dict[str, Any]` sin justificación documentada es una violación.
Una función que hace más de una cosa es una violación.
Lógica de negocio en un endpoint es una violación.
Imports dentro de funciones es una violación.

**Estas reglas no son sugerencias. Son la arquitectura.**

---

## CRITICAL ARCHITECTURE RULES — NON-NEGOTIABLE

### REGLA 1 — MAX 200 LÍNEAS POR ARCHIVO (ABSOLUTA)
```
❌ PROHIBIDO: Archivos de 201+ líneas
✅ OBLIGATORIO: Si llegas a 180 líneas → PARA y divide
✅ OBLIGATORIO: Propón la división antes de escribirla
```

### REGLA 2 — ZERO tipos vagos sin justificación
```
❌ PROHIBIDO (sin razón documentada):
  data: dict
  result: Any
  response: Dict
  items: list

✅ OBLIGATORIO:
  data: ClientContextData
  result: SubscriptionStatusResponse
  response: Dict[str, str]          ← al menos tipado por valor
  items: List[ClientRecord]

✅ EXCEPCIÓN DOCUMENTADA (única forma aceptable de Any):
  # Payload variable de Stripe — forma no garantizada por la API externa
  data: Optional[Dict[str, Any]]

  Sin ese comentario → no pasa.
```

### REGLA 3 — ESTRUCTURA DDD OBLIGATORIA
```
ESTRUCTURA DE MÓDULO:
backend/app/api/routes/[dominio]/
├── __init__.py     → Solo exporta router (máx 7 líneas)
├── router.py       → Solo registra sub-routers (máx 35 líneas)
├── models.py       → Solo Pydantic schemas, CERO lógica
├── [feature_a].py  → Endpoints de una funcionalidad
├── [feature_b].py  → Endpoints de otra funcionalidad
└── [config].py     → Config/constantes del dominio (si aplica)

CAPAS:
routes/    → HTTP: request/response, validación, auth
services/  → Lógica de negocio (si se extrae de routes)
infra/     → DB, APIs externas (supabase_service.py)
agents/    → AI agents (si aplica)
```

### REGLA 4 — SEPARACIÓN ESTRICTA DE RESPONSABILIDADES
```
models.py    → Solo Pydantic models. CERO lógica, CERO imports de negocio
router.py    → Solo include_router(). CERO lógica
__init__.py  → Solo "from .router import router; __all__ = ['router']"
endpoints    → HTTP validation + auth + delegación. CERO lógica de negocio
services     → Lógica de negocio pura. CERO HTTP (sin Request/Response)
infra        → DB queries. CERO lógica de negocio

❌ PROHIBIDO en models.py:
  from app.infrastructure.supabase_service import ...  (NO)
  def validate_and_save(self): ...                      (NO)

❌ PROHIBIDO en endpoints:
  if user.plan == 'basic' and len(items) > 2:  (lógica → va a service)
```

### REGLA 5 — FAIL-FAST PARA VARIABLES DE ENTORNO
```
✅ PATRÓN OBLIGATORIO para toda variable de entorno crítica:

# Al nivel de módulo (no dentro de funciones)
SECRET_KEY: str = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set. "
        "Configure it in Railway before deploying."
    )

❌ PROHIBIDO:
  key = os.environ.get("KEY")  # Puede ser None sin aviso
  key = os.environ.get("KEY", "default_insecure")  # Default inseguro
```

### REGLA 6 — IMPORTS TOP-LEVEL OBLIGATORIOS
```
❌ PROHIBIDO (imports dentro de funciones):
  async def my_endpoint():
      from app.infrastructure.supabase_service import get_supabase_service
      supabase = get_supabase_service()

✅ OBLIGATORIO (imports al nivel del módulo):
  from app.infrastructure.supabase_service import get_supabase_service

  async def my_endpoint():
      supabase = get_supabase_service()
```

### REGLA 7 — ERROR HANDLING SEMÁNTICO
```
HTTP Status codes obligatorios por tipo de error:
  400 → ValueError, input inválido, plan inválido
  401 → Token ausente o inválido
  403 → Authenticated pero no autorizado (client_id mismatch)
  404 → Recurso no encontrado
  402 → Error de pago (Stripe errors)
  409 → Conflicto (recurso ya existe)
  422 → Error de validación Pydantic (automático)
  500 → Error inesperado del servidor

✅ PATRÓN OBLIGATORIO en todos los endpoints:
  try:
      ...lógica...
  except HTTPException:
      raise                          # Re-raise sin envolver
  except ValueError as e:
      raise HTTPException(status_code=400, detail=str(e))
  except SpecificExternalError as e:
      logger.error(f"External error: {e}")
      raise HTTPException(status_code=40X, detail=...)
  except Exception as e:
      logger.error(f"Unexpected error: {e}", exc_info=True)
      raise HTTPException(status_code=500, detail="An error occurred")
```

### REGLA 8 — LOGGING OBLIGATORIO
```
✅ OBLIGATORIO en cada módulo:
  import logging
  logger = logging.getLogger(__name__)

✅ OBLIGATORIO en cada endpoint:
  - logger.info() en el happy path
  - logger.error() en cada except con contexto útil
  - logger.warning() para casos límite (no error, pero raro)

❌ PROHIBIDO:
  print()  → usar logger
  logger.error(e)  → siempre con contexto: logger.error(f"Context: {e}")
```

### REGLA 9 — AUTH EN ENDPOINTS PROTEGIDOS
```
✅ PATRÓN OBLIGATORIO para endpoints protegidos:
  from app.api.routes.auth.jwt_utils import get_current_user_id
  from typing import Optional
  from fastapi import Header

  async def protected_endpoint(
      authorization: Optional[str] = Header(None)
  ):
      client_id = await get_current_user_id(authorization)
      # client_id es el ID autenticado — úsalo para verificar ownership

✅ VERIFICACIÓN DE OWNERSHIP (cuando aplica):
  if authenticated_client_id != requested_client_id:
      raise HTTPException(
          status_code=403,
          detail="Cannot access another client's resource"
      )
```

### REGLA 10 — DOCSTRINGS OBLIGATORIOS
```
✅ OBLIGATORIO en cada endpoint:
  """
  Descripción clara del propósito.

  Args:
      param: descripción

  Returns:
      ResponseModel con ...

  Raises:
      HTTPException 400: descripción
      HTTPException 401: descripción
      HTTPException 500: descripción

  Security: (si aplica)
      Verifica que...
  """

✅ OBLIGATORIO en TODO CRÍTICO:
  # TODO CRÍTICO: Sin este handler, [consecuencia concreta].
  # Contexto: [qué falta, qué método implementar]
  # Prioridad: Alta (antes del primer cliente real)
```

### REGLA 11 — DRY ABSOLUTO
```
❌ PROHIBIDO: Misma constante en 2 archivos
❌ PROHIBIDO: Misma validación en 2 funciones
❌ PROHIBIDO: Misma query en 2 endpoints

✅ OBLIGATORIO: Extraer a:
  [dominio]/config.py   → constantes del dominio
  [dominio]/models.py   → schemas compartidos del dominio
  infrastructure/       → queries DB reutilizables
  utils/                → helpers puros
```

---

## FLUJO OBLIGATORIO ANTES DE CREAR CUALQUIER ARCHIVO

```
PASO 1: ¿Cuántas líneas tendrá? Si > 150 → divide primero
PASO 2: ¿Cuál es la responsabilidad única de este archivo?
PASO 3: ¿Hay tipos dict/Any sin justificar? → Define tipos específicos
PASO 4: ¿Hay lógica duplicada? → Extrae a utils o service
PASO 5: ¿El endpoint tiene lógica de negocio? → Extrae a service
PASO 6: MUÉSTRAME el plan antes de crear el archivo
```

**Si no sigues estos 6 pasos → NO crees el archivo.**

---

## PROCESO DE APROBACIÓN OBLIGATORIO

Para CADA archivo nuevo:
1. Muestra el contenido completo con número de líneas
2. Confirma: "X líneas — tipos justificados — responsabilidad única: [describe]"
3. Espera mi aprobación ✅ antes de crear
4. Solo después de ✅ → crea el archivo

---

## ESTADO ACTUAL DEL PROYECTO

### Módulos completados (NO tocar sin razón):
```
✅ auth/        → 7 módulos DDD (JWT + bcrypt)
✅ resellers/   → 9 módulos DDD
✅ billing/     → 7 módulos DDD (Stripe + webhooks)
   - models.py, stripe_config.py, checkout.py
   - webhook.py (TODO CRÍTICO: handle_subscription_updated)
   - subscription.py, router.py, __init__.py
✅ supabase_service.py → métodos async confirmados
```

### Módulos pendientes:
```
⏳ billing/webhook.py → Implementar handle_subscription_updated
⏳ context/ → Fase 3A (TAREA ACTUAL)
⏳ accounts/ → Fase 3A multi-cuenta
⏳ content/  → Inyección de contexto en generaciones
```

### Tarea actual (Fase 3A — Contexto de Cliente):
```
🎯 Tabla client_context en Supabase (SQL script)
🎯 backend/app/api/routes/context/ → módulo DDD completo
   - models.py: ClientContextCreate, ClientContextUpdate, ClientContextResponse
   - crud.py: GET + POST + PATCH endpoints
   - router.py + __init__.py
🎯 Inyección del contexto en /content/generate-* endpoints
```

---

## CONVENCIONES DE NAMING

```python
Archivos:     snake_case (client_context.py, stripe_config.py)
Clases:       PascalCase (ClientContextData, ApiResponse)
Funciones:    snake_case (get_client_context, update_subscription)
Constantes:   UPPER_SNAKE_CASE (VALID_PLANS, TRIAL_PERIOD_DAYS)
Variables:    snake_case (client_id, subscription_data)
Routers:      router = APIRouter()  (siempre "router")
Loggers:      logger = logging.getLogger(__name__)  (siempre "logger")
```

---

## MÓDULOS DE INFRAESTRUCTURA DISPONIBLES

```python
# DB — supabase_service.py
from app.infrastructure.supabase_service import get_supabase_service
# Métodos confirmados disponibles:
#   update_client_subscription(client_id, stripe_customer_id, ...)
#   cancel_client_subscription(stripe_subscription_id)
#   get_client_subscription(client_id)

# Auth — jwt_utils.py
from app.api.routes.auth.jwt_utils import get_current_user_id
# Uso: client_id = await get_current_user_id(authorization_header)

# Stripe
from app.api.routes.billing.stripe_config import stripe, get_price_id, TRIAL_PERIOD_DAYS
```

---

## PATRONES DE CÓDIGO APROBADOS

### Pydantic Model (models.py)
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class ClientContextCreate(BaseModel):
    client_id: str = Field(..., description="UUID del cliente")
    business_name: str = Field(..., min_length=1, max_length=200)
    industry: str = Field(..., min_length=1, max_length=100)
    communication_tone: str = Field(default="casual")
    business_description: Optional[str] = Field(default=None, max_length=1000)

class ClientContextResponse(BaseModel):
    success: bool
    data: Optional[ClientContextData] = None
    error: Optional[str] = None
    message: Optional[str] = None
```

### Endpoint (feature.py)
```python
@router.post("/context", response_model=ClientContextResponse)
async def create_client_context(
    request: ClientContextCreate,
    authorization: Optional[str] = Header(None)
) -> ClientContextResponse:
    """
    Create context profile for a client.
    ...
    """
    try:
        client_id = await get_current_user_id(authorization)
        if client_id != request.client_id:
            raise HTTPException(status_code=403, detail="...")
        supabase = get_supabase_service()
        result = await supabase.create_client_context(request.dict())
        logger.info(f"Context created for client {client_id}")
        return ClientContextResponse(success=True, data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating context: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred")
```

---

## RECORDATORIO FINAL

```
🐢 La tortuga gana la carrera.
💎 El diamante no se forma en un día.

Un módulo bien diseñado hoy = 10 bugs menos mañana.
Tipos correctos hoy = refactor evitado en 3 meses.
Fail-fast hoy = outage evitado en producción.
Junior dev en junio necesita código que pueda entender.

No velocity, only precision. 🐢💎
```
