from __future__ import annotations

from codegen.models import DeferredVar, ImportHelper, PredefinedFn, Program, expr, stmt

from sera.make.py_backend.system_controlled_property import (
    AvailableVars,
    get_controlled_property_value,
)
from sera.misc import assert_not_null
from sera.models import DataCollection, Module, Package
from sera.typing import GLOBAL_IDENTS


def make_python_update_api(
    collection: DataCollection, target_pkg: Package
) -> tuple[Module, str]:
    """Make an endpoint for updating resource using the graph API"""
    app = target_pkg.app

    program = Program()
    import_helper = ImportHelper(program, GLOBAL_IDENTS)

    program.import_("__future__.annotations", True)
    program.import_("litestar.put", True)
    program.import_("sera.libs.digraph.ItemID", True)
    program.import_("sera.libs.digraph.LitestarContext", True)
    program.import_("sera.libs.digraph.NodeInput", True)
    program.import_(
        f"{app.logic.path}.digraph.graph",
        True,
    )
    program.import_(
        app.models.data.path
        + f".{collection.get_pymodule_name()}.Update{collection.name}",
        True,
    )

    # assuming the collection has only one class
    cls = collection.cls
    id_prop = assert_not_null(cls.get_id_property())
    id_type = id_prop.datatype.get_python_type().type
    collection_module = collection.get_pymodule_name()
    node_id = f"{collection_module}.update"

    update_controlled_props = [
        prop
        for prop in cls.properties.values()
        if prop.data.system_controlled is not None
        and prop.data.system_controlled.is_on_update_value_updated()
    ]
    if len(update_controlled_props) > 0:
        program.import_("sera.libs.api_helper.SingleAutoUSCP", True)

    # Check if any controlled property is the ID property itself
    # In this case, we have to reject the request if the ID doesn't match
    is_id_controlled = any(
        prop.name == id_prop.name for prop in update_controlled_props
    )
    if is_id_controlled:
        program.import_("litestar.exceptions.HTTPException", True)
        program.import_("litestar.status_codes", True)
        program.import_(
            "sera.libs.api_helper.SKIP_UPDATE_SYSTEM_CONTROLLED_PROPS_KEY", True
        )
        program.import_("litestar.types.Scope", True)

    available_controlled_prop_vars: AvailableVars = {
        "user": PredefinedFn.item_getter(
            expr.ExprIdent("scope"),
            expr.ExprConstant("user"),
        )
    }

    func_name = "update"

    program.root(
        stmt.LineBreak(),
        stmt.PythonDecoratorStatement(
            expr.ExprFuncCall(
                expr.ExprIdent("put"),
                [
                    expr.ExprConstant("/{id:%s}" % id_type),
                ]
                + (
                    [
                        PredefinedFn.keyword_assignment(
                            "dto",
                            PredefinedFn.item_getter(
                                expr.ExprIdent("SingleAutoUSCP"),
                                expr.ExprIdent(f"Update{cls.name}"),
                            ),
                        )
                    ]
                    if len(update_controlled_props) > 0
                    else []
                ),
            )
        ),
        lambda ast10: ast10.func(
            func_name,
            [
                DeferredVar.simple(
                    "id",
                    expr.ExprIdent(id_type),
                ),
                DeferredVar.simple(
                    "data",
                    expr.ExprIdent(f"Update{cls.name}"),
                ),
                DeferredVar.simple(
                    "session",
                    import_helper.use("AsyncSession"),
                ),
                DeferredVar.simple("scope", expr.ExprIdent("Scope"))
                if is_id_controlled
                else None,
            ],
            return_type=expr.ExprIdent(id_prop.datatype.get_python_type().type),
            is_async=True,
        )(
            stmt.SingleExprStatement(expr.ExprConstant("Update an existing record")),
            *(
                [
                    stmt.LineBreak(),
                    lambda ast_if: ast_if.if_(
                        # if not scope["state"][SKIP_UPDATE_SYSTEM_CONTROLLED_PROPS_KEY]:
                        expr.ExprNegation(
                            PredefinedFn.item_getter(
                                PredefinedFn.item_getter(
                                    expr.ExprIdent("scope"),
                                    expr.ExprConstant("state"),
                                ),
                                expr.ExprIdent(
                                    "SKIP_UPDATE_SYSTEM_CONTROLLED_PROPS_KEY"
                                ),
                            )
                        )
                    )(
                        # if scope["user"].tenant_id != id:
                        lambda ast_inner_if: ast_inner_if.if_(
                            expr.ExprNotEqual(
                                get_controlled_property_value(
                                    assert_not_null(
                                        id_prop.data.system_controlled
                                    ).get_on_search_update_func(),
                                    available_controlled_prop_vars,
                                ),
                                expr.ExprIdent("id"),
                            )
                        )(
                            lambda ast_raise: ast_raise.raise_exception(
                                expr.StandardExceptionExpr(
                                    expr.ExprIdent("HTTPException"),
                                    [
                                        PredefinedFn.keyword_assignment(
                                            "status_code",
                                            expr.ExprIdent(
                                                "status_codes.HTTP_404_NOT_FOUND"
                                            ),
                                        ),
                                        PredefinedFn.keyword_assignment(
                                            "detail",
                                            expr.ExprIdent(
                                                'f"Record with id {id} not found"'
                                            ),
                                        ),
                                    ],
                                )
                            )
                        ),
                    ),
                    stmt.LineBreak(),
                ]
                if is_id_controlled
                else []
            ),
            # data.id = id
            stmt.SingleExprStatement(
                PredefinedFn.attr_setter(
                    expr.ExprIdent("data"),
                    expr.ExprIdent(id_prop.name),
                    expr.ExprIdent("id"),
                )
            ),
            # context = LitestarContext(session=session)
            lambda ast100: ast100.assign(
                DeferredVar.simple("context"),
                expr.ExprFuncCall(
                    expr.ExprIdent("LitestarContext"),
                    [
                        PredefinedFn.keyword_assignment(
                            "session", expr.ExprIdent("session")
                        ),
                    ],
                ),
            ),
            # input = NodeInput(id=ItemID("0"), args=data.to_db())
            lambda ast101: ast101.assign(
                DeferredVar.simple("input"),
                expr.ExprFuncCall(
                    expr.ExprIdent("NodeInput"),
                    [
                        PredefinedFn.keyword_assignment(
                            "id",
                            expr.ExprFuncCall(
                                expr.ExprIdent("ItemID"),
                                [expr.ExprConstant("0")],
                            ),
                        ),
                        PredefinedFn.keyword_assignment(
                            "args",
                            expr.ExprMethodCall(expr.ExprIdent("data"), "to_db", []),
                        ),
                    ],
                ),
            ),
            # result = await graph.execute_async({"<node_id>": input}, context)
            lambda ast102: ast102.assign(
                DeferredVar.simple("result"),
                expr.ExprAwait(
                    expr.ExprMethodCall(
                        expr.ExprIdent("graph"),
                        "execute_async",
                        [
                            PredefinedFn.dict(
                                [
                                    (
                                        expr.ExprConstant(node_id),
                                        expr.ExprIdent("input"),
                                    )
                                ]
                            ),
                            expr.ExprIdent("context"),
                        ],
                    )
                ),
            ),
            # return result["<node_id>"][0][0].value.id
            lambda ast103: ast103.return_(
                PredefinedFn.attr_getter(
                    PredefinedFn.attr_getter(
                        PredefinedFn.item_getter(
                            PredefinedFn.item_getter(
                                PredefinedFn.item_getter(
                                    expr.ExprIdent("result"),
                                    expr.ExprConstant(node_id),
                                ),
                                expr.ExprConstant(0),
                            ),
                            expr.ExprConstant(0),
                        ),
                        expr.ExprIdent("value"),
                    ),
                    expr.ExprIdent(id_prop.name),
                )
            ),
        ),
    )

    outmod = target_pkg.module("update")
    outmod.write(program)

    return outmod, func_name
