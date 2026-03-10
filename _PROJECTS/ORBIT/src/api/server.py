import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy import select

from config.settings import get_settings
from src.database import AsyncSessionLocal, engine
from src.models import Base
from src.models.client import Client
from src.models.system import System
from src.models.alert import Alert
from src.api.routes import auth, clients, systems, heartbeat, alerts, metrics
from src.api.middleware.auth import get_current_user
from src.services.alert_service import create_alert
from src.services.health_puller import run_metrics_pull

settings = get_settings()


async def heartbeat_watcher():
    """
    Background job: runs every 60 seconds.
    Checks all active systems for missing heartbeats and fires alerts.
    """
    threshold = timedelta(minutes=settings.heartbeat_alert_after_minutes)
    while True:
        await asyncio.sleep(60)
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(System).where(System.is_active == True, System.status != "en_construccion")
                )
                systems_list = list(result.scalars().all())
                now = datetime.now(timezone.utc)
                for system in systems_list:
                    if system.last_heartbeat_at is None:
                        continue
                    age = now - system.last_heartbeat_at
                    if age > threshold:
                        await create_alert(
                            db,
                            alert_type="heartbeat_lost",
                            title=f"Heartbeat perdido: {system.name}",
                            severity="critica",
                            description=f"Sin heartbeat desde hace {int(age.total_seconds() / 60)} minutos.",
                            system_id=system.id,
                            client_id=system.client_id,
                        )
                        if system.status != "caido":
                            system.status = "caido"
                await db.commit()
        except Exception as e:
            print(f"[heartbeat_watcher] Error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB tables on startup (idempotent)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Start background tasks
    watcher_task = asyncio.create_task(heartbeat_watcher())
    puller_task = asyncio.create_task(run_metrics_pull())
    yield
    for task in [watcher_task, puller_task]:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Orbit — AURENIX Control Dashboard",
    docs_url=None,  # Disable Swagger in production
    redoc_url=None,
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Register routers
app.include_router(auth.router, tags=["auth"])
app.include_router(clients.router, tags=["clients"])
app.include_router(systems.router, tags=["systems"])
app.include_router(heartbeat.router, tags=["heartbeat"])
app.include_router(alerts.router, tags=["alerts"])
app.include_router(metrics.router, tags=["metrics"])


@app.get("/api/vps/metrics")
async def vps_metrics(current_user=Depends(get_current_user)):
    """
    Return current VPS health metrics from Hostinger API.
    Requires HOSTINGER_API_TOKEN in .env.
    """
    from src.services.hostinger_service import get_vps_metrics
    from dataclasses import asdict

    if not settings.hostinger_api_token:
        return {"error": "HOSTINGER_API_TOKEN not configured", "available": False}

    snapshot = await get_vps_metrics(settings.hostinger_api_token, settings.hostinger_vps_id)
    if not snapshot:
        return {"error": "Failed to fetch VPS metrics", "available": False}

    return {"available": True, **asdict(snapshot)}


@app.get("/api/vps/status")
async def vps_status(current_user=Depends(get_current_user)):
    """Quick VPS health summary with alert flags."""
    from src.services.hostinger_service import get_vps_metrics
    from dataclasses import asdict

    if not settings.hostinger_api_token:
        return {"available": False}

    snapshot = await get_vps_metrics(settings.hostinger_api_token, settings.hostinger_vps_id)
    if not snapshot:
        return {"available": False}

    return {
        "available": True,
        "state": snapshot.state,
        "cpu_pct": snapshot.cpu_pct,
        "ram_pct": snapshot.ram_pct,
        "disk_pct": snapshot.disk_pct,
        "uptime_human": snapshot.uptime_human,
        "alerts": {
            "cpu_high": snapshot.cpu_avg_2h > settings.alert_cpu_threshold_pct,
            "ram_high": snapshot.ram_pct > settings.alert_ram_threshold_pct,
            "disk_high": snapshot.disk_pct > settings.alert_disk_threshold_pct,
        },
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "orbit"}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    # Redirect to login if no session
    token = request.cookies.get("orbit_session")
    if not token:
        return RedirectResponse(url="/login")

    from src.services.auth_service import decode_token
    payload = decode_token(token)
    if not payload:
        return RedirectResponse(url="/login")

    clients_result = await db.execute(
        select(Client).where(Client.is_active == True).order_by(Client.name)
    )
    all_clients = list(clients_result.scalars().all())

    systems_result = await db.execute(
        select(System).where(System.is_active == True)
    )
    all_systems = list(systems_result.scalars().all())

    alerts_result = await db.execute(
        select(Alert)
        .where(Alert.status.in_(["open", "acknowledged"]))
        .order_by(Alert.created_at.desc())
        .limit(20)
    )
    open_alerts = list(alerts_result.scalars().all())

    # Serialize to plain dicts to avoid detached instance issues
    clients_data = [
        {
            "id": c.id,
            "name": c.name,
            "plan": c.plan,
            "mrr_eur": float(c.mrr_eur),
            "started_at": c.started_at,
        }
        for c in all_clients
    ]
    systems_data = [
        {
            "id": s.id,
            "client_id": s.client_id,
            "name": s.name,
            "system_type": s.system_type,
            "status": s.status,
            "last_heartbeat_at": s.last_heartbeat_at,
        }
        for s in all_systems
    ]
    alerts_data = [
        {
            "id": a.id,
            "severity": a.severity,
            "title": a.title,
            "status": a.status,
            "created_at": a.created_at,
        }
        for a in open_alerts
    ]

    total_systems = len(systems_data)
    operational = sum(1 for s in systems_data if s["status"] == "operativo")
    down = sum(1 for s in systems_data if s["status"] == "caido")
    total_mrr = sum(c["mrr_eur"] for c in clients_data)
    critical_alerts = sum(1 for a in alerts_data if a["severity"] == "critica")

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "clients": clients_data,
            "systems": systems_data,
            "open_alerts": alerts_data,
            "stats": {
                "total_clients": len(clients_data),
                "total_systems": total_systems,
                "operational": operational,
                "down": down,
                "total_mrr": total_mrr,
                "critical_alerts": critical_alerts,
            },
        },
    )
