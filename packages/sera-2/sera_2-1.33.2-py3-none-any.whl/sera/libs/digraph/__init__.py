"""
Digraph module for sera - A directed computing graph for business logic.

This module provides classes and utilities for building directed computing graphs
where nodes represent business logic operations and edges define data flow.

Key concepts:
- **ItemID**: Tracks item provenance across the graph, supports hierarchical IDs
- **NodeInput/NodeOutput**: Structured input/output for nodes
- **ExecutionSummary**: Records what type of operation was performed (Create, Update, etc.)
- **Context**: Read-only access to previous node outputs and global state
- **Node**: Represents a computation with a specific signature
- **Edge**: Connects nodes with optional filtering
- **Graph**: Orchestrates execution in sync or async mode
"""

from sera.libs.digraph._context import Context, LitestarContext
from sera.libs.digraph._edge import Edge
from sera.libs.digraph._execution_summary import (
    CreateSummary,
    ExecutionSummary,
    UpdateSummary,
)
from sera.libs.digraph._graph import Graph
from sera.libs.digraph._node import ComputeFn, Node
from sera.libs.digraph._node_input import NodeInput
from sera.libs.digraph._node_output import NodeOutput
from sera.libs.digraph._types import ItemID, NodeID

__all__ = [
    # Types
    "ItemID",
    "NodeID",
    # Input/Output
    "NodeInput",
    "NodeOutput",
    # Execution summaries
    "ExecutionSummary",
    "CreateSummary",
    "UpdateSummary",
    # Context
    "Context",
    "LitestarContext",
    # Node and Edge
    "Node",
    "ComputeFn",
    "Edge",
    # Graph
    "Graph",
]
