from __future__ import annotations

from codegen.models import DeferredVar, PredefinedFn, Program, expr, stmt

from sera.misc import assert_not_null
from sera.models import DataCollection, Package


def make_python_create_logic(collection: DataCollection, target_pkg: Package):
    """Generate a create logic module for a collection.

    This generates an async create function that:
    - Takes NodeInput[Model] and LitestarContext as parameters
    - Returns tuple[NodeOutput[Model], CreateSummary]
    - Handles IntegrityError from database operations
    """
    app = target_pkg.app

    outmod = target_pkg.pkg(collection.get_pymodule_name()).module("create")

    # assuming the collection has only one class
    cls = collection.cls
    id_prop = assert_not_null(cls.get_id_property())

    program = Program()
    program.import_("__future__.annotations", True)
    program.import_("litestar.exceptions.HTTPException", True)
    program.import_(
        "sera.libs.digraph.CreateSummary",
        True,
    )
    program.import_(
        "sera.libs.digraph.LitestarContext",
        True,
    )
    program.import_(
        "sera.libs.digraph.NodeInput",
        True,
    )
    program.import_(
        "sera.libs.digraph.NodeOutput",
        True,
    )
    program.import_("litestar.status_codes", True)
    program.import_("sqlalchemy.exc.IntegrityError", True)
    program.import_(
        app.models.db.path + f".{collection.get_pymodule_name()}.{cls.name}",
        True,
    )

    program.root(
        stmt.LineBreak(),
        lambda ast00: ast00.func(
            "create",
            [
                DeferredVar.simple(
                    "input",
                    expr.ExprIdent(f"NodeInput[{cls.name}]"),
                ),
                DeferredVar.simple(
                    "context",
                    expr.ExprIdent("LitestarContext"),
                ),
            ],
            return_type=expr.ExprIdent(f"tuple[NodeOutput[{cls.name}], CreateSummary]"),
            is_async=True,
        )(
            # record = input.args
            lambda ast01: ast01.assign(
                DeferredVar.simple("record"),
                expr.ExprIdent("input.args"),
            ),
            # session = context.session
            lambda ast02: ast02.assign(
                DeferredVar.simple("session"),
                expr.ExprIdent("context.session"),
            ),
            stmt.LineBreak(),
            # record.id = None  # type: ignore - Ensure id is None for new record
            stmt.PythonStatement(
                f"record.{id_prop.name} = None  # type: ignore - Ensure id is None for new record"
            ),
            stmt.LineBreak(),
            # try block
            lambda ast03: ast03.try_()(
                # session.add(record)
                stmt.SingleExprStatement(
                    expr.ExprMethodCall(
                        expr.ExprIdent("session"),
                        "add",
                        [expr.ExprIdent("record")],
                    )
                ),
                # await session.flush()
                stmt.SingleExprStatement(
                    expr.ExprAwait(
                        expr.ExprMethodCall(
                            expr.ExprIdent("session"),
                            "flush",
                            [],
                        )
                    )
                ),
            ),
            # except IntegrityError
            lambda ast04: ast04.catch(expr.ExprIdent("IntegrityError"))(
                stmt.PythonStatement(
                    'raise HTTPException(detail="Invalid request", status_code=status_codes.HTTP_409_CONFLICT)'
                ),
            ),
            stmt.LineBreak(),
            # return NodeOutput(id=input.id, value=record), CreateSummary()
            lambda ast05: ast05.return_(
                PredefinedFn.tuple(
                    [
                        expr.ExprFuncCall(
                            expr.ExprIdent("NodeOutput"),
                            [
                                PredefinedFn.keyword_assignment(
                                    "id", expr.ExprIdent("input.id")
                                ),
                                PredefinedFn.keyword_assignment(
                                    "value", expr.ExprIdent("record")
                                ),
                            ],
                        ),
                        expr.ExprFuncCall(
                            expr.ExprIdent("CreateSummary"),
                            [],
                        ),
                    ]
                )
            ),
        ),
    )

    outmod.write(program)
