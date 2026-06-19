from sqlalchemy import String, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class HealthPlan(Base):
    __tablename__ = "health_plans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_code: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    plan_name: Mapped[str] = mapped_column(String, nullable=False)
    deductible_amount: Mapped[float] = mapped_column(Numeric, nullable=False)
    copay_primary_care: Mapped[float] = mapped_column(Numeric, nullable=False)
    copay_specialist: Mapped[float] = mapped_column(Numeric, nullable=False)
    out_of_pocket_max: Mapped[float] = mapped_column(Numeric, nullable=False)
