import hashlib
import hmac
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.agent_token import AgentToken
from src.models.system import System


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _compute_signature(client_id: str, timestamp: str, body: bytes, raw_token: str) -> str:
    message = f"{client_id}{timestamp}".encode() + body
    return hmac.new(raw_token.encode(), message, hashlib.sha256).hexdigest()


def verify_hmac_signature(
    client_id: str,
    timestamp: str,
    signature: str,
    body: bytes,
    raw_token: str,
    max_age_seconds: int = 300,
) -> bool:
    # Reject stale messages (anti-replay)
    try:
        ts = int(timestamp)
    except (ValueError, TypeError):
        return False

    now = int(time.time())
    if abs(now - ts) > max_age_seconds:
        return False

    expected = _compute_signature(client_id, timestamp, body, raw_token)
    return hmac.compare_digest(expected, signature)


async def resolve_agent_token(db: AsyncSession, client_id: str, token_hash: str) -> AgentToken | None:
    """Find an active token for the given client by its hash."""
    import uuid
    try:
        cid = uuid.UUID(client_id)
    except ValueError:
        return None

    result = await db.execute(
        select(AgentToken).where(
            AgentToken.client_id == cid,
            AgentToken.token_hash == token_hash,
            AgentToken.is_active == True,
        )
    )
    return result.scalar_one_or_none()


def generate_raw_token() -> str:
    """Generate a cryptographically secure 32-byte hex token."""
    import secrets
    return secrets.token_hex(32)
