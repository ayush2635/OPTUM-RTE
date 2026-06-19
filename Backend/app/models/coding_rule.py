from sqlalchemy import Integer, String, Date
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from app.database import Base
from typing import Optional


class CodingRule(Base):
    __tablename__ = "coding_rules"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    column1_cpt: Mapped[str] = mapped_column(String, nullable=False, index=True)
    column2_cpt: Mapped[str] = mapped_column(String, nullable=False, index=True)
    modifier_indicator: Mapped[int] = mapped_column(Integer, nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    delete_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
