# ✅ DEPLOYMENT CHECKLIST - FASE 2 RESELLERS

## 📋 PASO 1 — SUPABASE DATABASE

### 1.1 Ejecutar Migración SQL

```bash
📁 Archivo: backend/supabase_migrations/002_resellers_multitenant.sql
```

**Instrucciones:**
1. Ir a [Supabase Dashboard](https://app.supabase.com)
2. Seleccionar proyecto OMEGA
3. Menú lateral → **SQL Editor**
4. Click **New Query**
5. Copiar TODO el contenido de `002_resellers_multitenant.sql`
6. Pegar en editor
7. Click **Run** (o `Ctrl+Enter`)

**Resultado esperado:**
```
Success. No rows returned
```

### 1.2 Verificar Tablas Creadas

En **SQL Editor**, ejecutar:

```sql
-- Verificar tablas FASE 2
SELECT table_name
FROM information_schema.tables
WHERE table_name IN ('resellers', 'reseller_branding', 'reseller_agents')
ORDER BY table_name;
```

**Resultado esperado:**
```
reseller_agents
reseller_branding
resellers
```

### 1.3 Verificar Campos Agregados a `clients`

```sql
-- Verificar campos MultiOMEGA en clients
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'clients'
  AND column_name IN (
    'reseller_id',
    'monthly_budget_total',
    'budget_operative_60',
    'budget_reserve_40',
    'plan',
    'human_supervision',
    'status',
    'trial_active'
  )
ORDER BY column_name;
```

**Resultado esperado:** 8 filas

---

## 🗄️ PASO 2 — SUPABASE STORAGE

### 2.1 Crear Bucket

1. Menú lateral → **Storage**
2. Click **New Bucket**
3. Configurar:
   - **Name:** `reseller-media`
   - **Public bucket:** ✅ **Yes**
   - Click **Create bucket**

### 2.2 Configurar Políticas de Acceso

En **Storage** → `reseller-media` → **Policies**, ejecutar:

```sql
-- Política 1: Permitir uploads autenticados
CREATE POLICY "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'reseller-media');

-- Política 2: Permitir acceso público de lectura
CREATE POLICY "Allow public access"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'reseller-media');

-- Política 3: Permitir updates autenticados
CREATE POLICY "Allow authenticated updates"
ON storage.objects FOR UPDATE
TO authenticated
USING (bucket_id = 'reseller-media');
```

### 2.3 Configurar Límites de Tamaño

En **Storage** → `reseller-media` → **Settings**:

- **Max file size:** `15 MB`
- **Allowed MIME types:** `video/mp4, video/webm, image/jpeg, image/png, image/webp`

---

## 🚂 PASO 3 — RAILWAY DEPLOYMENT

### 3.1 Verificar Variables de Entorno

En Railway → Proyecto OMEGA → **Variables**:

**Agregar estas variables si no existen:**

```bash
# Supabase
SUPABASE_URL=https://[project-ref].supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**⚠️ IMPORTANTE:**
- `SUPABASE_SERVICE_ROLE_KEY` debe ser la **Service Role Key** (NO la Anon Key)
- Obtenerla en Supabase → Settings → API → `service_role` (secret)

### 3.2 Verificar Deployment

Railway debería hacer **auto-deploy** al hacer push a GitHub.

**Verificar en Railway:**
1. Tab **Deployments** → última build debe estar **Active** ✅
2. Ver logs: debe decir `Application startup complete`

### 3.3 Test de Endpoints

**Test 1: Health Check**
```bash
curl https://[railway-url]/health
```
**Esperado:** `{"status":"healthy","version":"2.0.0","agents":"15/15",...}`

**Test 2: Listar Resellers (vacío al inicio)**
```bash
curl https://[railway-url]/api/v1/resellers/all
```
**Esperado:** `{"success":true,"data":{"resellers":[],"count":0},...}`

**Test 3: Crear Reseller de Prueba**
```bash
curl -X POST https://[railway-url]/api/v1/resellers/create \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "test-agency",
    "agency_name": "Test Agency",
    "owner_email": "test@example.com",
    "owner_name": "Test Owner"
  }'
