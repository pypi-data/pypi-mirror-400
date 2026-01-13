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


def make_python_get_by_id_api(
    collection: DataCollection, target_pkg: Package
) -> tuple[Module, str]:
    """Make an endpoint for querying resource by id"""
    app = target_pkg.app

    program = Program()
    import_helper = ImportHelper(program, GLOBAL_IDENTS)

    program.import_("__future__.annotations", True)
    program.import_("litestar.get", True)
    program.import_("litestar.status_codes", True)
    program.import_("litestar.exceptions.HTTPException", True)
    program.import_(
        app.logic.path
        + f".{collection.get_pymodule_name()}.search.{collection.get_search_service_name()}",
        True,
    )
    program.import_(
        app.models.data.path + f".{collection.get_pymodule_name()}.{collection.name}",
        True,
    )

    # assuming the collection has only one class
    cls = collection.cls

    # Find system_controlled properties that should be applied on search/get
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

    func_name = "get_by_id"
    program.root(
        stmt.LineBreak(),
        stmt.PythonDecoratorStatement(
            expr.ExprFuncCall(
                expr.ExprIdent("get"),
                [
                    expr.ExprConstant("/{id:%s}" % id_type),
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
            return_type=expr.ExprIdent("dict"),
            is_async=True,
        )(
            stmt.SingleExprStatement(expr.ExprConstant("Retrieving record by id")),
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
            # Generate if/else for controlled properties that don't match ID (e.g., tenant_id on User)
            *(
                [
                    stmt.LineBreak(),
                    lambda ast_if: ast_if.if_(
                        # if not (scope["state"][SKIP_UPDATE_SYSTEM_CONTROLLED_PROPS_KEY]):
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
                DeferredVar.simple("record"),
                expr.ExprAwait(
                    expr.ExprFuncCall(
                        expr.ExprIdent("service.get_by_id"),
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
            lambda ast12: ast12.if_(PredefinedFn.is_null(expr.ExprIdent("record")))(
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
            lambda ast13: ast13.return_(
                PredefinedFn.dict(
                    [
                        (
                            PredefinedFn.attr_getter(
                                expr.ExprIdent(cls.name), expr.ExprIdent("__name__")
                            ),
                            PredefinedFn.list(
                                [
                                    expr.ExprFuncCall(
                                        PredefinedFn.attr_getter(
                                            expr.ExprIdent(cls.name),
                                            expr.ExprIdent("from_db"),
                                        ),
                                        [expr.ExprIdent("record")],
                                    )
                                ]
                            ),
                        )
                    ]
                ),
            ),
        ),
    )

    outmod = target_pkg.module("get_by_id")
    outmod.write(program)

    return outmod, func_name
