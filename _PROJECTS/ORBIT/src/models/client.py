import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, Date, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    plan: Mapped[str] = mapped_column(String(50), nullable=False)  # basic | pro | enterprise
    mrr_eur: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    vps_cost_eur: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    contact_email: Mapped[str | None] = mapped_column(String(255))
    contact_name: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    started_at: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    systems: Mapped[list["System"]] = relationship("System", back_populates="client", lazy="selectin")
    agent_tokens: Mapped[list["AgentToken"]] = relationship("AgentToken", back_populates="client")
    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="client")
    onboarding_tasks: Mapped[list["OnboardingTask"]] = relationship(
        "OnboardingTask", back_populates="client", order_by="OnboardingTask.sort_order"
    )