```
**Esperado:** `{"success":true,"data":{...},"message":"Reseller 'Test Agency' created successfully"}`

---

## 📊 PASO 4 — VERIFICACIÓN FINAL

### 4.1 Checklist Completo

- [ ] **Supabase Database**
  - [ ] Tablas `resellers`, `reseller_branding`, `reseller_agents` creadas
  - [ ] Tabla `clients` tiene columnas nuevas (reseller_id, budget_*, plan, etc.)
  - [ ] Tabla `leads` tiene columna `reseller_id`
  - [ ] Índices creados (8 índices totales)
  - [ ] Triggers funcionando (updated_at auto-update)

- [ ] **Supabase Storage**
  - [ ] Bucket `reseller-media` creado y público
  - [ ] 3 políticas de acceso configuradas
  - [ ] Límite de 15MB configurado
  - [ ] MIME types permitidos configurados

- [ ] **Railway Backend**
  - [ ] Variables de entorno configuradas:
    - [ ] `SUPABASE_URL`
    - [ ] `SUPABASE_ANON_KEY`
    - [ ] `SUPABASE_SERVICE_ROLE_KEY`
  - [ ] Deployment activo y corriendo
  - [ ] `/health` responde 200
  - [ ] `/api/v1/resellers/all` responde 200
  - [ ] Crear reseller funciona (201)

- [ ] **Código Backend**
  - [ ] Archivo `supabase_service.py` creado
  - [ ] Archivo `routes/resellers.py` creado (11 endpoints)
  - [ ] Router registrado en `main.py`
  - [ ] Dependencia `supabase==2.3.0` en requirements.txt
  - [ ] Variables en `config.py`

---

## 🧪 PASO 5 — TEST COMPLETO DE FLUJO

### Test Flow: Crear Reseller + Branding + Upload

```bash
# 1. Crear reseller
RESELLER_ID=$(curl -s -X POST https://[railway-url]/api/v1/resellers/create \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "agencia-demo",
    "agency_name": "Agencia Demo",
    "owner_email": "demo@agencia.com",
    "owner_name": "Demo Owner"
  }' | jq -r '.data.id')

echo "Reseller ID: $RESELLER_ID"

# 2. Actualizar branding
curl -X POST https://[railway-url]/api/v1/resellers/$RESELLER_ID/branding \
  -H "Content-Type: application/json" \
  -d '{
    "agency_tagline": "Tu agencia digital",
    "primary_color": "38 85% 55%",
    "hero_cta_text": "Comenzar Ahora"
  }'

# 3. Obtener branding por slug (público)
curl https://[railway-url]/api/v1/resellers/slug/agencia-demo

# 4. Upload hero media (con archivo real)
curl -X POST https://[railway-url]/api/v1/resellers/$RESELLER_ID/upload-hero-media \
  -F "file=@/path/to/image.jpg"
```

**Esperado:** Todos los endpoints responden con `"success": true`

---

## ⚠️ TROUBLESHOOTING

### Error: "Failed to initialize Supabase client"

**Causa:** Variables de entorno incorrectas

**Solución:**
1. Verificar que `SUPABASE_URL` termina en `.supabase.co`
2. Verificar que `SUPABASE_SERVICE_ROLE_KEY` es la key correcta (comienza con `eyJ...`)
3. Re-deploy en Railway después de cambiar variables

### Error: "relation 'resellers' does not exist"

**Causa:** Migración SQL no ejecutada

**Solución:**
1. Ir a Supabase → SQL Editor
2. Ejecutar `002_resellers_multitenant.sql` completo
3. Verificar con: `SELECT * FROM resellers LIMIT 1;`

### Error: "bucket 'reseller-media' not found"

**Causa:** Bucket no creado

**Solución:**
1. Supabase → Storage → New Bucket
2. Nombre: `reseller-media`
3. Public: Yes

### Error 500 en endpoints de resellers

**Causa:** Problemas de conexión Supabase

**Solución:**
1. Ver logs en Railway: `railway logs`
2. Buscar error específico
3. Verificar que la IP de Railway está permitida en Supabase (debería ser automático)

---

## 🎯 SIGUIENTE FASE

Una vez completado este checklist:

✅ **Backend FASE 2 está COMPLETO y FUNCIONAL**

➡️ **Próximo paso:** Frontend Lovable puede comenzar:
   - Landing page white-label dinámica
   - CMS para resellers
   - Gestión de branding
   - Asignación de clientes

---

**Fecha:** 2026-02-13
**Status:** Listo para deployment
**Total endpoints:** 95+ (84 agentes + 11 resellers)
