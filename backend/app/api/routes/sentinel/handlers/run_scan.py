"""
Handler: Run Security Scan
Ejecuta scans de seguridad y guarda resultados
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
from pydantic import BaseModel
import logging

from app.services.sentinel_service import SentinelService

logger = logging.getLogger(__name__)


class ScanRequest(BaseModel):
    scan_type: str  # "vault" | "pulse" | "db" | "full"


async def handle_run_scan(request: ScanRequest) -> Dict[str, Any]:
    """
    Execute security scan

    Args:
        request: ScanRequest with scan_type

    Returns:
        Dict with scan results

    Raises:
        HTTPException 400: Invalid scan type
        HTTPException 500: Scan execution error
    """
    try:
        sentinel = SentinelService()

        # Validate scan type
        valid_types = ["vault", "pulse", "db", "full"]
        if request.scan_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid scan_type. Must be one of: {valid_types}"
            )

        logger.info(f"Running {request.scan_type} scan...")

        # Execute appropriate scan
        if request.scan_type == "vault":
            result = await sentinel.run_vault_scan()
        elif request.scan_type == "pulse":
            result = await sentinel.run_pulse_monitor()
        elif request.scan_type == "db":
            result = await sentinel.run_db_guardian()
        elif request.scan_type == "full":
            result = await sentinel.run_full_scan()
        else:
            raise HTTPException(status_code=400, detail="Invalid scan type")

        # Save to database if not full scan (full scan saves internally)
        if request.scan_type != "full":
            from app.infrastructure.supabase_service import get_supabase_service
            supabase = get_supabase_service()
            # Filter to valid columns only
            valid_cols = ["agent_code", "scan_type", "status", "security_score", "issues", "deploy_decision"]
            insert_data = {k: v for k, v in result.items() if k in valid_cols}
            insert_data["triggered_by"] = "manual"
            supabase.client.table("sentinel_scans").insert(insert_data).execute()

        logger.info(f"{request.scan_type} scan completed: score={result.get('security_score', 0)}")

        return {
            "success": True,
            "scan_type": request.scan_type,
            "result": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running scan: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run scan: {str(e)}"
        )
