from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from sera.libs.digraph._types import ItemID

O = TypeVar("O")


@dataclass
class NodeOutput(Generic[O]):
    """Output from a node in the graph.

    The `id` field tracks item provenance, matching the input ItemID
    that this output was produced from.
    """

    id: ItemID
    value: O
