import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.alert import Alert
from src.models.system import System
from src.models.client import Client
from src.notifications.telegram_notifier import send_alert_notification

CRITICAL_SEVERITIES = {"critica", "alta"}


async def create_alert(
    db: AsyncSession,
    alert_type: str,
    title: str,
    severity: str,
    description: str | None = None,
    system_id: uuid.UUID | None = None,
    client_id: uuid.UUID | None = None,
) -> Alert | None:
    """
    Create an alert only if no identical open alert already exists (deduplication).
    Returns the alert if created, None if deduplicated.
    """
    # Deduplication: skip if same type + system already has an open alert
    filters = [
        Alert.alert_type == alert_type,
        Alert.status == "open",
    ]
    if system_id:
        filters.append(Alert.system_id == system_id)
    elif client_id:
        filters.append(Alert.client_id == client_id)

    existing = await db.execute(select(Alert).where(*filters))
    if existing.scalar_one_or_none():
        return None  # Already open, don't duplicate

    alert = Alert(
        id=uuid.uuid4(),
        system_id=system_id,
        client_id=client_id,
        severity=severity,
        alert_type=alert_type,
        title=title,
        description=description,
        status="open",
    )
    db.add(alert)
    await db.flush()

    # Send Telegram notification for critical/high severity
    if severity in CRITICAL_SEVERITIES:
        try:
            await send_alert_notification(alert, system_id, client_id)
            alert.telegram_sent = True
        except Exception:
            pass  # Notification failure must not block alert creation

    return alert


async def acknowledge_alert(db: AsyncSession, alert_id: uuid.UUID, user_id: uuid.UUID) -> Alert | None:
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert or alert.status != "open":
        return None
    alert.status = "acknowledged"
    alert.acknowledged_at = datetime.now(timezone.utc)
    return alert


async def resolve_alert(db: AsyncSession, alert_id: uuid.UUID, user_id: uuid.UUID) -> Alert | None:
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert or alert.status == "resolved":
        return None
    alert.status = "resolved"
    alert.resolved_at = datetime.now(timezone.utc)
    alert.resolved_by = user_id
    return alert


async def silence_alert(db: AsyncSession, alert_id: uuid.UUID, until: datetime) -> Alert | None:
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        return None
    alert.status = "silenced"
    alert.silenced_until = until
    return alert


async def get_open_alerts(db: AsyncSession, limit: int = 50) -> list[Alert]:
    result = await db.execute(
        select(Alert)
        .where(Alert.status.in_(["open", "acknowledged"]))
        .order_by(Alert.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
