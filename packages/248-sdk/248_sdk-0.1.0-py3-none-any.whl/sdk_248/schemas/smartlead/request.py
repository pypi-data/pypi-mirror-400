"""Request schemas for SmartLead API."""

import base64
import csv
import io
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from sdk_248.models.mongo.node import Node
from sdk_248.schemas.smartlead.validators import validate_responder_sequence_nodes


class TrackSetting(str, Enum):
    """Enum for tracking settings."""

    DONT_TRACK_EMAIL_OPEN = "DONT_TRACK_EMAIL_OPEN"
    DONT_TRACK_LINK_CLICK = "DONT_TRACK_LINK_CLICK"
    DONT_TRACK_REPLY_TO_AN_EMAIL = "DONT_TRACK_REPLY_TO_AN_EMAIL"


class StopLeadSetting(str, Enum):
    """Enum for stop lead settings."""

    REPLY_TO_AN_EMAIL = "REPLY_TO_AN_EMAIL"
    CLICK_ON_A_LINK = "CLICK_ON_A_LINK"
    OPEN_AN_EMAIL = "OPEN_AN_EMAIL"


class BaseCampaignRequest(BaseModel):
    """Base schema for campaign-related requests."""

    client_id: Optional[int] = Field(None, description="Client ID (null if no client)")


class BaseScheduleRequest(BaseModel):
    """Base schema for schedule-related requests."""

    timezone: Optional[str] = Field(
        None, description="Timezone (e.g., 'America/Los_Angeles')"
    )
    days_of_the_week: Optional[list[int]] = Field(
        None, description="Days of the week [0,1,2,3,4,5,6] where 0=Sunday"
    )
    start_hour: Optional[str] = Field(
        None, description="Start hour in format 'HH:MM' (e.g., '09:00')"
    )
    end_hour: Optional[str] = Field(
        None, description="End hour in format 'HH:MM' (e.g., '18:00')"
    )
    min_time_btw_emails: Optional[int] = Field(
        None, description="Minimum time between emails in minutes"
    )
    max_new_leads_per_day: Optional[int] = Field(
        None, description="Maximum new leads per day"
    )


class BaseSettingsRequest(BaseModel):
    """Base schema for campaign settings requests."""

    model_config = ConfigDict(use_enum_values=True)

    track_settings: Optional[list[TrackSetting]] = Field(
        None,
        description="Tracking settings: DONT_TRACK_EMAIL_OPEN | "
        "DONT_TRACK_LINK_CLICK | DONT_TRACK_REPLY_TO_AN_EMAIL",
    )
    stop_lead_settings: Optional[StopLeadSetting] = Field(
        None,
        description="Stop lead settings: REPLY_TO_AN_EMAIL | CLICK_ON_A_LINK | OPEN_AN_EMAIL",
    )
    unsubscribe_text: Optional[str] = Field(None, description="Unsubscribe text")
    send_as_plain_text: Optional[bool] = Field(
        None, description="Send emails as plain text"
    )
    follow_up_percentage: Optional[int] = Field(
        None, ge=0, le=100, description="Follow-up percentage (0-100)"
    )
    enable_ai_esp_matching: Optional[bool] = Field(
        None, description="Enable AI ESP matching for similar mailboxes"
    )
    bounce_autopause_threshold: Optional[str] = Field(
        None, description="Number of bounces to autopause campaign"
    )


