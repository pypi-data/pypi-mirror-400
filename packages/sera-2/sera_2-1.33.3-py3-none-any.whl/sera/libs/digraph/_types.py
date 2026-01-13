from __future__ import annotations

from typing import NewType, TypeAlias

# ItemID supports hierarchical IDs using "." separator for nested item structures
# Example: "order.123" or "order.123.item.456"
ItemID = NewType("ItemID", str)

# NodeID identifies a node in the graph (type alias for str to work with RetworkXStrDiGraph)
NodeID: TypeAlias = str
