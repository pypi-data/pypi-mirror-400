from __future__ import annotations

import inspect
from typing import Any, Callable, Coroutine, Generic, TypeVar, get_args, get_type_hints

from graph.interface import BaseNode

from sera.libs.digraph._context import Context
from sera.libs.digraph._execution_summary import ExecutionSummary
from sera.libs.digraph._node_input import NodeInput
from sera.libs.digraph._node_output import NodeOutput
from sera.libs.digraph._types import NodeID

I = TypeVar("I")
O = TypeVar("O")
C = TypeVar("C", bound=Context)

# Type alias for sync compute function signature
SyncComputeFn = Callable[[NodeInput[I], C], tuple[NodeOutput[O], ExecutionSummary]]

# Type alias for async compute function signature
AsyncComputeFn = Callable[
    [NodeInput[I], C],
    Coroutine[None, None, tuple[NodeOutput[O], ExecutionSummary]],
]

# Combined type for both sync and async compute functions
ComputeFn = SyncComputeFn[I, C, O] | AsyncComputeFn[I, C, O]


class Node(BaseNode[NodeID], Generic[I, C, O]):
    """A node in the computing graph.

    The compute function takes:
    - input: NodeInput[I] containing the item ID and arguments
    - context: Context providing access to previous outputs and global state

    And returns:
    - A tuple of (NodeOutput[O], ExecutionSummary)

    Example:
        >>> def process_order(input: NodeInput[Order], context: Context) -> tuple[NodeOutput[ProcessedOrder], ExecutionSummary]:
        ...     order = input.args
        ...     result = ProcessedOrder(...)
        ...     return NodeOutput(value=result), CreateSummary()
        ...
        >>> node = Node(id="process_order", compute=process_order)
    """

    def __init__(self, id: NodeID, compute: ComputeFn[I, C, O]):
        super().__init__(id)
        self.compute = compute
        self.is_async = inspect.iscoroutinefunction(compute)
        self.input_type, self.output_type = _extract_input_output_types(compute)


def _extract_input_output_types(
    compute: ComputeFn[Any, Any, Any],
) -> tuple[type, type]:
    """Extract input and output types from compute function signature.

    Args:
        compute: The compute function to extract types from.

    Returns:
        A tuple of (input_type, output_type).

    Raises:
        TypeError: If input or output types cannot be inferred from the function signature.
    """
    func_name = getattr(compute, "__name__", repr(compute))

    try:
        hints = get_type_hints(compute)
    except Exception as e:
        raise TypeError(
            f"Cannot get type hints for compute function '{func_name}': {e}"
        ) from e

    input_type = None
    output_type = None

    # Get the first parameter's type hint (should be NodeInput[T])
    params = list(inspect.signature(compute).parameters.values())
    if params and params[0].name in hints:
        node_input_hint = hints[params[0].name]
        # Extract T from NodeInput[T]
        args = get_args(node_input_hint)
        if args:
            input_type = args[0]

    if input_type is None:
        raise TypeError(
            f"Cannot infer input type for compute function '{func_name}'. "
            f"Ensure the first parameter is typed as NodeInput[T]."
        )

    # Get return type (should be tuple[NodeOutput[O], ExecutionSummary])
    if "return" in hints:
        return_hint = hints["return"]
        return_args = get_args(return_hint)
        if return_args and len(return_args) >= 1:
            # First element should be NodeOutput[O]
            node_output_hint = return_args[0]
            output_args = get_args(node_output_hint)
            if output_args:
                output_type = output_args[0]

    if output_type is None:
        raise TypeError(
            f"Cannot infer output type for compute function '{func_name}'. "
            f"Ensure the return type is typed as tuple[NodeOutput[O], ExecutionSummary]."
        )

    return input_type, output_type
