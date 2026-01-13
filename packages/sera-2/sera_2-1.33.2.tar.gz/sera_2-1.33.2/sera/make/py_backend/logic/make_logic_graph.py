from __future__ import annotations

from typing import Sequence

from codegen.models import PredefinedFn, Program, expr, stmt

from sera.models import App, DataCollection


def make_python_logic_graph(app: App, collections: Sequence[DataCollection]):
    """Generate the digraph.py file that creates a Graph with Node elements for each collection.

    This generates a file that:
    - Imports Graph and Node from sera.libs.digraph
    - Imports create and update functions from each collection's logic module
    - Creates a graph variable with all nodes registered
    """
    program = Program()
    program.import_("__future__.annotations", True)
    program.import_("sera.libs.digraph.Graph", True)
    program.import_("sera.libs.digraph.Node", True)

    # Import create and update functions from each collection
    nodes: list[expr.Expr] = []
    for collection in collections:
        collection_module = collection.get_pymodule_name()

        # Import create function
        program.import_(
            f"{app.logic.path}.{collection_module}.create.create",
            True,
            alias=f"{collection_module}_create",
        )
        # Import update function
        program.import_(
            f"{app.logic.path}.{collection_module}.update.update",
            True,
            alias=f"{collection_module}_update",
        )

        # Create Node entries
        nodes.append(
            expr.ExprFuncCall(
                expr.ExprIdent("Node"),
                [
                    expr.ExprConstant(f"{collection_module}.create"),
                    expr.ExprIdent(f"{collection_module}_create"),
                ],
            )
        )
        nodes.append(
            expr.ExprFuncCall(
                expr.ExprIdent("Node"),
                [
                    expr.ExprConstant(f"{collection_module}.update"),
                    expr.ExprIdent(f"{collection_module}_update"),
                ],
            )
        )

    program.root(
        stmt.LineBreak(),
        stmt.AssignStatement(
            expr.ExprIdent("graph"),
            expr.ExprFuncCall(
                expr.ExprIdent("Graph.from_nodes_and_edges"),
                [
                    PredefinedFn.keyword_assignment(
                        "nodes",
                        PredefinedFn.list(nodes),
                    ),
                    PredefinedFn.keyword_assignment(
                        "edges",
                        PredefinedFn.list([]),
                    ),
                ],
            ),
        ),
    )

    outmod = app.logic.module("digraph")
    outmod.write(program)
