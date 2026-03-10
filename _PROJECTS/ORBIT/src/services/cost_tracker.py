"""
cost_tracker.py — Aggregates monthly costs per system from system_metrics.
Called on demand from the costs route.
"""
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.system import System
from src.models.client import Client
from src.models.metric import SystemMetric
from src.models.cost_record import CostRecord

HAIKU_COST_PER_1M = Decimal("0.35")
SONNET_COST_PER_1M = Decimal("4.50")


def _month_start(d: date | None = None) -> date:
    d = d or date.today()
    return d.replace(day=1)


async def get_monthly_costs(db: AsyncSession, month: date | None = None) -> list[dict]:
    """
    Returns a list of dicts with cost breakdown per system for the given month.
    Aggregates from system_metrics rows collected during that month.
    """
    month_start = _month_start(month)
    month_end = date(
        month_start.year + (month_start.month // 12),
        (month_start.month % 12) + 1,
        1,
    ) if month_start.month < 12 else date(month_start.year + 1, 1, 1)

    # Get all systems with their clients
    systems_result = await db.execute(
        select(System, Client)
        .join(Client, System.client_id == Client.id)
        .where(System.is_active == True)
    )
    rows = systems_result.all()

    results = []
    for system, client in rows:
        # Aggregate metrics for this month
        agg_result = await db.execute(
            select(
                func.sum(SystemMetric.claude_haiku_tokens).label("haiku_tokens"),
                func.sum(SystemMetric.claude_sonnet_tokens).label("sonnet_tokens"),
                func.count(SystemMetric.id).label("samples"),
            ).where(
                SystemMetric.system_id == system.id,
                SystemMetric.collected_at >= datetime(month_start.year, month_start.month, 1, tzinfo=timezone.utc),
                SystemMetric.collected_at < datetime(month_end.year, month_end.month, 1, tzinfo=timezone.utc),
            )
        )
        agg = agg_result.one()

        haiku_tokens = agg.haiku_tokens or 0
        sonnet_tokens = agg.sonnet_tokens or 0
        haiku_eur = (Decimal(haiku_tokens) / 1_000_000) * HAIKU_COST_PER_1M
        sonnet_eur = (Decimal(sonnet_tokens) / 1_000_000) * SONNET_COST_PER_1M
        claude_total = haiku_eur + sonnet_eur
        vps_share = client.vps_cost_eur  # simplification: full VPS per system
        total_cost = claude_total + vps_share
        mrr = client.mrr_eur
        margin = mrr - total_cost
        margin_pct = (margin / mrr * 100) if mrr > 0 else Decimal("0")

        results.append({
            "system_id": system.id,
            "system_name": system.name,
            "system_type": system.system_type,
            "client_id": client.id,
            "client_name": client.name,
            "haiku_tokens": haiku_tokens,
            "sonnet_tokens": sonnet_tokens,
            "haiku_eur": float(haiku_eur),
            "sonnet_eur": float(sonnet_eur),
            "claude_total_eur": float(claude_total),
            "vps_eur": float(vps_share),
            "total_cost_eur": float(total_cost),
            "mrr_eur": float(mrr),
            "margin_eur": float(margin),
            "margin_pct": float(margin_pct),
            "samples": agg.samples or 0,
        })

    return results


async def get_client_monthly_summary(db: AsyncSession, month: date | None = None) -> list[dict]:
    """Aggregate costs per client (sum of all their systems)."""
    system_costs = await get_monthly_costs(db, month)

    clients: dict[uuid.UUID, dict] = {}
    for row in system_costs:
        cid = row["client_id"]
        if cid not in clients:
            clients[cid] = {
                "client_id": cid,
                "client_name": row["client_name"],
                "mrr_eur": row["mrr_eur"],
                "total_cost_eur": 0.0,
                "claude_total_eur": 0.0,
                "margin_eur": 0.0,
                "systems": 0,
            }
        clients[cid]["total_cost_eur"] += row["total_cost_eur"]
        clients[cid]["claude_total_eur"] += row["claude_total_eur"]
        clients[cid]["systems"] += 1

    for c in clients.values():
        c["margin_eur"] = c["mrr_eur"] - c["total_cost_eur"]
        c["margin_pct"] = (c["margin_eur"] / c["mrr_eur"] * 100) if c["mrr_eur"] > 0 else 0.0

    return list(clients.values())
