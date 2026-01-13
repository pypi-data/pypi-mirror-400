from __future__ import annotations

from collections import defaultdict
from typing import Any, Generic, Sequence

from graph.retworkx import RetworkXStrDiGraph

from sera.libs.digraph._edge import Edge
from sera.libs.digraph._execution_summary import ExecutionSummary
from sera.libs.digraph._node import C, Node
from sera.libs.digraph._node_input import NodeInput
from sera.libs.digraph._node_output import NodeOutput
from sera.libs.digraph._types import NodeID
from sera.misc import is_type_compatible

# Type alias for the graph with our node and edge types
_GraphType = RetworkXStrDiGraph[int, Node[Any, C, Any], Edge]


class Graph(Generic[C]):
    """A directed computing graph for business logic.

    Uses RetworkXStrDiGraph for efficient graph operations.

    Type Parameters:
        C: The context type that all nodes in this graph must use.
           Must be a subtype of Context.

    Features:
    - No parallel edges between nodes (only one edge allowed per source-target pair)
    - Sync and async execution modes
    - Result dictionary mapping node IDs to their outputs

    Example:
        >>> from sera.libs.digraph import Graph, Node, Edge, NodeInput, NodeOutput, ItemID, NodeID
        >>>
        >>> def process(input: NodeInput, context: Context):
        ...     return NodeOutput(id=input.id, value=input.args * 2), CreateSummary()
        ...
        >>> node_a = Node(id="a", compute=process)
        >>> node_b = Node(id="b", compute=lambda inp, ctx: (NodeOutput(id=inp.id, value=inp.args + 1), CreateSummary()))
        >>> edge = Edge(source="a", target="b")
        >>>
        >>> graph: Graph[Context] = Graph.from_nodes_and_edges([node_a, node_b], [edge])
        >>> result = graph.execute({\"a\": NodeInput(id=ItemID(\"item1\"), args=5)})
    """

    _graph: _GraphType
    check_types: bool

    def __init__(
        self,
        graph: _GraphType | None = None,
        check_types: bool = True,
    ) -> None:
        """Initialize the graph.

        Args:
            graph: Optional existing graph to wrap.
            check_types: If True, validate that edge source output types
                        are compatible with target input types. Default is True.
        """
        if graph is None:
            self._graph = RetworkXStrDiGraph(check_cycle=False, multigraph=False)
        else:
            self._graph = graph
        self.check_types = check_types

    def add_node(self, node: Node[Any, C, Any]) -> None:
        """Add a node to the graph.

        Args:
            node: The node to add.

        Raises:
            ValueError: If a node with the same ID already exists.
        """
        if self._graph.has_node(node.id):
            raise ValueError(f"Node with ID '{node.id}' already exists")
        self._graph.add_node(node)

    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph.

        No parallel edges are allowed between the same source and target.

        Args:
            edge: The edge to add.

        Raises:
            ValueError: If the source or target node doesn't exist,
                       or if an edge already exists between them.
            TypeError: If check_types is True and the source output type
                      is incompatible with the target input type.
        """
        if not self._graph.has_node(edge.source):
            raise ValueError(f"Source node '{edge.source}' does not exist")
        if not self._graph.has_node(edge.target):
            raise ValueError(f"Target node '{edge.target}' does not exist")
        if self._graph.has_edge_between_nodes(edge.source, edge.target, key=0):
            raise ValueError(
                f"Edge from '{edge.source}' to '{edge.target}' already exists"
            )

        # Check type compatibility if enabled
        if self.check_types:
            source_node = self._graph.get_node(edge.source)
            target_node = self._graph.get_node(edge.target)

            if not is_type_compatible(source_node.output_type, target_node.input_type):
                raise TypeError(
                    f"Type mismatch: node '{edge.source}' outputs {source_node.output_type}, "
                    f"but node '{edge.target}' expects {target_node.input_type}"
                )

        self._graph.add_edge(edge)

    def get_node(self, node_id: NodeID) -> Node[Any, C, Any]:
        """Get a node by its ID.

        Args:
            node_id: The ID of the node to retrieve.

        Returns:
            The node with the given ID.

        Raises:
            KeyError: If no node exists with the given ID.
        """
        return self._graph.get_node(node_id)

    @staticmethod
    def from_nodes_and_edges(
        nodes: Sequence[Node[Any, C, Any]],
        edges: Sequence[Edge],
        check_types: bool = True,
    ) -> Graph[C]:
        """Construct a graph from nodes and edges.

        Args:
            nodes: The nodes to add to the graph.
            edges: The edges to add to the graph.
            check_types: If True, validate type compatibility between connected nodes. Default is True.

        Returns:
            A new Graph containing all the given nodes and edges.
        """
        graph = Graph(check_types=check_types)
        for node in nodes:
            graph.add_node(node)
        for edge in edges:
            graph.add_edge(edge)
        return graph

    def merge(self, *others: Graph[C]) -> Graph[C]:
        """Merge other graphs into this one, returning a new combined graph.

        All nodes and edges from all graphs are combined. If there are
        duplicate node IDs, a ValueError is raised. The merged graph inherits
        check_types=True if any source graph has it enabled.

        Args:
            *others: The graphs to merge with this one.

        Returns:
            A new Graph containing all nodes and edges from all graphs.

        Raises:
            ValueError: If there are duplicate node IDs between the graphs.
        """
        # Determine check_types: True if any graph has it enabled
        check_types = self.check_types or any(g.check_types for g in others)
        merged = Graph(check_types=check_types)

        # Add all nodes from this graph
        for node in self._graph.iter_nodes():
            merged.add_node(node)

        # Add all nodes from other graphs
        for other in others:
            for node in other._graph.iter_nodes():
                merged.add_node(node)

        # Add all edges from this graph
        for edge in self._graph.iter_edges():
            merged.add_edge(edge)

        # Add all edges from other graphs
        for other in others:
            for edge in other._graph.iter_edges():
                merged.add_edge(edge)

        return merged

    def execute(
        self,
        inputs: dict[NodeID, NodeInput[Any]],
        context: C,
    ) -> dict[NodeID, list[tuple[NodeOutput[Any], ExecutionSummary]]]:
        """Execute the graph synchronously.

        Triggers execution starting from the input nodes and propagates
        through the graph based on edge filters.

        Args:
            inputs: Dictionary mapping node IDs to their inputs.
            context: Context for sharing state during execution.

        Returns:
            Dictionary mapping node IDs to lists of (output, summary) tuples.
        """
        results: dict[NodeID, list[tuple[NodeOutput[Any], ExecutionSummary]]] = (
            defaultdict(list)
        )

        # Queue of (node_id, input) pairs to process
        queue: list[tuple[NodeID, NodeInput[Any]]] = [
            (node_id, inp) for node_id, inp in inputs.items()
        ]

        while queue:
            node_id, node_input = queue.pop(0)
            node = self._graph.get_node(node_id)

            # Execute the node
            assert not node.is_async
            output, summary = node.compute(node_input, context)  # type: ignore

            # Store the result
            results[node_id].append((output, summary))
            context._set_result(node_id, node_input.id, output, summary)

            # Propagate to downstream nodes
            for edge in self._graph.out_edges(node_id):
                if edge.should_propagate(output):
                    # Create input for the downstream node
                    # The output value becomes the args of the downstream node
                    downstream_input = NodeInput(id=node_input.id, args=output.value)
                    queue.append((edge.target, downstream_input))

        return dict(results)

    async def execute_async(
        self,
        inputs: dict[NodeID, NodeInput[Any]],
        context: C,
    ) -> dict[NodeID, list[tuple[NodeOutput[Any], ExecutionSummary]]]:
        """Execute the graph asynchronously.

        Triggers execution starting from the input nodes and propagates
        through the graph based on edge filters. Handles both sync and
        async compute functions.

        Args:
            inputs: Dictionary mapping node IDs to their inputs.
            context: Context for sharing state during execution.

        Returns:
            Dictionary mapping node IDs to lists of (output, summary) tuples.
        """
        results: dict[NodeID, list[tuple[NodeOutput[Any], ExecutionSummary]]] = (
            defaultdict(list)
        )

        # Queue of (node_id, input) pairs to process
        queue: list[tuple[NodeID, NodeInput[Any]]] = [
            (node_id, inp) for node_id, inp in inputs.items()
        ]

        while queue:
            node_id, node_input = queue.pop(0)
            node = self._graph.get_node(node_id)

            # Execute the node (handle both sync and async compute functions)
            if node.is_async:
                output, summary = await node.compute(node_input, context)  # type: ignore
            else:
                output, summary = node.compute(node_input, context)  # type: ignore

            # Store the result
            results[node_id].append((output, summary))
            context._set_result(node_id, node_input.id, output, summary)

            # Propagate to downstream nodes
            for edge in self._graph.out_edges(node_id):
                if edge.should_propagate(output):
                    # Create input for the downstream node
                    # The output value becomes the args of the downstream node
                    downstream_input = NodeInput(id=node_input.id, args=output.value)
                    queue.append((edge.target, downstream_input))

        return dict(results)
