"""Node models - embedded within campaigns and action runs."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from sdk_248.models.enums import NodeType


class Node(BaseModel):
    """Schema for responder action node."""

    type: NodeType = Field(..., description="Type of node action")
    payload: dict[str, Any] = Field(
        default_factory=dict, description="Node-specific payload data"
    )
    on_result: dict[str, Any] = Field(
        default_factory=dict, description="Result handling configuration"
    )
    next: Optional[int] = Field(None, description="Next node index in the workflow")
