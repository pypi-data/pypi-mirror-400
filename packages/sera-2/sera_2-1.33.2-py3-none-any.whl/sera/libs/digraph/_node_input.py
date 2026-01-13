from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from sera.libs.digraph._types import ItemID

T = TypeVar("T")


@dataclass
class NodeInput(Generic[T]):
    """Input to a node in the graph.

    The `id` field tracks item provenance across the graph, enabling:
    - Joining outputs from multiple nodes processing the same item
    - Hierarchical IDs using "." separator for nested item structures

    Example:
        >>> NodeInput(id=ItemID("order.123"), args=order_data)
        >>> NodeInput(id=ItemID("order.123.item.0"), args=item_data)
    """

    id: ItemID
    args: T
