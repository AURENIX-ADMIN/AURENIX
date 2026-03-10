"""
health_puller.py — Pulls rich metrics from each active client system every 60 minutes.
Runs as a background asyncio task started in server lifespan.
"""
import asyncio
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import AsyncSessionLocal
from src.models.system import System
from src.models.metric import SystemMetric
from src.services.alert_service import create_alert
from config.settings import get_settings

settings = get_settings()

# Claude API pricing (EUR, approximate)
HAIKU_COST_PER_1M_TOKENS = 0.35   # input+output blended
SONNET_COST_PER_1M_TOKENS = 4.50


def _calc_cost(haiku_tokens: int, sonnet_tokens: int) -> float:
    haiku = (haiku_tokens / 1_000_000) * HAIKU_COST_PER_1M_TOKENS
    sonnet = (sonnet_tokens / 1_000_000) * SONNET_COST_PER_1M_TOKENS
    return round(haiku + sonnet, 4)


async def pull_system_metrics(system: System) -> SystemMetric | None:
    """Pull metrics from a single system's /orbit/metrics endpoint."""
    if not system.base_url or not system.pull_key:
        return None

    metrics_url = system.base_url.rstrip("/") + "/orbit/metrics"

    try:
        async with httpx.AsyncClient(timeout=settings.metrics_pull_timeout_seconds) as client:
            resp = await client.get(
                metrics_url,
                headers={"X-Orbit-Key": system.pull_key},
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
    except Exception:
        return None

    claude = data.get("claude_usage", {})
    n8n = data.get("n8n_executions", {})
    custom = data.get("system_metrics", {})

    haiku_tokens = claude.get("haiku_tokens", 0)
    sonnet_tokens = claude.get("sonnet_tokens", 0)
    cost = _calc_cost(haiku_tokens, sonnet_tokens)

    return SystemMetric(
        system_id=system.id,
        claude_haiku_tokens=haiku_tokens,
        claude_sonnet_tokens=sonnet_tokens,
        claude_cost_eur=Decimal(str(cost)),
        n8n_executions_total=n8n.get("total", 0),
        n8n_executions_failed=n8n.get("failed", 0),
        custom_metrics=custom,
    )


async def run_metrics_pull():
    """Background task: pull metrics from all active systems every 60 minutes."""
    while True:
        await asyncio.sleep(settings.metrics_pull_interval_minutes * 60)
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(System).where(
                        System.is_active == True,
                        System.base_url.isnot(None),
                        System.pull_key.isnot(None),
                    )
                )
                systems = list(result.scalars().all())

                for system in systems:
                    metric = await pull_system_metrics(system)
                    if metric:
                        db.add(metric)
                        system.last_metrics_at = datetime.now(timezone.utc)

                        # Alert if Claude cost is very high this hour
                        hourly_threshold = settings.alert_claude_cost_monthly_eur / 720
                        if float(metric.claude_cost_eur) > hourly_threshold * 3:
                            await create_alert(
                                db,
                                alert_type="high_cost",
                                title=f"Coste Claude elevado en {system.name}: €{metric.claude_cost_eur}/h",
                                severity="alta",
                                system_id=system.id,
                                client_id=system.client_id,
                            )

                await db.commit()
        except Exception as e:
            print(f"[health_puller] Error: {e}")
