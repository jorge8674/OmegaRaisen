# PROMPT — AGENTE LOVABLE (Frontend)
## Ponte al día y continúa

---

Lee todo esto antes de tocar cualquier archivo.

## CONTEXTO DEL PROYECTO

Proyecto: Raisen OMEGA — plataforma SaaS de marketing con AI
URL producción: https://r-omega.agency
Backend Railway: https://omegaraisen-production.up.railway.app
Stack: Next.js/React + Tailwind + design system oscuro propio

## SISTEMA DE DISEÑO — NUNCA ROMPER ESTO

```
Dark mode ÚNICO. Sin light mode jamás.
Colores HSL:
  background:  225 15% 5%
  primary:     38 85% 55%   (oro/ámbar — CTAs y accents)
  secondary:   225 12% 14%
  card:        225 15% 8%
  border:      225 12% 16%

Tipografía:
  font-display: Syne (títulos, badges, botones, logo)
  font-body:    DM Sans (párrafos, labels, inputs)

Cursor personalizado global (oro)
```

## LO QUE YA ESTÁ CONSTRUIDO

Páginas completas y funcionales:
- /dashboard, /contenido, /calendario, /analytics
- /competitive, /crisis-room, /growth
- /admin/resellers (KPIs + tabla + modal crear + switches)
- /reseller/dashboard (KPIs + clientes + agentes + estado OMEGA)

Sidebar tiene sección "Admin" con:
- Resellers → /admin/resellers
- Mi Panel → /reseller/dashboard

Todo el api-client.ts tiene los endpoints de Railway configurados.
BASE_URL = https://omegaraisen-production.up.railway.app

## LO QUE NECESITO AHORA — EN ORDEN ESTRICTO

No avances a la siguiente tarea hasta que la anterior esté
100% funcional y confirmada.

---

### TAREA 1 — /reseller/branding (Editor Visual)

RUTA: /reseller/branding?reseller_id={id}

Agrega al sidebar bajo "Admin":
  - Resellers
  - Mi Panel
  - Mi Branding ← nuevo, apunta a /reseller/branding

HEADER:
  Título: "Editor de Branding"
  Subtítulo: "Personaliza la landing page de tu agencia"
  Botón derecha: "Ver Landing →" abre {slug}.r-omega.agency en nueva tab

LAYOUT: 2 columnas en desktop
  Izquierda (60%): 5 tabs de edición
  Derecha (40%): Preview en tiempo real (iframe o mock)

---

TAB 1 — Identidad Visual:
  Logo actual (si tiene) con botón "Cambiar logo"
  Upload de logo: PNG/JPG/SVG, máx 5MB
    → POST /api/v1/resellers/{id}/upload-hero-media con file
    → Guarda la URL devuelta en logo_url
  
  Color primario: color picker que guarda en HSL format
    Ej: "38 85% 55%" (sin el hsl())
    Muestra preview del color seleccionado
  
  Color secundario: igual
  
  Nombre de agencia (agency_name): input editable
  Tagline (agency_tagline): input, ej: "Tu agencia de marketing digital"
  Badge text (badge_text): input, ej: "Boutique Creative Agency"
  CTA del hero (hero_cta_text): input, ej: "Comenzar ahora"

---

TAB 2 — Hero:
  Tipo de media hero:
    ○ Imagen (jpg/png/webp)
    ○ Video (mp4/webm)
    ○ Sin media (usa el fondo 3D por defecto)
  
  Upload de media hero: máx 15MB
    → POST /api/v1/resellers/{id}/upload-hero-media
    → Guarda URL en hero_media_url
    → Guarda tipo en hero_media_type
  
  Preview del hero con la media subida
  Botón: "Eliminar media" → vuelve al fondo por defecto

---

TAB 3 — Secciones:
  Cada sección tiene lista editable (añadir/eliminar/editar items)

  PAIN ITEMS (problemas del cliente):
    Lista de strings editables
    Botón "+ Añadir problema"
    Ejemplo: "Pierdes tiempo en múltiples herramientas"

  SOLUTION ITEMS (soluciones):
    Lista de strings editables
    Botón "+ Añadir solución"

  SERVICIOS:
    Lista de cards: título + descripción + ícono (emoji o nombre de lucide icon)
    Botón "+ Añadir servicio"

  MÉTRICAS (números impactantes):
    Lista de pares: valor + label
    Ej: "47" + "Clientes activos"
    Botón "+ Añadir métrica"

  PASOS DEL PROCESO:
    Lista numerada: número + título + descripción
    Botón "+ Añadir paso"

---

TAB 4 — Social Proof:
  TESTIMONIOS:
    Lista de cards: nombre + empresa + texto
    Botón "+ Añadir testimonio"

  (Logos de clientes: por ahora solo placeholder, implementar después)

---

