"""Lead model - embedded within campaigns."""

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

from sdk_248.models.mongo.action_run import ActionRun
from sdk_248.schemas.smartlead.webhook import (
    CampaignReplyWebhookSchema,
    EmailSentWebhookSchema,
)


class Lead(BaseModel):
    """Embedded schema for leads within a campaign - matches SmartLead structure.

    Note on is_positive and is_closed_won:
        These fields are Optional[bool] where None means "not yet determined".
        Use the helper methods (is_positive_true(), is_positive_false(), etc.)
        to avoid accidentally treating None as False in boolean contexts.
    """

    email: str = Field(..., description="Lead email address")
    first_name: Optional[str] = Field(None, description="Lead first name")
    last_name: Optional[str] = Field(None, description="Lead last name")
    phone_number: Optional[str] = Field(None, description="Phone number")
    company_name: Optional[str] = Field(None, description="Company name")
    website: Optional[str] = Field(None, description="Company website")
    location: Optional[str] = Field(None, description="Location")
    linkedin_profile: Optional[str] = Field(None, description="LinkedIn profile URL")
    company_url: Optional[str] = Field(None, description="Company URL")
    custom_fields: Optional[dict[str, Any]] = Field(
        None, description="Custom fields (max 20 fields)"
    )
    email_orchestrator_lead_id: Optional[int] = Field(
        None, description="Lead ID in email orchestrator"
    )
    email_orchestrator_lead_map_id: Optional[int] = Field(
        None, description="Lead map ID in email orchestrator"
    )
    last_contacted: Optional[datetime] = Field(
        None, description="Last contact timestamp"
    )
    lead_status: Optional[str] = Field(None, description="Lead status")
    is_positive: Optional[bool] = Field(
        default=None, description="Whether lead is positive"
    )
    is_closed_won: Optional[bool] = Field(
        default=None, description="Whether lead is closed won"
    )
    in_campaign: bool = Field(default=True, description="Whether lead is in a campaign")
    action_runs: list[ActionRun] = Field(
        default_factory=list, description="List of action runs for this lead"
    )
    webhook_payload: Optional[CampaignReplyWebhookSchema] = Field(
        None,
        description="Most recent SmartLead webhook payload received for this lead",
    )
    email_sent_webhook_payloads: list[EmailSentWebhookSchema] = Field(
        default_factory=list,
        description="List of email sent webhook payloads for this lead",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp",
    )
