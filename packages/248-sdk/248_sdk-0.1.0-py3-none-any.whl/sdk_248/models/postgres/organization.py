"""Organization models for managing organizations."""

from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import ENUM as PGEnum

from sdk_248.db.postgres import Base


OrganizationStatus = PGEnum(
    "active",
    "inactive",
    name="organization_status",
    create_type=False,
)


class Organization(Base):
    """Organization entity."""

    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    clerk_auth_org_id = Column(String, nullable=False, unique=True)
    status = Column(OrganizationStatus, nullable=False, server_default="active")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
