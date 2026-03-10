"""
setup_db.py — Inicializa la base de datos de Orbit.
Ejecutar una vez en el servidor antes de arrancar el servicio.

Uso: python scripts/setup_db.py
"""
import asyncio
import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def main():
    from src.database import engine, AsyncSessionLocal
    from src.models import Base
    from src.models.user import User
    from src.models.client import Client
    from src.models.system import System
    from src.services.auth_service import hash_password
    from config.settings import get_settings
    from sqlalchemy import select, text
    import uuid

    settings = get_settings()

    print("=" * 50)
    print("Orbit — Setup de base de datos")
    print("=" * 50)

    # Create all tables
    print("\n[1/3] Creando tablas...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("      OK — Tablas creadas.")

    # Create admin user
    print("\n[2/3] Creando usuario admin...")
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == settings.admin_email))
        existing = result.scalar_one_or_none()

        if existing:
            print(f"      OK — Admin '{settings.admin_email}' ya existe, omitiendo.")
        else:
            if not settings.admin_password:
                print("      ERROR: ADMIN_PASSWORD no configurada en .env")
                sys.exit(1)
            admin = User(
                id=uuid.uuid4(),
                email=settings.admin_email,
                name="Admin AURENIX",
                password_hash=hash_password(settings.admin_password),
            )
            db.add(admin)
            await db.commit()
            print(f"      OK — Admin creado: {settings.admin_email}")

    # Create AURENIX as first internal client
    print("\n[3/3] Registrando AURENIX como cliente interno...")
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Client).where(Client.slug == "aurenix-internal"))
        existing = result.scalar_one_or_none()

        if existing:
            print("      OK — Cliente AURENIX ya existe, omitiendo.")
        else:
            from datetime import date
            client = Client(
                id=uuid.uuid4(),
                name="AURENIX (Interno)",
                slug="aurenix-internal",
                plan="enterprise",
                mrr_eur=0,
                vps_cost_eur=0,
                contact_email=settings.admin_email,
                contact_name="Equipo AURENIX",
                notes="Cliente interno — sistemas propios de AURENIX",
                started_at=date.today(),
            )
            db.add(client)
            await db.commit()
            print(f"      OK — Cliente interno creado. ID: {client.id}")
            print(f"\n      Guarda este ID para el agente: CLIENT_ID={client.id}")

    print("\n" + "=" * 50)
    print("Setup completado.")
    print("Siguiente paso: python main.py serve")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
