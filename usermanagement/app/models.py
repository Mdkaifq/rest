from sqlalchemy import String, ForeignKey, Text, TIMESTAMP, Enum
from sqlalchemy.orm import Mapped, mapped_column, validates
from datetime import datetime, timezone, date
from .db import Base
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid
from sqlalchemy.types import JSON
from passlib.context import CryptContext
from typing import Optional
import enum

class Role(enum.Enum):
    USER = "User"
    ADMIN = "Admin"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    id: Mapped[PGUUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    first_name: Mapped[str] = mapped_column(index=True)
    last_name: Mapped[str] = mapped_column(index=True)
    phone_no: Mapped[str] = mapped_column(index=True, nullable=True)
    role: Mapped[Role] = mapped_column(Enum(Role, name="role_enum"), default=Role.USER)
    created_on: Mapped[datetime] = mapped_column(TIMESTAMP, default=date.today(), nullable=False)

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)



class Case(Base):
    __tablename__ = "cases"

    id: Mapped[PGUUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="NEW")

    created_on: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now(timezone.utc), nullable=False)

    created_by: Mapped[PGUUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    updated_on: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)

    updated_by: Mapped[PGUUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    status_change_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    assignee: Mapped[PGUUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    watchers: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)


    @validates("id", "title", "created_on", "created_by")
    def validate_immutable_fields(self, key, value):
        # Prevent changes after the initial set
        if getattr(self, key) is not None and getattr(self, key) != value:
            raise ValueError(f"{key} is immutable and cannot be changed.")
        return value