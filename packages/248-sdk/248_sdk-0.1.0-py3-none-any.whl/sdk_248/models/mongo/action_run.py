"""Action run model - embedded within leads."""

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

from sdk_248.models.enums import ActionRunStatus, NodeType


class ActionRun(BaseModel):
    """Embedded schema for action runs within a lead.

    Each ActionRun represents the execution of the entire responder_sequence for a lead.
    The block_history contains the execution history of each node/block in the sequence,
    ordered by execution time. Each BlockHistory entry references the node_index in the
    campaign's responder_sequence that was executed.
    """

    run_id: str = Field(
        ..., description="Unique run identifier for this sequence execution"
    )
    node_type: Optional[NodeType] = Field(
        None, description="Type of node this action run is executing"
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Execution context shared across all blocks in this run",
    )
    status: ActionRunStatus = Field(
        default=ActionRunStatus.PENDING,
        description="Current status of the entire sequence run",
    )
    current_node_index: Optional[int] = Field(
        None,
        description="Index of the current node being executed in responder_sequence",
    )
    result: Optional[dict[str, Any]] = Field(
        None, description="Final result/output of the entire sequence execution"
    )
    error_message: Optional[str] = Field(
        None, description="Error message if the sequence execution failed"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp",
    )
