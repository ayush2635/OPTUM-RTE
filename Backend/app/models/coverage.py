from sqlalchemy import ForeignKey, Integer, String, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from app.database import Base
from typing import Optional


class Coverage(Base):
    __tablename__ = "coverage"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    member_id: Mapped[str] = mapped_column(
        String, ForeignKey("members.id"), nullable=False
    )
    plan_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("health_plans.id"), nullable=False
    )
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    termination_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    subscriber_relationship: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
