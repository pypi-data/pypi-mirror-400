"""Response schemas for SmartLead API."""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class CampaignStatus(str, Enum):
    """Enum for SmartLead campaign status values."""

    DRAFTED = "DRAFTED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"
    PAUSED = "PAUSED"


class LeadStatus(str, Enum):
    """Enum for lead status values."""

    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    INPROGRESS = "INPROGRESS"


class BaseSuccessResponse(BaseModel):
    """Base schema for success responses."""

    ok: bool = Field(..., description="Whether the operation was successful")


class BaseCampaignResponse(BaseModel):
    """Base schema for campaign responses."""

    id: Optional[int] = Field(None, description="Campaign ID")
    user_id: Optional[int] = Field(None, description="User ID")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Update timestamp")
    status: Optional[CampaignStatus] = Field(
        None, description="Campaign status: DRAFTED/ACTIVE/COMPLETED/STOPPED/PAUSED"
    )
    name: Optional[str] = Field(None, description="Campaign name")
    client_id: Optional[int] = Field(None, description="Client ID")


class CreateCampaignResponse(BaseSuccessResponse, BaseCampaignResponse):
    """Response schema for campaign creation."""

    pass


class DeleteCampaignResponse(BaseSuccessResponse):
    """Response schema for campaign deletion."""

    pass


class UpdateCampaignScheduleResponse(BaseSuccessResponse):
    """Response schema for updating campaign schedule."""

    pass


class UpdateCampaignSettingsResponse(BaseSuccessResponse):
    """Response schema for updating campaign settings."""

    pass


class SaveCampaignSequenceResponse(BaseSuccessResponse):
    """Response schema for saving campaign sequence."""

    pass


class CreateCampaignSequencesResponse(BaseSuccessResponse):
    """Response schema for creating campaign sequences."""

    pass


class AddEmailAccountResponse(BaseSuccessResponse):
    """Response schema for adding email account to campaign."""

    pass


class AddLeadsResponse(BaseSuccessResponse):
    """Response schema for adding leads to campaign."""

    added_count: Optional[int] = Field(None, description="Number of leads added")
    skipped_count: Optional[int] = Field(None, description="Number of leads skipped")
    message: Optional[str] = Field(None, description="Response message")


class CampaignSequenceResponse(BaseModel):
    """Response schema for campaign sequence data."""

    id: Optional[int] = Field(None, description="Sequence ID")
    email_campaign_id: Optional[int] = Field(None, description="Campaign ID")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Update timestamp")
    steps: Optional[list[dict[str, Any]]] = Field(None, description="Sequence steps")


class LeadResponse(BaseModel):
    """Response schema for lead data."""

    id: Optional[int] = Field(None, description="Lead ID")
    email: Optional[str] = Field(None, description="Lead email")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    company_name: Optional[str] = Field(None, description="Company name")
    phone_number: Optional[str] = Field(None, description="Phone number")
    website: Optional[str] = Field(None, description="Website")
    location: Optional[str] = Field(None, description="Location")
    linkedin_profile: Optional[str] = Field(None, description="LinkedIn profile")
    company_url: Optional[str] = Field(None, description="Company URL")
    status: Optional[LeadStatus] = Field(
        None,
        description="Lead status: STARTED/COMPLETED/BLOCKED/INPROGRESS",
    )
    custom_fields: Optional[dict[str, Any]] = Field(None, description="Custom fields")


class TimezoneInfo(BaseModel):
    """Response schema for timezone information."""

    value: str = Field(
        ..., description="Timezone identifier (e.g., 'America/New_York')"
    )
    label: str = Field(
        ..., description="Human-readable label (e.g., 'America/New_York (UTC-05:00)')"
    )
    utc: str = Field(..., description="UTC offset string (e.g., 'UTC-05:00')")
    offset: int = Field(..., description="UTC offset in hours (e.g., -5)")


class EmailAccountResponse(BaseModel):
    """Response schema for email account/inbox data."""

    id: Optional[int] = Field(None, description="Email account ID")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Update timestamp")
    from_name: Optional[str] = Field(None, description="Display name for sender")
    from_email: Optional[str] = Field(None, description="Email address")
    daily_sent_count: Optional[int] = Field(None, description="Daily sent count")


class LeadMessageResponse(BaseModel):
    """Response schema for a single message in lead message history."""

    type: str = Field(..., description="Message type: SENT or REPLY")
    message_id: Optional[str] = Field(None, description="Email message ID")
    stats_id: str = Field(..., description="Statistics identifier")
    time: Optional[str] = Field(
        None, description="ISO 8601 timestamp when message was sent/received"
    )
    email_body: Optional[str] = Field(None, description="Email body content (HTML)")
    subject: Optional[str] = Field(
        None, description="Email subject (typically only for SENT messages)"
    )


class LeadMessageHistoryResponse(BaseModel):
    """Response schema for lead message history."""

    history: list[LeadMessageResponse] = Field(
        default_factory=list, description="List of messages in chronological order"
    )
    from_email: str = Field(..., description="Sender email address")
    to_email: str = Field(..., description="Recipient email address")


class CampaignResponse(BaseModel):
    """Response schema for full campaign data."""

    id: int
    user_id: int
    created_at: str
    updated_at: str
    status: CampaignStatus
    name: str
    track_settings: list[str]
    min_time_btwn_emails: int
    max_leads_per_day: int
    stop_lead_settings: str
    schedule_start_time: Optional[str] = None
    enable_ai_esp_matching: bool
    send_as_plain_text: bool
    follow_up_percentage: int
    unsubscribe_text: Optional[str] = None
    parent_campaign_id: Optional[int] = None
    client_id: Optional[int] = None
    email_accounts: Optional[list[EmailAccountResponse]] = None
