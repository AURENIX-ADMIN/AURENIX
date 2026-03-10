from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.services.auth_service import decode_token, get_user_by_id
from src.models.user import User


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    """
    Extract JWT from httpOnly cookie or Authorization header.
    Cookie takes precedence (browser sessions), header for API clients.
    """
    token = request.cookies.get("orbit_session")

    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
        )

    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
        )

    user = await get_user_by_id(db, payload.get("sub", ""))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )

    return user
