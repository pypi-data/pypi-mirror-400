from __future__ import annotations

from typing import Any, Callable

from graph.interface import BaseEdge

from sera.libs.digraph._node_output import NodeOutput
from sera.libs.digraph._types import NodeID


class Edge(BaseEdge[NodeID, int]):
    """An edge connecting two nodes in the graph.

    The filter function determines whether to propagate execution to the target node.
    If None (default), the edge always propagates.

    Args:
        source: The NodeID of the source node.
        target: The NodeID of the target node.
        filter_fn: Optional function that takes a NodeOutput and returns True
                   if execution should propagate to the target node.

    Example:
        >>> # Always propagate (default)
        >>> edge = Edge(source=NodeID("a"), target=NodeID("b"))
        >>>
        >>> # Only propagate if output value is positive
        >>> edge = Edge(
        ...     source=NodeID("a"),
        ...     target=NodeID("b"),
        ...     filter_fn=lambda output: output.value > 0
        ... )
    """

    def __init__(
        self,
        source: NodeID,
        target: NodeID,
        filter_fn: Callable[[NodeOutput[Any]], bool] | None = None,
        id: int = -1,
    ):
        # key=0 since we don't allow parallel edges
        super().__init__(id, source, target, key=0)
        self.filter_fn = filter_fn

    def should_propagate(self, output: NodeOutput[Any]) -> bool:
        """Check if execution should propagate through this edge.

        Args:
            output: The output from the source node.

        Returns:
            True if execution should propagate to the target, False otherwise.
        """
        if self.filter_fn is None:
            return True
        return self.filter_fn(output)
