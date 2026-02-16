"""
Context Main Router
Registers all context sub-routers under /context prefix
"""
from fastapi import APIRouter
import logging

# Import sub-routers
from app.api.routes.context import (
    create,
    read,
    update,
)

# Create main router
router = APIRouter(prefix="/context", tags=["context"])

# Configure logging
logger = logging.getLogger(__name__)

# Register sub-routers
router.include_router(create.router, tags=["context-create"])
router.include_router(read.router, tags=["context-read"])
router.include_router(update.router, tags=["context-update"])

logger.info("Context routers registered successfully")
