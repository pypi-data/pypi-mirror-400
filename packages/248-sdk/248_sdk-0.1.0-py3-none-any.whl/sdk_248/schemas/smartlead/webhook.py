"""Webhook schemas for SmartLead webhooks."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MessageModel(BaseModel):
    """Schema for email message content."""

    model_config = ConfigDict(extra="allow")

    message_id: str = Field(..., description="Message ID")
    html: str = Field(..., description="HTML content of the message")
    text: str = Field(..., description="Plain text content of the message")
    time: str = Field(..., description="ISO 8601 timestamp of the message")


class MetadataModel(BaseModel):
    """Schema for webhook metadata."""

    model_config = ConfigDict(extra="allow")

    webhook_created_at: str = Field(
        ..., description="ISO 8601 timestamp when webhook was created"
    )


class CampaignReplyWebhookSchema(BaseModel):
    """Schema for campaign reply webhook payload from SmartLead."""

    model_config = ConfigDict(extra="allow")

    webhook_id: int = Field(..., description="Unique webhook identifier")
    webhook_name: str = Field(..., description="Name of the webhook")
    campaign_status: str = Field(..., description="Status of the campaign")
    stats_id: str = Field(..., description="Statistics identifier")
    from_email: str = Field(..., description="Email address of the sender")
    subject: str = Field(..., description="Email subject line")
    sent_message_body: Optional[str] = Field(
        None, description="Body content of the sent message"
    )
    sent_message: MessageModel = Field(..., description="Details of the sent message")
    to_email: str = Field(..., description="Email address of the recipient")
    to_name: str = Field(..., description="Name of the recipient")
    time_replied: Optional[str] = Field(
        None, description="ISO 8601 timestamp when reply was sent"
    )
    event_timestamp: str = Field(..., description="ISO 8601 timestamp of the event")
    reply_message: MessageModel = Field(..., description="Details of the reply message")
    reply_body: Optional[str] = Field(
        None, description="Body content of the reply message"
    )
    message_id: Optional[str] = Field(None, description="Message ID of the reply")
    preview_text: Optional[str] = Field(None, description="Preview text of the reply")
    campaign_name: str = Field(..., description="Name of the campaign")
    campaign_id: int = Field(..., description="Campaign identifier")
    client_id: Optional[int] = Field(
        None, description="Client identifier (null if no client)"
    )
    sequence_number: int = Field(..., description="Sequence number in the campaign")
    secret_key: str = Field(..., description="Secret key for webhook verification")
    app_url: str = Field(..., description="URL to the SmartLead app")
    ui_master_inbox_link: Optional[str] = Field(
        None, description="URL to the master inbox UI"
    )
    description: str = Field(..., description="Description of the webhook event")
    metadata: MetadataModel = Field(..., description="Additional metadata")
    webhook_url: str = Field(..., description="URL where the webhook was sent")
    event_type: str = Field(
        ..., description="Type of webhook event (e.g., 'EMAIL_REPLY')"
    )
    sl_email_lead_id: Optional[int] = Field(
        None, description="SmartLead email lead identifier"
    )
    sl_email_lead_map_id: Optional[int] = Field(
        None, description="SmartLead email lead map identifier"
    )
    sl_lead_email: Optional[str] = Field(
        None, description="SmartLead lead email address"
    )
    webhookUrl: Optional[str] = Field(
        None, description="Webhook URL (camelCase variant)"
    )


class EmailSentWebhookSchema(BaseModel):
    """Schema for email sent webhook payload from SmartLead."""

    model_config = ConfigDict(extra="allow")

    webhook_id: int = Field(..., description="Unique webhook identifier")
    webhook_name: str = Field(..., description="Name of the webhook")
    campaign_status: str = Field(..., description="Status of the campaign")
    client_id: Optional[int] = Field(None, description="Client identifier")
    stats_id: str = Field(..., description="Statistics identifier")
    from_email: str = Field(..., description="Email address of the sender")
    to_email: str = Field(..., description="Email address of the recipient")
    to_name: str = Field(..., description="Name of the recipient")
    event_timestamp: str = Field(..., description="ISO 8601 timestamp of the event")
    campaign_name: str = Field(..., description="Name of the campaign")
    campaign_id: int = Field(..., description="Campaign identifier")
    sequence_number: int = Field(..., description="Sequence number in the campaign")
    sent_message: MessageModel = Field(..., description="Details of the sent message")
    subject: str = Field(..., description="Email subject line")
    secret_key: str = Field(..., description="Secret key for webhook verification")
    app_url: str = Field(..., description="URL to the SmartLead app")
    description: str = Field(..., description="Description of the webhook event")
    metadata: MetadataModel = Field(..., description="Additional metadata")
    webhook_url: str = Field(..., description="URL where the webhook was sent")
    event_type: str = Field(
        ..., description="Type of webhook event (e.g., 'EMAIL_SENT')"
    )
    sl_email_lead_id: Optional[int] = Field(
        None, description="SmartLead email lead identifier"
    )
    sl_email_lead_map_id: Optional[int] = Field(
        None, description="SmartLead email lead map identifier"
    )
    webhookUrl: Optional[str] = Field(
        None, description="Webhook URL (camelCase variant)"
    )
