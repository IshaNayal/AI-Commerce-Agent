from uuid import UUID, uuid4

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    products = relationship(
        "Product",
        back_populates="merchant",
        cascade="all, delete-orphan",
    )

    carts = relationship(
        "Cart",
        back_populates="merchant",
    )
    
    
""" Why server_default=func.now()?

#We want PostgreSQL itself to create the timestamp.

#Instead of relying entirely on Python:

#datetime.now()

#the database provides the timestamp.

#This becomes more reliable when multiple application instances are running. """
