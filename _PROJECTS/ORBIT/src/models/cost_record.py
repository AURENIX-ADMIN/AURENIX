import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import UUID, Date, DateTime, Numeric, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class CostRecord(Base):
    __tablename__ = "cost_records"
    __table_args__ = (UniqueConstraint("system_id", "month", name="uq_cost_system_month"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    system_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("systems.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    month: Mapped[datetime] = mapped_column(Date, nullable=False)  # first day of month

    claude_haiku_eur: Mapped[Decimal] = mapped_column(Numeric(8, 4), default=0)
    claude_sonnet_eur: Mapped[Decimal] = mapped_column(Numeric(8, 4), default=0)
    vps_share_eur: Mapped[Decimal] = mapped_column(Numeric(8, 4), default=0)
    total_cost_eur: Mapped[Decimal] = mapped_column(Numeric(8, 4), default=0)
    mrr_eur: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    margin_eur: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    margin_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
