"""
Sentinel Service - Security & Health Monitoring
Sistema inmune de OMEGA Company
Filosofía: No velocity, only precision 🐢💎
"""
import os
import time
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


class SentinelService:
    """Servicio de monitoreo de seguridad y salud del sistema"""

    def __init__(self):
        self.base_url = "https://omegaraisen-production-2031.up.railway.app/api/v1"

    def _prepare_for_insert(self, result: dict) -> dict:
        """Filter result to only include valid sentinel_scans columns"""
        valid_cols = ["agent_code", "scan_type", "status", "security_score", "issues", "deploy_decision", "triggered_by"]
        return {k: v for k, v in result.items() if k in valid_cols}

    def _calculate_score(self, issues: list) -> int:
        """Calcula score basado en issues"""
        critical = len([i for i in issues if i["severity"] == "CRITICAL"])
        high = len([i for i in issues if i["severity"] == "HIGH"])
        return max(0, 100 - (critical * 25) - (high * 10))

    def _get_status(self, score: int) -> str:
        """Determina status basado en score"""
        return "critical" if score < 70 else "warning" if score < 85 else "pass"

    async def run_vault_scan(self) -> Dict[str, Any]:
        """Detecta secrets expuestos y verifica env vars"""
        issues = []
        required_vars = ["ANTHROPIC_API_KEY", "SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "SECRET_KEY"]

        for var in required_vars:
            if not os.getenv(var):
                issues.append({"severity": "CRITICAL", "type": "MISSING_ENV_VAR", "message": f"{var} no configurada"})

        score = self._calculate_score(issues)
        return {
            "agent_code": "VAULT",
            "scan_type": "security",
            "status": self._get_status(score),
            "security_score": score,
            "issues": issues,
            "deploy_decision": "BLOCK" if score < 70 else "APPROVE"
        }

    async def run_pulse_monitor(self) -> Dict[str, Any]:
        """Health check de endpoints críticos"""
        import httpx
        endpoints = ["/health", "/agents/", "/omega/org-chart/", "/nova/data/?type=chat_history"]
        results, issues = [], []

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                for ep in endpoints:
                    start = time.time()
                    try:
                        r = await client.get(f"{self.base_url}{ep}")
                        latency = (time.time() - start) * 1000
                        status = "pass"

                        if r.status_code >= 500:
                            status = "critical"
                            issues.append({"severity": "CRITICAL", "type": "ENDPOINT_DOWN", "message": f"{ep} → {r.status_code}"})
                        elif latency > 2000:
                            status = "warning"
                            issues.append({"severity": "HIGH", "type": "SLOW_ENDPOINT", "message": f"{ep} → {latency:.0f}ms"})

                        results.append({"endpoint": ep, "status_code": r.status_code, "latency_ms": round(latency), "health": status})
                    except Exception as e:
                        issues.append({"severity": "CRITICAL", "type": "ENDPOINT_UNREACHABLE", "message": f"{ep}: {str(e)[:80]}"})
        except Exception as e:
            logger.error(f"Pulse error: {e}")

        score = max(0, 100 - len([i for i in issues if i["severity"] == "CRITICAL"]) * 20)
        return {
            "agent_code": "PULSE_MONITOR",
            "scan_type": "performance",
            "status": self._get_status(score),
            "security_score": score,
            "issues": issues,
            "details": results,
            "deploy_decision": "BLOCK" if score < 70 else "APPROVE"
        }

    async def run_db_guardian(self) -> Dict[str, Any]:
        """Verifica salud de la base de datos"""
        supabase = get_supabase_service()
        issues = []
        tables = ["omega_agents", "omega_agent_memory", "nova_data", "sentinel_scans", "resellers", "clients"]

        for table in tables:
            try:
                supabase.client.table(table).select("id").limit(1).execute()
            except:
                issues.append({"severity": "CRITICAL", "type": "MISSING_TABLE", "message": f"{table} no accesible"})

        try:
            agents = supabase.client.table("omega_agents").select("id", count="exact").execute()
            if agents.count and agents.count < 44:
                issues.append({"severity": "HIGH", "type": "DATA_INTEGRITY", "message": f"omega_agents: {agents.count} (esperados 44+)"})
        except Exception as e:
            logger.error(f"DB error: {e}")

        score = self._calculate_score(issues)
        return {
            "agent_code": "DB_GUARDIAN",
            "scan_type": "db",
            "status": self._get_status(score),
            "security_score": score,
            "issues": issues,
            "deploy_decision": "BLOCK" if score < 70 else "APPROVE"
        }

    async def run_full_scan(self) -> Dict[str, Any]:
        """Ejecuta todos los scans y calcula score global"""
        try:
            results = await asyncio.gather(self.run_vault_scan(), self.run_pulse_monitor(), self.run_db_guardian(), return_exceptions=True)
            weights = {"VAULT": 0.35, "PULSE_MONITOR": 0.35, "DB_GUARDIAN": 0.30}
            global_score, all_issues = 0, []
            supabase = get_supabase_service()

            for result in results:
                if isinstance(result, dict):
                    agent = result["agent_code"]
                    global_score += result["security_score"] * weights.get(agent, 0.33)
                    all_issues.extend(result.get("issues", []))
                    insert_data = self._prepare_for_insert({**result, "triggered_by": "cron"})
                    supabase.client.table("sentinel_scans").insert(insert_data).execute()

            global_score = round(global_score)
            status = "presidencial" if global_score >= 85 else "warning" if global_score >= 70 else "critical"
            return {
                "security_score": global_score,
                "status": status,
                "deploy_decision": "BLOCK" if global_score < 70 else "APPROVE",
                "total_issues": len(all_issues),
                "critical_issues": len([i for i in all_issues if i["severity"] == "CRITICAL"]),
                "agents_scanned": len(results)
            }
        except Exception as e:
            logger.error(f"Full scan error: {e}")
            return {"security_score": 0, "status": "critical", "deploy_decision": "BLOCK", "error": str(e)}
