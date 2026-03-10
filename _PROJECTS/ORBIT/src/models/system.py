import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, Numeric, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class System(Base):
    __tablename__ = "systems"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    system_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # operativo | degradado | caido | en_construccion | mantenimiento
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="en_construccion")
    base_url: Mapped[str | None] = mapped_column(String(500))
    pull_key: Mapped[str | None] = mapped_column(String(255))  # API key for metrics pull (read-only)
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_metrics_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    uptime_30d: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))  # cached uptime %
    notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    client: Mapped["Client"] = relationship("Client", back_populates="systems")
    heartbeats: Mapped[list["Heartbeat"]] = relationship("Heartbeat", back_populates="system")
    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="system")
