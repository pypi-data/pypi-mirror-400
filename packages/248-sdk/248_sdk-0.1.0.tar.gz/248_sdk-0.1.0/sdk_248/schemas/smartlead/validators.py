"""Validation functions for responder sequence nodes."""

from sdk_248.models.mongo.node import Node
from sdk_248.models.enums import NodeType


def _validate_node_index(idx: int, node_count: int, field_name: str = "index") -> None:
    """Validate that an index is within valid range."""
    if not isinstance(idx, int) or idx < 0 or idx >= node_count:
        raise ValueError(
            f"'{field_name}' must be a valid node index (0-{node_count-1}), got {idx}"
        )


def _validate_next_field(node: Node, idx: int, node_count: int, node_type: str) -> None:
    """Validate that next field is valid if provided.

    Multiple nodes can be end nodes (have next=None), so we only validate
    that if next is provided, it's a valid index.
    """
    if node.next is not None:
        _validate_node_index(node.next, node_count, "next")


def _validate_categoriser_node(node: Node, idx: int, node_count: int) -> None:
    """Validate Categoriser node structure."""
    if not node.on_result:
        raise ValueError(f"Categoriser node at index {idx} must have 'on_result' field")
    for key, value in node.on_result.items():
        _validate_node_index(value, node_count, f"on_result['{key}']")


def _validate_forwarder_node(node: Node, idx: int, node_count: int) -> None:
    """Validate Forwarder node structure."""
    if not node.payload or not all(key in node.payload for key in ["to", "cc", "bcc"]):
        raise ValueError(
            f"Forwarder node at index {idx}: 'payload' must contain 'to', 'cc', and 'bcc' fields"
        )
    _validate_next_field(node, idx, node_count, "Forwarder")


def _validate_crm_update_node(node: Node, idx: int, node_count: int) -> None:
    """Validate CRM_UPDATE node structure."""
    if not node.payload:
        raise ValueError(f"CRM_UPDATE node at index {idx} must have 'payload' field")
    if "fields_to_update" not in node.payload:
        raise ValueError(
            f"CRM_UPDATE node at index {idx}: 'payload.fields_to_update' is required"
        )
    if not isinstance(node.payload["fields_to_update"], dict):
        raise ValueError(
            f"CRM_UPDATE node at index {idx}: 'payload.fields_to_update' must be a dictionary"
        )
    _validate_next_field(node, idx, node_count, "CRM_UPDATE")


def validate_responder_sequence_nodes(nodes: list[Node]) -> list[Node]:
    """Validate responder sequence nodes based on node type.

    Validates:
    - Categoriser: requires on_result with key-value mapping to node indices
    - Forwarder: requires payload with to/cc/bcc lists; next index is optional
    - CRM_UPDATE: requires payload with fields_to_update dict; next index is optional
    - Any node can be an end node (next=None); multiple end nodes are allowed
    - If next is provided, it must be a valid node index
    - Nodes cannot reference themselves (next != current index) to prevent infinite loops

    Args:
        nodes: List of Node objects to validate

    Returns:
        Validated list of nodes

    Raises:
        ValueError: If validation fails
    """

    if not nodes:
        raise ValueError("Responder sequence must contain at least one node")

    node_count = len(nodes)
    validators = {
        NodeType.CATEGORISER: _validate_categoriser_node,
        NodeType.FORWARDER: _validate_forwarder_node,
        NodeType.CRM_UPSERT: _validate_crm_update_node,
    }

    for idx, node in enumerate(nodes):
        # Prevent self-reference which could cause infinite loops
        if node.next == idx:
            raise ValueError(f"Node at index {idx} cannot reference itself")

        validator = validators.get(node.type)

        if validator:
            validator(node, idx, node_count)
        elif node.next is not None:
            _validate_node_index(node.next, node_count, "next")

    return nodes
