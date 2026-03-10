import uuid
import asyncio
from config.settings import get_settings

settings = get_settings()

SEVERITY_EMOJI = {
    "critica": "🔴",
    "alta": "🟠",
    "media": "🟡",
    "baja": "🔵",
    "info": "⚪",
}


async def send_alert_notification(alert, system_id: uuid.UUID | None, client_id: uuid.UUID | None) -> None:
    """Send alert to the AURENIX admin Telegram chat."""
    if not settings.telegram_bot_token or not settings.telegram_admin_chat_id:
        return

    emoji = SEVERITY_EMOJI.get(alert.severity, "⚠️")
    lines = [
        f"{emoji} *ORBIT ALERT* — {alert.severity.upper()}",
        f"*{alert.title}*",
    ]
    if alert.description:
        lines.append(alert.description)
    lines.append(f"`{alert.alert_type}`")

    text = "\n".join(lines)

    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
                json={
                    "chat_id": settings.telegram_admin_chat_id,
                    "text": text,
                    "parse_mode": "Markdown",
                },
            )
    except Exception:
        pass  # Non-critical — alert is saved in DB regardless


async def send_info_message(text: str) -> None:
    """Send a plain info message to the admin chat."""
    if not settings.telegram_bot_token or not settings.telegram_admin_chat_id:
        return
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
                json={
                    "chat_id": settings.telegram_admin_chat_id,
                    "text": text,
                    "parse_mode": "Markdown",
                },
            )
    except Exception:
        pass
