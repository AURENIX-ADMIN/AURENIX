import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, BigInteger, Integer, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class SystemMetric(Base):
    __tablename__ = "system_metrics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    system_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("systems.id", ondelete="CASCADE"), nullable=False)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Claude usage (last hour period)
    claude_haiku_tokens: Mapped[int] = mapped_column(BigInteger, default=0)
    claude_sonnet_tokens: Mapped[int] = mapped_column(BigInteger, default=0)
    claude_cost_eur: Mapped[Decimal] = mapped_column(Numeric(8, 4), default=0)

    # n8n
    n8n_executions_total: Mapped[int] = mapped_column(Integer, default=0)
    n8n_executions_failed: Mapped[int] = mapped_column(Integer, default=0)

    # System-specific metrics (flexible per system type)
    custom_metrics: Mapped[dict] = mapped_column(JSON, default=dict)
