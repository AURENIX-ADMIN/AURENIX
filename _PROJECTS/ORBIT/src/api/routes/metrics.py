import uuid
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.database import get_db
from src.api.middleware.auth import get_current_user
from src.models.user import User
from src.models.system import System
from src.models.heartbeat import Heartbeat
from src.models.metric import SystemMetric
from src.services.cost_tracker import get_monthly_costs, get_client_monthly_summary
from src.services.n8n_client import get_n8n_summary
from config.settings import get_settings

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/costs")
async def costs_page(
    request: Request,
    month: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if month:
        try:
            month_date = datetime.strptime(month, "%Y-%m").date().replace(day=1)
        except ValueError:
            month_date = None
    else:
        month_date = None

    system_costs = await get_monthly_costs(db, month_date)
    client_summary = await get_client_monthly_summary(db, month_date)
    n8n = await get_n8n_summary()

    display_month = (month_date or date.today().replace(day=1)).strftime("%B %Y")
    current_month = date.today().strftime("%Y-%m")

    # Global totals
    total_mrr = sum(c["mrr_eur"] for c in client_summary)
    total_cost = sum(c["total_cost_eur"] for c in client_summary)
    total_margin = total_mrr - total_cost
    avg_margin_pct = (total_margin / total_mrr * 100) if total_mrr > 0 else 0

    return templates.TemplateResponse(
        "costs.html",
        {
            "request": request,
            "user": current_user,
            "system_costs": system_costs,
            "client_summary": client_summary,
            "n8n": n8n,
            "display_month": display_month,
            "current_month": current_month,
            "selected_month": month or current_month,
            "totals": {
                "mrr": total_mrr,
                "cost": total_cost,
                "margin": total_margin,
                "margin_pct": avg_margin_pct,
            },
        },
    )


@router.get("/api/systems/{system_id}/uptime")
async def system_uptime_data(
    system_id: uuid.UUID,
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns daily uptime percentage for Chart.js.
    A day is considered 'up' if > 80% of expected heartbeats arrived.
    Expected: 288 heartbeats/day (every 5 min).
    """
    from sqlalchemy import cast, Date, text
    result = await db.execute(
        select(
            cast(Heartbeat.received_at, Date).label("day"),
            func.count(Heartbeat.id).label("count"),
            func.avg(Heartbeat.cpu_pct).label("avg_cpu"),
            func.avg(Heartbeat.ram_pct).label("avg_ram"),
        )
        .where(
            Heartbeat.system_id == system_id,
            Heartbeat.received_at >= func.now() - text(f"interval '{days} days'"),
        )
        .group_by("day")
        .order_by("day")
    )
    rows = result.all()

    labels = []
    uptime_data = []
    cpu_data = []
    ram_data = []

    for row in rows:
        labels.append(row.day.strftime("%d/%m"))
        expected = 288  # heartbeats expected per day (every 5 min)
        uptime_pct = min(100, round(row.count / expected * 100, 1))
        uptime_data.append(uptime_pct)
        cpu_data.append(round(float(row.avg_cpu or 0), 1))
        ram_data.append(round(float(row.avg_ram or 0), 1))

    return {
        "labels": labels,
        "uptime": uptime_data,
        "cpu": cpu_data,
        "ram": ram_data,
    }


@router.get("/api/costs/summary")
async def costs_summary_api(
    db: AsyncSession = Depends(get_db),
    x_orbit_key: str = Header(default=""),
):
    """
    Machine-to-machine endpoint for n8n workflows.
    Returns monthly cost summary as JSON.
    Auth: X-Orbit-Key header must match INTERNAL_API_KEY env var.
    """
    settings = get_settings()
    if not settings.internal_api_key or x_orbit_key != settings.internal_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    client_summary = await get_client_monthly_summary(db, month_date=None)

    total_mrr = sum(c["mrr_eur"] for c in client_summary)
    total_cost = sum(c["total_cost_eur"] for c in client_summary)
    total_margin = total_mrr - total_cost
    margin_pct = round(total_margin / total_mrr * 100, 1) if total_mrr > 0 else 0

    return {
        "month": date.today().strftime("%Y-%m"),
        "total_mrr_eur": round(total_mrr, 2),
        "total_cost_eur": round(total_cost, 4),
        "total_margin_eur": round(total_margin, 2),
        "margin_pct": margin_pct,
        "clients": client_summary,
    }