class BaseLeadRequest(BaseModel):
    """Base schema for lead-related requests."""

    first_name: Optional[str] = Field(None, description="Lead first name")
    last_name: Optional[str] = Field(None, description="Lead last name")
    email: str = Field(..., description="Lead email address")
    phone_number: Optional[str] = Field(None, description="Phone number")
    company_name: Optional[str] = Field(None, description="Company name")
    website: Optional[str] = Field(None, description="Company website")
    location: Optional[str] = Field(None, description="Location")
    linkedin_profile: Optional[str] = Field(None, description="LinkedIn profile URL")
    company_url: Optional[str] = Field(None, description="Company URL")
    custom_fields: Optional[dict[str, Any]] = Field(
        None, description="Custom fields (max 20 fields)"
    )

    @field_validator("custom_fields")
    @classmethod
    def validate_custom_fields_max_length(
        cls, v: Optional[dict[str, Any]]
    ) -> Optional[dict[str, Any]]:
        """Validate that custom_fields dict has at most 20 items and normalize keys."""
        if v is not None:
            if len(v) > 20:
                raise ValueError("custom_fields must have at most 20 fields")
            normalized = {}
            for k, val in v.items():
                normalized_key = k.strip()
                if normalized_key:
                    normalized[normalized_key] = val
            return normalized if normalized else None
        return v


class CreateCampaignRequest(BaseCampaignRequest):
    """Request schema for creating a campaign."""

    name: str = Field(..., description="Campaign name")
    leads_csv_base64: str = Field(
        ..., description="Base64-encoded CSV file containing leads"
    )
    field_mappings: dict[str, str] = Field(
        ..., description="Mapping of CSV fields to campaign fields"
    )

    def parse_csv_leads(
        self, settings: Optional["AddLeadsSettings"] = None
    ) -> "AddLeadsToCampaignRequest":
        """Parse base64-encoded CSV and convert to AddLeadsToCampaignRequest."""
        if not self.leads_csv_base64:
            raise ValueError("leads_csv_base64 is not provided")

        try:
            csv_bytes = base64.b64decode(self.leads_csv_base64)
            csv_string = csv_bytes.decode("utf-8")
        except Exception as e:
            raise ValueError(f"Failed to decode base64 CSV: {e}") from e

        try:
            csv_reader = csv.DictReader(io.StringIO(csv_string))
            base_fields = {
                "email",
                "first_name",
                "last_name",
                "phone_number",
                "company_name",
                "website",
                "location",
                "linkedin_profile",
                "company_url",
            }

            mapped_csv_columns = set(self.field_mappings.values())

            leads = []
            for row in csv_reader:
                base_data = {}
                for field in base_fields:
                    csv_col = self.field_mappings.get(field)
                    if csv_col and csv_col in row:
                        value = row[csv_col].strip() if row[csv_col] else None
                        base_data[field] = value or None
                    else:
                        base_data[field] = None

                custom_fields = {
                    k.strip(): v.strip()
                    for k, v in row.items()
                    if k not in mapped_csv_columns
                    and v.strip()
                    and k.strip()
                }

                for k, v in custom_fields.items():
                    custom_fields[k] = v.replace("{{first_name}}", base_data.get("first_name", ""))

                lead = BaseLeadRequest(
                    **base_data,
                    custom_fields=custom_fields if custom_fields else None,
                )
                leads.append(lead)

            if not leads:
                raise ValueError("CSV file contains no valid leads")

            if settings is None:
                settings = AddLeadsSettings()

            return AddLeadsToCampaignRequest(lead_list=leads, settings=settings)

        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {e}") from e


class DeleteCampaignRequest(BaseCampaignRequest):
    """Request schema for deleting a campaign."""

    campaign_id: int = Field(..., description="Campaign ID to delete")


class UpdateCampaignScheduleRequest(BaseScheduleRequest):
    """Request schema for updating campaign schedule."""

    schedule_start_time: Optional[str] = Field(
        None,
        description="Schedule start time in ISO format (e.g., '2023-04-25T07:29:25.978Z')",
    )


class UpdateCampaignSettingsRequest(BaseSettingsRequest, BaseCampaignRequest):
    """Request schema for updating campaign general settings."""

    pass


class EmailSequenceStep(BaseModel):
    """Schema for a single email sequence step."""

    step_number: int = Field(..., description="Step number in sequence")
    subject: Optional[str] = Field(None, description="Email subject")
    body: Optional[str] = Field(None, description="Email body")
    delay_days: Optional[int] = Field(
        None, description="Delay in days before sending this step"
    )