TAB 5 — Contacto y Footer:
  Email de contacto (footer_email)
  Teléfono (footer_phone)
  
  REDES SOCIALES:
    Lista de pares: plataforma + URL
    Plataformas: Instagram, Facebook, LinkedIn, TikTok, Twitter, YouTube
    Botón "+ Añadir red social"
  
  PÁGINAS LEGALES:
    Lista de pares: título + contenido (textarea)
    Ej: "Política de Privacidad" + contenido
    Botón "+ Añadir página legal"

---

BOTÓN GUARDAR (sticky en bottom):
  "Guardar Cambios" →
  POST /api/v1/resellers/{id}/branding
  con todo el objeto de branding
  
  Si 200 → toast "Branding guardado exitosamente"
  Si error → toast rojo con el error

CARGA INICIAL:
  Al entrar → GET /api/v1/resellers/{id}/branding
  Pre-llena todos los campos con los datos existentes
  Si no hay branding → campos vacíos con placeholders

---

### TAREA 2 — /landing/:slug (Landing Pública White-Label)

IMPORTANTE: Esta es una página PÚBLICA. 
Cero branding de OMEGA. Cero mención a RAISEN.
Todo es del reseller.

RUTA: /landing/:slug (o /[slug] en el router)
También debe funcionar en: {slug}.r-omega.agency
(El subdominio lo configuramos después en el DNS)

AL CARGAR:
  GET /api/v1/resellers/slug/{slug}
  Si el reseller no existe → 404 page elegante
  Si está suspendido → página de "Servicio no disponible"
  Si está activo → renderiza la landing completa

VARIABLES CSS DINÁMICAS:
  :root {
    --landing-primary: {branding.primary_color};
    --landing-secondary: {branding.secondary_color};
  }
  Todo el color de la landing usa estas variables.

SECCIONES DE LA LANDING (en orden):

1. HERO:
   Logo del reseller (branding.logo_url) o nombre en Syne
   Badge: {branding.badge_text}
   H1: Tagline de impacto basado en {branding.agency_tagline}
   CTA button: {branding.hero_cta_text} → scroll al formulario
   
   Background (en este orden de prioridad):
   a) Si hero_media_type = "video" → video autoplay loop muted
   b) Si hero_media_type = "image" → background-image cover
   c) Si sin media → fondo oscuro con gradiente del color primario

2. PAIN/SOLUTION:
   Título: "¿Te identificas con esto?"
   Lista de {branding.pain_items} con ícono de X roja
   Título: "Con nosotros obtienes:"
   Lista de {branding.solution_items} con ícono de check dorado

3. SERVICIOS:
   Grid de cards con {branding.services}
   Cada card: ícono + título + descripción
   Fondo: color secondary del reseller

4. MÉTRICAS:
   Row de números grandes con {branding.metrics}
   Animación de count-up al hacer scroll

5. PROCESO:
   Pasos numerados de {branding.process_steps}
   Timeline visual

6. TESTIMONIOS:
   Cards de {branding.testimonials}
   Con comillas y gradiente sutil

7. FORMULARIO DE CONTACTO:
   Título: "Hablemos"
   Campos: Nombre, Email, Teléfono (opcional), Mensaje (opcional)
   Botón: {branding.hero_cta_text}
   
   Al submit:
   POST /api/v1/resellers/slug/{slug}/lead
   Body: { name, email, phone, message, source: "landing_page" }
   
   Si 200 → "¡Gracias! Te contactaremos pronto." 
   Si error → "Hubo un error. Intenta de nuevo."

8. FOOTER:
   Logo o nombre del reseller
   Email: {branding.footer_email}
   Teléfono: {branding.footer_phone}
   Redes sociales: {branding.social_links} con íconos
   Links a páginas legales: {branding.legal_pages}
   © {año} {agency_name}. Todos los derechos reservados.
   (SIN mención a OMEGA, SIN mención a Raisen)

GENERAL:
  Scroll reveal animations (IntersectionObserver)
  Responsive: mobile-first
  Sin navbar (es landing autónoma)
  Custom cursor con el color primario del reseller

---

### ORDEN DE EJECUCIÓN

1. Construye /reseller/branding completo
2. Prueba guardando branding desde la UI → verifica en Railway que llega
3. Muéstrame screenshot confirmando que guarda
4. Construye /landing/:slug
5. Prueba con el slug del reseller de prueba
6. Muéstrame screenshot de la landing renderizada
7. Prueba el formulario de contacto
8. Confirma que todo funciona end-to-end

---

### REGLAS ESTRICTAS

- NO avanzar a la siguiente tarea sin confirmar la anterior
- SIEMPRE hacer publish después de cada tarea completada
- Si un endpoint da error 422 → reportar el error exacto antes de continuar
- Si algo del diseño no está claro → preguntar antes de implementar
- El diseño de OMEGA siempre: oscuro, Syne, DM Sans, oro. Sin excepciones.

