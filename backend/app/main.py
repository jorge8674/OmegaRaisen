"""
OmegaRaisen FastAPI Application
Main entry point for the backend API
15 AI Agents | 91 Endpoints | Enterprise Social Media Automation
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.api.routes import (
    content,
    strategy,
    analytics,
    engagement,
    monitor,
    brand_voice,
    competitive,
    trends,
    crisis,
    reports,
    growth,
    video_production,
    scheduling,
    ab_testing,
    orchestrator,
    resellers,
    auth,
    billing,
    context,
    clients,
    social_accounts,
    brand_files,
    content_lab
)

# Create FastAPI application
app = FastAPI(
    title="OmegaRaisen API",
    version="2.0.0",
    description="Social Media Automation — 15 AI Agents | Enterprise Platform",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS (must be BEFORE routes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core Agents (1-5)
app.include_router(content.router, prefix=settings.api_v1_prefix, tags=["Content Creator"])
app.include_router(strategy.router, prefix=settings.api_v1_prefix, tags=["Strategy"])
app.include_router(analytics.router, prefix=settings.api_v1_prefix, tags=["Analytics"])
app.include_router(engagement.router, prefix=settings.api_v1_prefix, tags=["Engagement"])
app.include_router(monitor.router, prefix=settings.api_v1_prefix, tags=["Monitor"])

# Intelligence Agents (6-9)
app.include_router(brand_voice.router, prefix=settings.api_v1_prefix, tags=["Brand Voice"])
app.include_router(competitive.router, prefix=settings.api_v1_prefix, tags=["Competitive Intel"])
app.include_router(trends.router, prefix=settings.api_v1_prefix, tags=["Trend Hunter"])
app.include_router(crisis.router, prefix=settings.api_v1_prefix, tags=["Crisis Manager"])

# Production Agents (10-14)
app.include_router(reports.router, prefix=settings.api_v1_prefix, tags=["Report Generator"])
app.include_router(growth.router, prefix=settings.api_v1_prefix, tags=["Growth Hacker"])
app.include_router(video_production.router, prefix=settings.api_v1_prefix, tags=["Video Production"])
app.include_router(scheduling.router, prefix=settings.api_v1_prefix, tags=["Scheduling"])
app.include_router(ab_testing.router, prefix=settings.api_v1_prefix, tags=["A/B Testing"])

# Master Orchestrator (15)
app.include_router(orchestrator.router, prefix=settings.api_v1_prefix, tags=["Orchestrator ⭐"])

# Multi-Tenant Infrastructure
app.include_router(resellers.router, prefix=settings.api_v1_prefix, tags=["Resellers 🏢"])
app.include_router(auth.router, prefix=settings.api_v1_prefix, tags=["Auth 🔐"])
app.include_router(billing.router, prefix=settings.api_v1_prefix, tags=["Billing 💳"])
app.include_router(context.router, prefix=settings.api_v1_prefix, tags=["Context 🎯"])
app.include_router(clients.router, prefix=settings.api_v1_prefix, tags=["Clients 👥"])
app.include_router(social_accounts.router, prefix=settings.api_v1_prefix, tags=["Social Accounts 📱"])
app.include_router(brand_files.router, prefix=settings.api_v1_prefix, tags=["Brand Files 📎"])
app.include_router(content_lab.router, prefix=settings.api_v1_prefix, tags=["Content Lab 🎨"])


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {
        "message": "OmegaRaisen API",
        "version": "2.0.0",
        "status": "running",
        "agents": "15/15",
        "endpoints": "91",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "agents": "15/15",
        "environment": settings.environment
    }


@app.get(f"{settings.api_v1_prefix}/status")
async def api_status() -> dict[str, str | bool]:
    """API status endpoint"""
    return {
        "api_version": "v1",
        "status": "operational",
        "debug_mode": settings.debug,
        "environment": settings.environment
    }


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.debug else "An error occurred",
            "type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
