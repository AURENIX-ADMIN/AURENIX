import uuid
import re
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.api.middleware.auth import get_current_user
from src.models.user import User
from src.models.client import Client
from src.models.system import System
from src.models.alert import Alert
from src.services.onboarding_service import initialize_onboarding, toggle_task, get_client_tasks

router = APIRouter(prefix="/clients")
templates = Jinja2Templates(directory="templates")


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    return s[:100]


@router.get("")
async def list_clients(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Client).where(Client.is_active == True).order_by(Client.name)
    )
    clients = list(result.scalars().all())
    return templates.TemplateResponse("clients.html", {"request": request, "clients": clients, "user": current_user})


@router.get("/new")
async def new_client_form(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse("client_form.html", {"request": request, "client": None, "user": current_user})


@router.post("/new")
async def create_client(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    form = await request.form()
    name = form.get("name", "").strip()
    plan = form.get("plan", "basic")
    mrr = float(form.get("mrr_eur", 0) or 0)
    vps_cost = float(form.get("vps_cost_eur", 0) or 0)
    contact_email = form.get("contact_email", "").strip() or None
    contact_name = form.get("contact_name", "").strip() or None
    notes = form.get("notes", "").strip() or None
    started_at = form.get("started_at") or None

    if not name:
        return templates.TemplateResponse(
            "client_form.html",
            {"request": request, "client": None, "error": "El nombre es obligatorio", "user": current_user},
            status_code=422,
        )

    slug = slugify(name)
    # Ensure slug uniqueness
    existing = await db.execute(select(Client).where(Client.slug == slug))
    if existing.scalar_one_or_none():
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"

    client = Client(
        id=uuid.uuid4(),
        name=name,
        slug=slug,
        plan=plan,
        mrr_eur=mrr,
        vps_cost_eur=vps_cost,
        contact_email=contact_email,
        contact_name=contact_name,
        notes=notes,
        started_at=started_at,
    )
    db.add(client)
    await db.flush()
    await initialize_onboarding(db, client.id)
    await db.commit()
    return RedirectResponse(url=f"/clients/{client.id}", status_code=303)


@router.get("/{client_id}")
async def client_detail(
    request: Request,
    client_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    alerts_result = await db.execute(
        select(Alert)
        .where(Alert.client_id == client_id, Alert.status.in_(["open", "acknowledged"]))
        .order_by(Alert.created_at.desc())
        .limit(10)
    )
    alerts = list(alerts_result.scalars().all())

    tasks = await get_client_tasks(db, client_id)
    # Group tasks by phase
    onboarding = {
        "setup":       [t for t in tasks if t.phase == "setup"],
        "integration": [t for t in tasks if t.phase == "integration"],
        "golive":      [t for t in tasks if t.phase == "golive"],
    }
    total = len(tasks)
    done = sum(1 for t in tasks if t.done)
    progress_pct = round(done / total * 100) if total else 0

    return templates.TemplateResponse(
        "client_detail.html",
        {
            "request": request,
            "client": client,
            "alerts": alerts,
            "user": current_user,
            "onboarding": onboarding,
            "onboarding_progress": {"total": total, "done": done, "pct": progress_pct},
        },
    )


@router.post("/{client_id}/onboarding/init")
async def init_onboarding(
    client_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Initialize onboarding checklist for a client that was created before Phase 3."""
    result = await db.execute(select(Client).where(Client.id == client_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404)
    await initialize_onboarding(db, client_id)
    await db.commit()
    return RedirectResponse(url=f"/clients/{client_id}", status_code=303)


@router.post("/{client_id}/onboarding/{task_id}/toggle")
async def toggle_onboarding_task(
    client_id: uuid.UUID,
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await toggle_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404)
    await db.commit()
    return JSONResponse({"done": task.done})


@router.post("/{client_id}/deactivate")
async def deactivate_client(
    client_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404)
    client.is_active = False
    await db.commit()
    return RedirectResponse(url="/", status_code=303)
