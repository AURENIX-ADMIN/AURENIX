import uuid
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.api.middleware.auth import get_current_user
from src.models.user import User
from src.models.alert import Alert
from src.services.alert_service import acknowledge_alert, resolve_alert, silence_alert, get_open_alerts

router = APIRouter(prefix="/alerts")
templates = Jinja2Templates(directory="templates")


@router.get("")
async def alerts_page(
    request: Request,
    severity: str | None = None,
    status_filter: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Alert).order_by(Alert.created_at.desc()).limit(100)
    filters = []
    if severity:
        filters.append(Alert.severity == severity)
    if status_filter:
        filters.append(Alert.status == status_filter)
    else:
        filters.append(Alert.status.in_(["open", "acknowledged"]))
    if filters:
        query = query.where(*filters)

    result = await db.execute(query)
    alerts = list(result.scalars().all())

    return templates.TemplateResponse(
        "alerts.html",
        {"request": request, "alerts": alerts, "user": current_user, "severity": severity, "status_filter": status_filter},
    )


@router.post("/{alert_id}/acknowledge")
async def ack_alert(
    alert_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = await acknowledge_alert(db, alert_id, current_user.id)
    if not alert:
        raise HTTPException(status_code=404)
    await db.commit()
    return RedirectResponse(url="/alerts", status_code=303)


@router.post("/{alert_id}/resolve")
async def resolve(
    alert_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = await resolve_alert(db, alert_id, current_user.id)
    if not alert:
        raise HTTPException(status_code=404)
    await db.commit()
    return RedirectResponse(url="/alerts", status_code=303)


@router.post("/{alert_id}/silence")
async def silence(
    alert_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    form = await request.form()
    hours = int(form.get("hours", 2))
    until = datetime.now(timezone.utc) + timedelta(hours=hours)
    alert = await silence_alert(db, alert_id, until)
    if not alert:
        raise HTTPException(status_code=404)
    await db.commit()
    return RedirectResponse(url="/alerts", status_code=303)


@router.get("/api/open")
async def api_open_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """JSON endpoint for HTMX polling."""
    alerts = await get_open_alerts(db)
    return [
        {
            "id": str(a.id),
            "severity": a.severity,
            "title": a.title,
            "status": a.status,
            "created_at": a.created_at.isoformat(),
        }
        for a in alerts
    ]
