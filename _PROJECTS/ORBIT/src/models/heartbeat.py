import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, Numeric, BigInteger, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class Heartbeat(Base):
    __tablename__ = "heartbeats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    system_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("systems.id", ondelete="CASCADE"), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    agent_status: Mapped[str | None] = mapped_column(String(20))  # healthy | degraded | critical
    fastapi_up: Mapped[bool | None] = mapped_column(Boolean)
    n8n_up: Mapped[bool | None] = mapped_column(Boolean)
    postgresql_up: Mapped[bool | None] = mapped_column(Boolean)
    telegram_bot_up: Mapped[bool | None] = mapped_column(Boolean)
    cpu_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    ram_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    disk_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    agent_version: Mapped[str | None] = mapped_column(String(20))
    raw_payload: Mapped[dict | None] = mapped_column(JSON)

    system: Mapped["System"] = relationship("System", back_populates="heartbeats")
