# 🚀 OmegaRaisen - Sistema de Automatización de Redes Sociales Enterprise

> Sistema enterprise autónomo de gestión multi-cliente de redes sociales con arquitectura multi-agente y capacidades de auto-aprendizaje continuo.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)

---

## 📋 Tabla de Contenidos

- [Visión General](#visión-general)
- [Características Principales](#características-principales)
- [Arquitectura](#arquitectura)
- [Instalación](#instalación)
- [Uso](#uso)
- [Desarrollo](#desarrollo)
- [Documentación](#documentación)
- [Contribución](#contribución)

---

## 🎯 Visión General

**OmegaRaisen** es un sistema de automatización de redes sociales de nivel enterprise que combina:

- **15 Agentes IA Especializados** trabajando en paralelo
- **Generación de Contenido Multimedia** (texto, imagen, video)
- **Análisis Competitivo Automatizado**
- **Auto-Aprendizaje Continuo**
- **Integración con APIs Oficiales** (Instagram, Facebook, TikTok, Twitter)

### Capacidades Core

✅ **Generación de Video** (15-120 segundos) con Runway ML, Pika, Sora  
✅ **Generación de Imágenes** con DALL-E 3, Midjourney, Stable Diffusion  
✅ **Generación de Texto** con GPT-4, Claude, Gemini  
✅ **Respuestas Inteligentes** contextuales y personalizadas  
✅ **Programación Automatizada** con optimización de timing  
✅ **Analytics en Tiempo Real** con predicción de engagement  
✅ **Web Scraping** de competidores y tendencias  

---

## 🏗️ Arquitectura

### Stack Tecnológico

**Frontend**:
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS + shadcn/ui
- React Query (data fetching)
- Supabase (auth + database)

**Backend**:
- FastAPI (Python 3.11+)
- PostgreSQL (base de datos principal)
- Redis (cache + message queue)
- MongoDB (documentos)
- Pinecone (vector database para embeddings)

**IA/ML**:
- OpenAI (GPT-4, DALL-E 3)
- Anthropic (Claude Opus/Sonnet)
- Runway ML (generación de video)
- LangChain + LangGraph (orquestación de agentes)
- AutoGen (multi-agente framework)

**DevOps**:
- Docker + Docker Compose
- GitHub Actions (CI/CD)
- Prometheus + Grafana (monitoreo)
- ELK Stack (logging)

### Arquitectura Multi-Agente

El sistema implementa **15 agentes especializados**:

1. **Content Creator Agent** - Generación de contenido multimedia
2. **Strategy Agent** - Planificación estratégica
3. **Analytics Agent** - Análisis de datos e insights
4. **Engagement Agent** - Interacción con usuarios
5. **Monitor Agent** - Vigilancia del sistema
6. **Competitive Intelligence Agent** - Análisis de competencia
7. **Trend Hunter Agent** - Detección de tendencias
8. **Brand Voice Agent** - Consistencia de marca
9. **Crisis Manager Agent** - Gestión de crisis
10. **Growth Hacker Agent** - Optimización de crecimiento
11. **Report Generator Agent** - Reportes automatizados
12. **Defense Agent** - Seguridad y protección
13. **Scheduler Agent** - Optimización de calendario
14. **Media Processor Agent** - Procesamiento de medios
15. **Approval Agent** - Supervisión humana

---

## 🚀 Instalación

### Prerrequisitos

- Node.js 18+ y npm
- Python 3.11+
- Docker y Docker Compose (opcional pero recomendado)
- Git

### Instalación Rápida con Docker

```bash
# Clonar repositorio
git clone https://github.com/jorge8674/OmegaRaisen.git
cd OmegaRaisen

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# Ejecutar con Docker
docker-compose up --build
```

El frontend estará disponible en `http://localhost:5173`  
El backend estará disponible en `http://localhost:8000`

### Instalación Manual

#### Frontend

```bash
# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev
```

#### Backend

```bash
# Crear entorno virtual
cd backend
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
uvicorn app.main:app --reload
```

---

## 💻 Uso

### Generación de Contenido

```typescript
// Generar video
const video = await apiClient.generateVideo({
  prompt: "Un perro jugando en la playa al atardecer",
  duration: 30,
  style: "realistic",
  aspectRatio: "16:9"
});

// Generar imagen
const image = await apiClient.generateImage({
  prompt: "Logo minimalista de startup tech",
  size: "1024x1024",
  style: "professional"
});

// Generar texto
const caption = await apiClient.generateCaption({
  topic: "lanzamiento de producto",
  tone: "excited",
  platform: "instagram"
});
```

### Programación de Posts

```typescript
// Programar publicación
const scheduled = await apiClient.schedulePost({
  accountId: "acc_123",
  platform: "instagram",
  content: {
    caption: "🚀 ¡Nuevo producto!",
    mediaUrls: ["https://..."],
    hashtags: ["#ProductLaunch"]
  },
  scheduledTime: "2026-02-15T10:00:00Z"
});
```

---

## 🛠️ Desarrollo

### Estructura del Proyecto

```
OmegaRaisen/
├── backend/                 # Backend Python (FastAPI)
│   ├── app/
│   │   ├── agents/         # 15 Agentes IA
│   │   ├── api/            # Endpoints REST
│   │   ├── domain/         # Lógica de dominio (DDD)
│   │   ├── infrastructure/ # Servicios externos
│   │   └── main.py         # App principal
│   └── requirements.txt
├── src/                     # Frontend React
│   ├── components/         # Componentes UI
│   ├── pages/              # Páginas
│   ├── hooks/              # Custom hooks
│   └── lib/                # Utilidades
├── docs/                    # Documentación
├── docker-compose.yml
└── README_OMEGA.md
```

### Reglas de Desarrollo

⚠️ **Reglas No Negociables**:

1. ✅ **Máximo 200 líneas por archivo** - Sin excepciones
2. ✅ **Zero tipos `any`** en TypeScript - Usar tipos específicos
3. ✅ **Arquitectura DDD** - Separación estricta de capas
4. ✅ **Inmutabilidad** - No mutar estado directamente
5. ✅ **Funciones Puras** - Aislar efectos secundarios
6. ✅ **Tests** - Cobertura mínima 80%

### Ejecutar Tests

```bash
# Frontend
npm run test

# Backend
cd backend
pytest
```

---

## 📚 Documentación

- [Master Sistema Redes](./Master_Sistema_Redes.md) - Arquitectura completa
- [Estrategia Híbrida](./ESTRATEGIA_HIBRIDA.md) - Plan de implementación
- [Prompt Master Agent](./PROMPT_MASTER_AGENT.md) - Instrucciones para agentes
- [API Documentation](./docs/api.md) - Documentación de endpoints

---

## 🔐 Seguridad

- **Autenticación**: JWT con refresh tokens
- **Autorización**: RBAC (Role-Based Access Control)
- **Encriptación**: Datos sensibles encriptados en reposo
- **Rate Limiting**: Protección contra abuso
- **Secrets Management**: Variables de entorno seguras

⚠️ **NUNCA** commitear archivos `.env` o API keys

---

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

---

## 👥 Equipo

- **Arquitectura**: Sistema de Arquitectura IA
- **Desarrollo**: [Tu Nombre]
- **Repositorio**: https://github.com/jorge8674/OmegaRaisen

---

## 🙏 Agradecimientos

- OpenAI por GPT-4 y DALL-E 3
- Anthropic por Claude
- Runway ML por generación de video
- Comunidad open source

---

**¿Preguntas?** Abre un issue en GitHub o contacta al equipo.

**OmegaRaisen** - Automatización de Redes Sociales del Futuro 🚀