class SaveCampaignSequenceRequest(BaseModel):
    """Request schema for saving campaign sequence."""

    steps: list[EmailSequenceStep] = Field(
        ..., description="List of email sequence steps"
    )


class AddEmailAccountRequest(BaseModel):
    """Request schema for adding email account to campaign."""

    email_account_ids: List[int] = Field(
        ..., description="Email account ID to add to campaign"
    )


class AddLeadsSettings(BaseModel):
    """Settings for adding leads to a campaign."""

    ignore_global_block_list: bool = Field(
        default=False,
        description="If true, ignores leads uploaded in the "
        "lead list that are part of your global/client level block list",
    )
    ignore_unsubscribe_list: bool = Field(
        default=False,
        description="If true, ignores leads uploaded in the "
        "lead list that have unsubscribed previously",
    )
    ignore_duplicate_leads_in_other_campaign: bool = Field(
        default=True,
        description="If false, allows leads to be added to this campaign "
        "even if they exist in another campaign",
    )


class AddLeadsToCampaignRequest(BaseModel):
    """Request schema for adding leads to a campaign by ID."""

    lead_list: list[BaseLeadRequest] = Field(
        ...,
        description="List of leads to add to the campaign "
        "(will be batched into groups of 100 for SmartLead API)",
    )
    settings: Optional[AddLeadsSettings] = Field(
        default_factory=AddLeadsSettings, description="Settings for adding leads"
    )


class CampaignSequenceInput(BaseModel):
    """Schema for a single campaign sequence input."""

    delay_in_days: int = Field(
        ..., description="Delay in days before sending this sequence", ge=0
    )
    email: str = Field(..., description="Email body content (HTML or plain text)")
    subject: Optional[str] = Field(
        None, description="Email subject (blank makes follow-up in same thread)"
    )


class CreateCampaignSequencesRequest(BaseModel):
    """Request schema for creating campaign sequences."""

    sequences: list[CampaignSequenceInput] = Field(
        ..., description="List of campaign sequences to create"
    )


class UpdateCampaignMetadataRequest(BaseModel):
    """Request schema for updating campaign metadata."""

    campaign_start_date: str = Field(
        ..., description="Campaign start date in ISO format (e.g., '2023-04-25')"
    )
    start_hour: str = Field(
        ..., description="Start hour in format 'HH:MM' (e.g., '09:00')"
    )
    end_hour: str = Field(..., description="End hour in format 'HH:MM' (e.g., '18:00')")
    timezone: str = Field(..., description="Campaign timezone")
    daily_volume: int = Field(..., description="Daily email volume limit")
    inboxes: list[int] = Field(..., description="List of inbox IDs")


class UpdateResponderSequenceRequest(BaseModel):
    """Request schema for updating responder sequence."""

    nodes: list[Node] = Field(
        ..., description="List of nodes in the responder sequence"
    )

    @field_validator("nodes")
    @classmethod
    def validate_nodes(cls, v: list[Node]) -> list[Node]:
        """Validate node structure based on node type."""
        return validate_responder_sequence_nodes(v)


class ReplyEmailThreadRequest(BaseModel):
    """Request schema for replying to an email thread in a campaign."""

    email_stats_id: str = Field(
        ...,
        description="Unique ID per lead per email sequence per campaign "
        "(can be fetched via message-history API)",
    )
    email_body: str = Field(..., description="Reply message email body")
    reply_message_id: str = Field(
        ...,
        description="Message ID to which email will be sent reply "
        "(can be fetched via message-history API)",
    )
    cc: Optional[str] = Field(None, description="CC email address")
    bcc: Optional[str] = Field(None, description="BCC email address")
    to_email: Optional[str] = Field(None, description="To email address")


class MarkCategorizerAsInterestedRequest(BaseModel):
    """Request schema for marking a categorizer action run as Interested."""

    lead_email: str = Field(..., description="Email address of the lead")
