import uuid
from sqlalchemy import String, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.sqlite import JSON
from app.database import Base
from datetime import date


class Member(Base):
    __tablename__ = "members"
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String, nullable=False)
    ssn_last4: Mapped[str] = mapped_column(String(4), nullable=False)
    member_number: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    group_number: Mapped[str] = mapped_column(String, nullable=False)
