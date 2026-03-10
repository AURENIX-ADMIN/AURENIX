import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.onboarding_task import OnboardingTask


# Default onboarding checklist for every new client.
# phase: setup → integration → golive
DEFAULT_TASKS = [
    # ── Setup ────────────────────────────────────────────────────────────
    {"phase": "setup", "sort_order": 0,  "title": "VPS aprovisionado",
     "description": "Servidor Hostinger creado y acceso SSH verificado."},
    {"phase": "setup", "sort_order": 1,  "title": "Dominio y DNS configurados",
     "description": "Subdominio apuntando al VPS; registros A/CNAME propagados."},
    {"phase": "setup", "sort_order": 2,  "title": "Cloudflare Tunnel activo",
     "description": "cloudflared instalado y túnel HTTPS funcionando."},
    {"phase": "setup", "sort_order": 3,  "title": "PostgreSQL instalado",
     "description": "Base de datos creada con usuario y contraseña fuertes."},
    {"phase": "setup", "sort_order": 4,  "title": "Python 3.11+ y dependencias",
     "description": "Entorno virtual creado, requirements.txt instalado."},
    # ── Integration ──────────────────────────────────────────────────────
    {"phase": "integration", "sort_order": 10, "title": "Agente Orbit instalado",
     "description": "orbit_agent.py desplegado como servicio systemd en el VPS del cliente."},
    {"phase": "integration", "sort_order": 11, "title": "Primer heartbeat recibido",
     "description": "El agente envía señal correctamente → visible en Orbit dashboard."},
    {"phase": "integration", "sort_order": 12, "title": "n8n configurado",
     "description": "Workflows principales activados y credenciales configuradas."},
    {"phase": "integration", "sort_order": 13, "title": "Telegram Bot conectado",
     "description": "Bot responde correctamente; alertas de prueba recibidas."},
    {"phase": "integration", "sort_order": 14, "title": "API de Claude configurada",
     "description": "ANTHROPIC_API_KEY activa con crédito suficiente para el mes."},
    {"phase": "integration", "sort_order": 15, "title": "Notion workspace conectado",
     "description": "Integration token con acceso a las bases de datos necesarias."},
    # ── Go-Live ───────────────────────────────────────────────────────────
    {"phase": "golive", "sort_order": 20, "title": "Prueba end-to-end superada",
     "description": "Flujo completo ejecutado con datos reales del cliente."},
    {"phase": "golive", "sort_order": 21, "title": "Contrato y factura enviados",
     "description": "Stripe configurado o factura manual emitida."},
    {"phase": "golive", "sort_order": 22, "title": "Briefing al cliente",
     "description": "Cliente formado: qué hace el sistema, cómo interpretar alertas."},
    {"phase": "golive", "sort_order": 23, "title": "Monitoreo 48h post-lanzamiento",
     "description": "Sin alertas críticas durante las primeras 48 horas de producción."},
]


async def initialize_onboarding(db: AsyncSession, client_id: uuid.UUID) -> list[OnboardingTask]:
    """Create default onboarding tasks for a new client. Idempotent: skips if tasks already exist."""
    existing = await db.execute(
        select(OnboardingTask).where(OnboardingTask.client_id == client_id).limit(1)
    )
    if existing.scalar_one_or_none():
        return []

    tasks = [
        OnboardingTask(
            id=uuid.uuid4(),
            client_id=client_id,
            title=t["title"],
            description=t["description"],
            phase=t["phase"],
            sort_order=t["sort_order"],
        )
        for t in DEFAULT_TASKS
    ]
    db.add_all(tasks)
    await db.flush()
    return tasks


async def toggle_task(db: AsyncSession, task_id: uuid.UUID) -> OnboardingTask | None:
    result = await db.execute(select(OnboardingTask).where(OnboardingTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        return None
    task.done = not task.done
    task.completed_at = datetime.now(timezone.utc) if task.done else None
    return task


async def get_client_tasks(db: AsyncSession, client_id: uuid.UUID) -> list[OnboardingTask]:
    result = await db.execute(
        select(OnboardingTask)
        .where(OnboardingTask.client_id == client_id)
        .order_by(OnboardingTask.sort_order)
    )
    return list(result.scalars().all())
