import uuid
import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request, HTTPException, status, Header
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.models.system import System
from src.models.agent_token import AgentToken
from src.models.heartbeat import Heartbeat
from src.models.client import Client
from src.services.hmac_service import verify_hmac_signature, _hash_token
from src.services.alert_service import create_alert

router = APIRouter()


class ServiceStatus(BaseModel):
    up: bool
    response_ms: float | None = None


class SystemMetrics(BaseModel):
    cpu_pct: float | None = None
    ram_pct: float | None = None
    disk_pct: float | None = None


class HeartbeatPayload(BaseModel):
    status: str  # healthy | degraded | critical
    services: dict[str, dict] = {}
    system: SystemMetrics = SystemMetrics()
    agent_version: str = "unknown"


@router.post("/heartbeat")
async def receive_heartbeat(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_client_id: str = Header(..., alias="X-Client-ID"),
    x_timestamp: str = Header(..., alias="X-Timestamp"),
    x_signature: str = Header(..., alias="X-Signature"),
    x_system_id: str = Header(..., alias="X-System-ID"),
):
    body = await request.body()

    # Resolve the client and find a matching active token
    try:
        client_uuid = uuid.UUID(x_client_id)
        system_uuid = uuid.UUID(x_system_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="IDs invalidos")

    tokens_result = await db.execute(
        select(AgentToken).where(
            AgentToken.client_id == client_uuid,
            AgentToken.is_active == True,
        )
    )
    tokens = list(tokens_result.scalars().all())
    if not tokens:
        raise HTTPException(status_code=401, detail="Sin tokens validos para este cliente")

    # Try each active token (allows rotation without downtime)
    verified_token = None
    for token_record in tokens:
        # We cannot reverse the hash, so the agent must send the raw token
        # in a separate header for HMAC computation — we verify by computing
        # HMAC with the raw token sent by the agent.
        # The raw token is sent as X-Agent-Token header (only over HTTPS/Cloudflare).
        pass

    # Simpler and equally secure approach: agent sends raw token in X-Agent-Token,
    # we hash it to find the record, then verify HMAC.
    x_agent_token = request.headers.get("X-Agent-Token", "")
    if not x_agent_token:
        raise HTTPException(status_code=401, detail="Token de agente requerido")

    token_hash = _hash_token(x_agent_token)
    token_result = await db.execute(
        select(AgentToken).where(
            AgentToken.client_id == client_uuid,
            AgentToken.token_hash == token_hash,
            AgentToken.is_active == True,
        )
    )
    token_record = token_result.scalar_one_or_none()
    if not token_record:
        raise HTTPException(status_code=401, detail="Token invalido")

    # Verify HMAC signature
    if not verify_hmac_signature(x_client_id, x_timestamp, x_signature, body, x_agent_token):
        raise HTTPException(status_code=401, detail="Firma invalida o timestamp expirado")

    # Find the system
    system_result = await db.execute(
        select(System).where(System.id == system_uuid, System.client_id == client_uuid)
    )
    system = system_result.scalar_one_or_none()
    if not system:
        raise HTTPException(status_code=404, detail="Sistema no encontrado")

    # Parse payload
    import json
    try:
        payload_data = json.loads(body)
        payload = HeartbeatPayload(**payload_data)
    except Exception:
        raise HTTPException(status_code=422, detail="Payload invalido")

    services = payload.services
    sys_metrics = payload.system

    # Save heartbeat
    hb = Heartbeat(
        system_id=system_uuid,
        agent_status=payload.status,
        fastapi_up=services.get("fastapi", {}).get("up"),
        n8n_up=services.get("n8n", {}).get("up"),
        postgresql_up=services.get("postgresql", {}).get("up"),
        telegram_bot_up=services.get("telegram_bot", {}).get("up"),
        cpu_pct=sys_metrics.cpu_pct,
        ram_pct=sys_metrics.ram_pct,
        disk_pct=sys_metrics.disk_pct,
        agent_version=payload.agent_version,
        raw_payload=payload_data,
    )
    db.add(hb)

    # Update system last_heartbeat and status based on agent report
    system.last_heartbeat_at = datetime.now(timezone.utc)
    if payload.status == "healthy" and system.status == "caido":
        system.status = "operativo"
    elif payload.status == "critical":
        system.status = "caido"
    elif payload.status == "degraded" and system.status == "operativo":
        system.status = "degradado"

    # Update token last_used
    token_record.last_used_at = datetime.now(timezone.utc)

    # Check thresholds and raise alerts
    from config.settings import get_settings
    cfg = get_settings()

    if sys_metrics.cpu_pct and sys_metrics.cpu_pct > cfg.alert_cpu_threshold_pct:
        await create_alert(
            db,
            alert_type="high_cpu",
            title=f"CPU alta en {system.name}: {sys_metrics.cpu_pct:.1f}%",
            severity="media",
            system_id=system_uuid,
            client_id=client_uuid,
        )
    if sys_metrics.disk_pct and sys_metrics.disk_pct > cfg.alert_disk_threshold_pct:
        await create_alert(
            db,
            alert_type="disk_warning",
            title=f"Disco lleno en {system.name}: {sys_metrics.disk_pct:.1f}%",
            severity="alta",
            system_id=system_uuid,
            client_id=client_uuid,
        )

    await db.commit()
    return {"ok": True, "received_at": datetime.now(timezone.utc).isoformat()}
