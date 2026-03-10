"""
Orbit — AURENIX Control Dashboard
CLI entry point.

Usage:
  python main.py serve         Start the dashboard server
  python main.py setup         Initialize database and create admin user
  python main.py add-token     Generate an agent token for a client
"""
import sys
import asyncio


def serve():
    import uvicorn
    from config.settings import get_settings
    settings = get_settings()
    uvicorn.run(
        "src.api.server:app",
        host="0.0.0.0",
        port=settings.port,
        reload=not settings.is_production,
        log_level="info",
    )


def setup():
    asyncio.run(_setup())


async def _setup():
    from src.database import engine
    from src.models import Base
    from src.models.user import User
    from src.database import AsyncSessionLocal
    from src.services.auth_service import hash_password
    from config.settings import get_settings
    from sqlalchemy import select
    import uuid

    settings = get_settings()

    print("Creando tablas en la base de datos...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tablas creadas.")

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == settings.admin_email))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"El usuario admin '{settings.admin_email}' ya existe.")
        else:
            admin = User(
                id=uuid.uuid4(),
                email=settings.admin_email,
                name="Admin AURENIX",
                password_hash=hash_password(settings.admin_password),
            )
            db.add(admin)
            await db.commit()
            print(f"Usuario admin creado: {settings.admin_email}")

    print("\nSetup completado. Arranca el servidor con: python main.py serve")


def add_token():
    asyncio.run(_add_token())


async def _add_token():
    from src.database import AsyncSessionLocal
    from src.models.agent_token import AgentToken
    from src.models.client import Client
    from src.services.hmac_service import generate_raw_token, _hash_token
    from sqlalchemy import select
    import uuid

    client_id_str = input("Client ID (UUID): ").strip()
    label = input("Etiqueta (ej: VPS principal): ").strip()

    try:
        client_uuid = uuid.UUID(client_id_str)
    except ValueError:
        print("UUID invalido.")
        return

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Client).where(Client.id == client_uuid))
        client = result.scalar_one_or_none()
        if not client:
            print("Cliente no encontrado.")
            return

        raw_token = generate_raw_token()
        token_hash = _hash_token(raw_token)

        record = AgentToken(
            id=uuid.uuid4(),
            client_id=client_uuid,
            token_hash=token_hash,
            label=label,
        )
        db.add(record)
        await db.commit()

    print(f"\nToken generado para '{client.name}':")
    print(f"  AGENT_TOKEN={raw_token}")
    print(f"  CLIENT_ID={client_id_str}")
    print("\nCopia estos valores al .env del agente en el VPS cliente.")
    print("IMPORTANTE: Este token no se puede recuperar. Guardalo ahora.")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "serve"
    if command == "serve":
        serve()
    elif command == "setup":
        setup()
    elif command == "add-token":
        add_token()
    else:
        print(__doc__)
        sys.exit(1)
