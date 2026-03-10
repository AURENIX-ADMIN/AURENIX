"""
n8n_client.py — Reads workflow and execution status from the local n8n instance.
"""
import httpx
from config.settings import get_settings

settings = get_settings()


async def get_workflows() -> list[dict]:
    """Returns active workflows from n8n."""
    if not settings.n8n_api_key:
        return []
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                f"{settings.n8n_base_url}/api/v1/workflows",
                headers={"X-N8N-API-KEY": settings.n8n_api_key},
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
            return data.get("data", [])
    except Exception:
        return []


async def get_recent_executions(limit: int = 20) -> list[dict]:
    """Returns recent workflow executions."""
    if not settings.n8n_api_key:
        return []
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                f"{settings.n8n_base_url}/api/v1/executions",
                headers={"X-N8N-API-KEY": settings.n8n_api_key},
                params={"limit": limit},
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
            return data.get("data", [])
    except Exception:
        return []


async def get_n8n_summary() -> dict:
    """Returns a summary dict for dashboard display."""
    workflows = await get_workflows()
    executions = await get_recent_executions(50)

    active = sum(1 for w in workflows if w.get("active"))
    total = len(workflows)
    failed = sum(1 for e in executions if e.get("status") == "error")
    success = sum(1 for e in executions if e.get("status") == "success")

    return {
        "connected": bool(settings.n8n_api_key),
        "total_workflows": total,
        "active_workflows": active,
        "recent_executions": len(executions),
        "failed_executions": failed,
        "success_executions": success,
        "error_rate_pct": round(failed / len(executions) * 100, 1) if executions else 0,
        "workflows": workflows[:10],
        "executions": executions[:10],
    }
