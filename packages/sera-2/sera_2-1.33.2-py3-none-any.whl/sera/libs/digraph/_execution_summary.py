from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ExecutionSummary:
    """Base class for execution summaries.

    Subclasses indicate the type of operation performed by a node.
    """

    pass


@dataclass
class CreateSummary(ExecutionSummary):
    """Summary indicating an item was created."""

    pass


@dataclass
class UpdateSummary(ExecutionSummary):
    """Summary indicating an item was updated."""

    pass
