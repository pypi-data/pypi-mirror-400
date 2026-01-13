"""Campaign document model - main MongoDB collection."""

from datetime import datetime, timezone
from typing import Optional

from beanie import Document
from pydantic import Field

from sdk_248.models.enums import AppType, CampaignStatus, EmailOrchestrator
from sdk_248.models.mongo.lead import Lead
from sdk_248.models.mongo.node import Node
from sdk_248.schemas.smartlead.request import CampaignSequenceInput


class Campaign(Document):
    """MongoDB schema for campaigns collection - contains all leads and their action runs."""

    fk_organization_id: int = Field(..., description="Organization ID")
    name: str = Field(..., description="Campaign name")
    status: CampaignStatus = Field(
        default=CampaignStatus.DRAFT, description="Campaign status"
    )
    timezone: str = Field(..., description="Campaign timezone")
    daily_volume: int = Field(..., description="Daily email volume limit")
    start_hour: Optional[str] = Field(
        None, description="Start hour in format 'HH:MM' (e.g., '09:00')"
    )
    end_hour: Optional[str] = Field(
        None, description="End hour in format 'HH:MM' (e.g., '18:00')"
    )
    schedule_start_time: Optional[str] = Field(
        None,
        description="Schedule start time in ISO format (e.g., '2023-04-25T07:29:25.978Z')",
    )
    email_orchestrator: EmailOrchestrator = Field(
        default=EmailOrchestrator.SMARTLEAD,
        description="Email orchestrator service",
    )
    email_orchestrator_campaign_id: Optional[int] = Field(
        None, description="Campaign ID in email orchestrator"
    )
    recycle_minimum_days: int = Field(
        ..., description="Minimum days before recycling a lead"
    )
    inboxes: list[int] = Field(default_factory=list, description="List of inbox IDs")
    leads: list[Lead] = Field(
        default_factory=list, description="List of leads in this campaign"
    )
    sequence_messages: list[CampaignSequenceInput] = Field(
        default_factory=list, description="Email sequence configuration"
    )
    responder_sequence: Optional[list[Node]] = Field(
        None, description="Responder sequence"
    )
    app_type: AppType = Field(..., description="Application type")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp",
    )

    class Settings:
        """Beanie collection settings."""

        name = "campaigns"
        indexes = [
            "fk_organization_id",
            "status",
            "email_orchestrator_campaign_id",
            "leads.email",
            "leads.lead_status",
        ]
