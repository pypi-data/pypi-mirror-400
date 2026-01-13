from __future__ import annotations

from codegen.models import DeferredVar, Program, expr, stmt

from sera.misc import assert_not_null
from sera.models import DataCollection, Package


def make_python_search_logic(collection: DataCollection, target_pkg: Package):
    app = target_pkg.app

    outmod = target_pkg.pkg(collection.get_pymodule_name()).module("search")

    # assuming the collection has only one class
    cls = collection.cls
    id_type = assert_not_null(cls.get_id_property()).datatype.get_python_type().type

    program = Program()
    program.import_("__future__.annotations", True)
    program.import_(
        app.models.db.path + f".{collection.name}",
        True,
    )
    program.import_(app.config.path + f".schema", True)
    program.import_("sera.libs.base_search.BaseAsyncSearchService", True)
    program.import_(app.models.db.path + ".dbschema", True)

    program.root(
        stmt.LineBreak(),
        lambda ast00: ast00.class_(
            collection.get_search_service_name(),
            [expr.ExprIdent(f"BaseAsyncSearchService[{id_type}, {cls.name}]")],
        )(
            lambda ast01: ast01.func(
                "__init__",
                [
                    DeferredVar.simple("self"),
                ],
            )(
                lambda ast02: ast02.expr(
                    expr.ExprFuncCall(
                        expr.ExprIdent("super().__init__"),
                        [
                            expr.ExprRawPython(f"schema.classes['{cls.name}']"),
                            expr.ExprIdent("dbschema"),
                        ],
                    )
                ),
            ),
        ),
    )
    outmod.write(program)
