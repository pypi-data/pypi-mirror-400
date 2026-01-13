from __future__ import annotations

from codegen.models import DeferredVar, ImportHelper, PredefinedFn, Program, expr, stmt

from sera.make.py_backend.misc import get_python_property_name
from sera.make.py_backend.system_controlled_property import (
    AvailableVars,
    get_controlled_property_value,
)
from sera.misc import assert_not_null
from sera.models import DataCollection, Module, Package
from sera.typing import GLOBAL_IDENTS


def make_python_has_api(
    collection: DataCollection, target_pkg: Package
) -> tuple[Module, str]:
    """Make an endpoint for querying resource by id"""
    app = target_pkg.app

    program = Program()
    import_helper = ImportHelper(program, GLOBAL_IDENTS)

    program.import_("__future__.annotations", True)
    program.import_("litestar.head", True)
    program.import_("litestar.status_codes", True)
    program.import_("litestar.exceptions.HTTPException", True)
    program.import_(
        app.logic.path
        + f".{collection.get_pymodule_name()}.search.{collection.get_search_service_name()}",
        True,
    )

    # Find system_controlled properties that should be applied on search/has
    search_controlled_props = [
        prop
        for prop in collection.cls.properties.values()
        if prop.data.system_controlled is not None
        and prop.data.system_controlled.is_on_search_value_updated()
    ]
    if len(search_controlled_props) > 0:
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

    # assuming the collection has only one class
    cls = collection.cls
    id_prop = assert_not_null(cls.get_id_property())
    id_type = id_prop.datatype.get_python_type().type

    # Check if any controlled property is the ID property itself
    # In this case, we compare the user's value directly with the ID parameter
    is_id_controlled = any(
        prop.name == id_prop.name for prop in search_controlled_props
    )
    search_controlled_props = [
        prop for prop in search_controlled_props if prop.name != id_prop.name
    ]

    func_name = "has"
    program.root(
        stmt.LineBreak(),
        stmt.PythonDecoratorStatement(
            expr.ExprFuncCall(
                expr.ExprIdent("head"),
                [
                    expr.ExprConstant("/{id:%s}" % id_type),
                    PredefinedFn.keyword_assignment(
                        "status_code",
                        expr.ExprIdent("status_codes.HTTP_204_NO_CONTENT"),
                    ),
                ],
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
                    "session",
                    import_helper.use("AsyncSession"),
                ),
                DeferredVar.simple("scope", expr.ExprIdent("Scope"))
                if len(search_controlled_props) > 0 or is_id_controlled
                else None,
            ],
            return_type=expr.ExprConstant(None),
            is_async=True,
        )(
            stmt.SingleExprStatement(
                expr.ExprConstant("Checking if record exists by id")
            ),
            lambda ast100: ast100.assign(
                DeferredVar.simple("service"),
                expr.ExprFuncCall(
                    PredefinedFn.attr_getter(
                        expr.ExprIdent(collection.get_search_service_name()),
                        expr.ExprIdent("get_instance"),
                    ),
                    [],
                ),
            ),
            # Generate code for controlled properties that match the ID
            # These compare user's value directly with the id parameter
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
            # Generate if/else for controlled properties (e.g., tenant_id)
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
                        # e.g., tenant_id = scope["user"].tenant_id
                        *[
                            lambda ast_then: ast_then.assign(
                                DeferredVar.simple(get_python_property_name(prop)),
                                get_controlled_property_value(
                                    assert_not_null(
                                        prop.data.system_controlled
                                    ).get_on_search_update_func(),
                                    available_controlled_prop_vars,
                                ),
                            )
                            for prop in search_controlled_props
                        ]
                    ),
                    lambda ast_else: ast_else.else_()(
                        # e.g., tenant_id = None
                        *[
                            lambda ast_else: ast_else.assign(
                                DeferredVar.simple(get_python_property_name(prop)),
                                expr.ExprConstant(None),
                            )
                            for prop in search_controlled_props
                        ]
                    ),
                    stmt.LineBreak(),
                ]
                if len(search_controlled_props) > 0
                else []
            ),
            lambda ast11: ast11.assign(
                DeferredVar.simple("record_exist"),
                expr.ExprAwait(
                    expr.ExprFuncCall(
                        expr.ExprIdent("service.has_id"),
                        [
                            expr.ExprIdent("session"),
                            expr.ExprIdent("id"),
                        ]
                        + [
                            PredefinedFn.keyword_assignment(
                                get_python_property_name(prop),
                                expr.ExprIdent(get_python_property_name(prop)),
                            )
                            for prop in search_controlled_props
                        ],
                    )
                ),
            ),
            lambda ast12: ast12.if_(expr.ExprNegation(expr.ExprIdent("record_exist")))(
                lambda ast23: ast23.raise_exception(
                    expr.StandardExceptionExpr(
                        expr.ExprIdent("HTTPException"),
                        [
                            PredefinedFn.keyword_assignment(
                                "status_code",
                                expr.ExprIdent("status_codes.HTTP_404_NOT_FOUND"),
                            ),
                            PredefinedFn.keyword_assignment(
                                "detail",
                                expr.ExprIdent('f"Record with id {id} not found"'),
                            ),
                        ],
                    )
                )
            ),
            lambda ast13: ast13.return_(expr.ExprConstant(None)),
        ),
    )

    outmod = target_pkg.module("has")
    outmod.write(program)

    return outmod, func_name
