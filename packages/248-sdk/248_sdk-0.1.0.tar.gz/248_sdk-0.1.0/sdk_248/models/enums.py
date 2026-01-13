"""Enums for SDK models."""

from enum import Enum


class CampaignStatus(str, Enum):
    """Campaign status enumeration."""

    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class EmailOrchestrator(str, Enum):
    """Email orchestrator enumeration."""

    SMARTLEAD = "Smartlead"


class AppType(str, Enum):
    """Application type enumeration."""

    OUTBOUNDER = "Outbounder"
    RECRUITER = "Recruiter"
    INBOUNDER = "Inbounder"


class NodeType(str, Enum):
    """Node type enumeration for responder actions."""

    CATEGORISER = "Categoriser"
    FORWARDER = "Forwarder"
    CRM_UPSERT = "CRM Upsert"
    CRM_TASK = "CRM Task"


class ActionRunStatus(str, Enum):
    """Action run status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CategoriserStatus(str, Enum):
    """Categoriser status enumeration."""

    INTERESTED = "Interested"
    NOT_INTERESTED = "NotInterested"
    UNSUBSCRIBE = "Unsubscribe"
    WRONG_PERSON = "WrongPerson"
    OUT_OF_OFFICE = "OutOfOffice"
