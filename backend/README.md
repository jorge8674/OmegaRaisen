# OmegaRaisen Backend

Backend Python con FastAPI para el sistema de automatización de redes sociales.

## Instalación

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## Configuración

1. Copiar `.env.example` a `.env`:
```bash
cp .env.example .env
```

2. Configurar variables de entorno en `.env`:
- `OPENAI_API_KEY`: Tu API key de OpenAI
- `DATABASE_URL`: URL de PostgreSQL
- Otras configuraciones necesarias

## Ejecutar

```bash
# Desarrollo (con auto-reload)
uvicorn app.main:app --reload

# Producción
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

El servidor estará disponible en `http://localhost:8000`

## Documentación API

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints Disponibles

### Health Check
- `GET /health` - Estado del servidor

### Content Generation (API v1)
- `POST /api/v1/content/generate-caption` - Generar caption
- `POST /api/v1/content/generate-image` - Generar imagen
- `POST /api/v1/content/generate-hashtags` - Generar hashtags
- `POST /api/v1/content/generate-video-script` - Generar script de video
- `GET /api/v1/content/agent-status` - Estado del agente

## Estructura

```
backend/
├── app/
│   ├── agents/              # Agentes IA
│   │   ├── base_agent.py
│   │   └── content_creator.py
│   ├── api/                 # Endpoints REST
│   │   └── routes/
│   │       └── content.py
│   ├── infrastructure/      # Servicios externos
│   │   └── ai/
│   │       └── openai_service.py
│   ├── config.py           # Configuración
│   └── main.py             # App principal
├── requirements.txt
└── .env.example
```

## Testing

```bash
pytest
```
