from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sera.libs.digraph._execution_summary import ExecutionSummary
from sera.libs.digraph._node_output import NodeOutput
from sera.libs.digraph._types import ItemID, NodeID

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class Context:
    """Read-only context available during node execution.

    Provides access to:
    - Global variables (e.g., database sessions)
    - Previous node outputs and execution summaries

    This is the base context class. Subclass for specific use cases
    (e.g., LitestarContext for Litestar API handlers).
    """

    def __init__(
        self,
        outputs: dict[tuple[NodeID, ItemID], NodeOutput[Any]] | None = None,
        summaries: dict[tuple[NodeID, ItemID], ExecutionSummary] | None = None,
    ):
        self._outputs = outputs or {}
        self._summaries = summaries or {}

    def get_output_exec_summary(
        self, node_id: NodeID, input_id: ItemID
    ) -> ExecutionSummary:
        """Get the execution summary from a previous node for a given input ID.

        Args:
            node_id: The ID of the node whose summary to retrieve.
            input_id: The ItemID of the input that was processed.

        Returns:
            The ExecutionSummary from the specified node for the given input.

        Raises:
            KeyError: If no summary exists for the given node_id and input_id.
        """
        return self._summaries[(node_id, input_id)]

    def get_output(self, node_id: NodeID, input_id: ItemID) -> NodeOutput[Any]:
        """Get the output from a previous node for a given input ID.

        Args:
            node_id: The ID of the node whose output to retrieve.
            input_id: The ItemID of the input that was processed.

        Returns:
            The NodeOutput from the specified node for the given input.

        Raises:
            KeyError: If no output exists for the given node_id and input_id.
        """
        return self._outputs[(node_id, input_id)]

    def _set_result(
        self,
        node_id: NodeID,
        input_id: ItemID,
        output: NodeOutput[Any],
        summary: ExecutionSummary,
    ) -> None:
        """Internal method to store a node's result.

        This should only be called by the Graph during execution.
        """
        self._outputs[(node_id, input_id)] = output
        self._summaries[(node_id, input_id)] = summary


class LitestarContext(Context):
    """Context for Litestar + SQLAlchemy API request handlers.

    This context is only valid during a Litestar backend API request.
    It provides access to the SQLAlchemy AsyncSession for database operations.
    """

    def __init__(
        self,
        session: AsyncSession,
        outputs: dict[tuple[NodeID, ItemID], NodeOutput[Any]] | None = None,
        summaries: dict[tuple[NodeID, ItemID], ExecutionSummary] | None = None,
    ):
        super().__init__(outputs, summaries)
        self.session = session
