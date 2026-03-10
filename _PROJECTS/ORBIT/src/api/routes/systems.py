import uuid
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.api.middleware.auth import get_current_user
from src.models.user import User
from src.models.client import Client
from src.models.system import System
from src.models.heartbeat import Heartbeat
from src.models.alert import Alert

router = APIRouter(prefix="/systems")
templates = Jinja2Templates(directory="templates")

VALID_STATUSES = {"operativo", "degradado", "caido", "en_construccion", "mantenimiento"}
VALID_TYPES = {"resona", "nexo", "asistente_personal", "ocr_facturas", "custom"}


@router.get("/new")
async def new_system_form(
    request: Request,
    client_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    clients_result = await db.execute(select(Client).where(Client.is_active == True).order_by(Client.name))
    clients = list(clients_result.scalars().all())
    return templates.TemplateResponse(
        "system_form.html",
        {"request": request, "system": None, "clients": clients, "selected_client_id": client_id, "user": current_user},
    )


@router.post("/new")
async def create_system(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    form = await request.form()
    client_id = uuid.UUID(form.get("client_id"))
    name = form.get("name", "").strip()
    system_type = form.get("system_type", "custom")
    base_url = form.get("base_url", "").strip() or None
    notes = form.get("notes", "").strip() or None

    if not name:
        raise HTTPException(status_code=422, detail="Nombre obligatorio")
    if system_type not in VALID_TYPES:
        raise HTTPException(status_code=422, detail="Tipo de sistema invalido")

    system = System(
        id=uuid.uuid4(),
        client_id=client_id,
        name=name,
        system_type=system_type,
        status="en_construccion",
        base_url=base_url,
        notes=notes,
    )
    db.add(system)
    await db.commit()
    return RedirectResponse(url=f"/clients/{client_id}", status_code=303)


@router.get("/{system_id}")
async def system_detail(
    request: Request,
    system_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(System).where(System.id == system_id))
    system = result.scalar_one_or_none()
    if not system:
        raise HTTPException(status_code=404, detail="Sistema no encontrado")

    # Last 48 heartbeats
    hb_result = await db.execute(
        select(Heartbeat)
        .where(Heartbeat.system_id == system_id)
        .order_by(Heartbeat.received_at.desc())
        .limit(48)
    )
    heartbeats = list(hb_result.scalars().all())

    alerts_result = await db.execute(
        select(Alert)
        .where(Alert.system_id == system_id)
        .order_by(Alert.created_at.desc())
        .limit(20)
    )
    alerts = list(alerts_result.scalars().all())

    return templates.TemplateResponse(
        "system_detail.html",
        {"request": request, "system": system, "heartbeats": heartbeats, "alerts": alerts, "user": current_user},
    )


@router.post("/{system_id}/status")
async def update_system_status(
    system_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    form = await request.form()
    new_status = form.get("status", "")
    if new_status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Estado invalido")

    result = await db.execute(select(System).where(System.id == system_id))
    system = result.scalar_one_or_none()
    if not system:
        raise HTTPException(status_code=404)

    system.status = new_status
    await db.commit()
    return RedirectResponse(url=f"/systems/{system_id}", status_code=303)
