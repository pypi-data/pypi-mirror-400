from __future__ import annotations

import os
from pathlib import Path
from pydoc import doc
from typing import Annotated

from codegen.models import DeferredVar, PredefinedFn, Program, expr, stmt

from sera.make.make_typescript_model import make_typescript_data_model
from sera.make.py_backend import (
    make_python_api,
    make_python_data_model,
    make_python_enums,
    make_python_logic,
    make_python_relational_model,
)
from sera.make.ts_frontend.make_enums import make_typescript_enums
from sera.misc import CacheCleaner, FileWriter, check_clean_repo_or_token
from sera.models import App, DataCollection, parse_schema
from sera.typing import Language


def make_config(app: App):
    """Make the configuration for the application."""
    program = Program()
    program.import_("__future__.annotations", True)
    program.import_("os", False)
    program.import_("serde.yaml", False)
    program.import_("pathlib.Path", True)
    program.import_("sera.models.parse_schema", True)

    program.root(
        lambda ast: ast.if_(
            PredefinedFn.not_has_item(
                expr.ExprIdent("os.environ"), expr.ExprConstant("CFG_FILE")
            )
        )(
            lambda ast01: ast01.assign(
                DeferredVar.simple("CFG_FILE"),
                expr.ExprRawPython("Path(__file__).parent.parent / 'config.yml'"),
            ),
        ),
        lambda ast: ast.else_()(
            lambda ast01: ast01.assign(
                DeferredVar.simple("CFG_FILE"),
                expr.ExprRawPython('Path(os.environ["CFG_FILE"])'),
            ),
        ),
        lambda ast: ast.assign(
            DeferredVar.simple("cfg"),
            expr.ExprFuncCall(
                expr.ExprIdent("serde.yaml.deser"), [expr.ExprIdent("CFG_FILE")]
            ),
        ),
        stmt.LineBreak(),
        lambda ast: ast.assign(
            DeferredVar.simple("DB_CONNECTION"),
            expr.ExprIdent("cfg['db']['connection']"),
        ),
        lambda ast: ast.assign(
            DeferredVar.simple("DB_DEBUG"),
            expr.ExprIdent('os.environ.get("DB_DEBUG", "0") == "1"'),
        ),
        lambda ast: ast.assign(
            DeferredVar.simple("API_DEBUG"),
            expr.ExprIdent('os.environ.get("API_DEBUG", "0") == "1"'),
        ),
        stmt.LineBreak(),
        lambda ast: ast.assign(
            DeferredVar.simple("PKG_DIR"),
            expr.ExprRawPython("Path(__file__).parent"),
        ),
        lambda ast: ast.assign(
            DeferredVar.simple("SCHEMA_DIR"),
            expr.ExprRawPython("PKG_DIR.parent / 'schema'"),
        ),
        lambda ast: ast.assign(
            DeferredVar.simple("schema"),
            expr.ExprFuncCall(
                expr.ExprIdent("parse_schema"),
                [
                    expr.ExprConstant(app.name),
                    PredefinedFn.list(
                        [
                            expr.ExprDivision(
                                expr.ExprIdent("SCHEMA_DIR"),
                                expr.ExprConstant(
                                    os.path.relpath(
                                        path.absolute(), app.root.dir.parent / "schema"
                                    )
                                ),
                            )
                            for path in app.schema_files
                        ]
                    ),
                ],
            ),
        ),
    )

    app.config.write(program)


def make_app(
    app_dir: Annotated[
        Path,
        doc("Directory of the generated application"),
    ],
    schema_files: Annotated[
        list[Path],
        doc("YAML schema files. Multiple files are merged automatically"),
    ],
    api_collections: Annotated[
        list[str],
        doc("API collections to generate."),
    ],
    language: Annotated[
        Language,
        doc(
            "Language of the generated application. Currently only Python is supported."
        ),
    ] = Language.Python,
    referenced_schema: Annotated[
        list[str],
        doc(
            "Classes in the schema that are defined in different modules, used as references and thus should not be generated."
        ),
    ] = [],
    allow_dirty_repo: Annotated[
        bool,
        doc(
            "Allow code generation in a repo with uncommitted changes (by default, clean repo is enforced)"
        ),
    ] = False,
    session_token: Annotated[
        str | None,
        doc(
            "Token filename for parallel runs. If the token file exists, version control checks are skipped."
        ),
    ] = None,
):
    # Perform version control safety check before code generation
    check_clean_repo_or_token(app_dir, session_token, allow_dirty_repo)

    schema = parse_schema(app_dir.name, schema_files)

    app = App(app_dir.name, app_dir, schema_files, language)

    if language == Language.Python:
        # generate application configuration
        make_config(app)

        # generate models from schema
        # TODO: fix me, this is a hack to make the code work for referenced classes
        referenced_classes = {
            path.rsplit(".", 1)[1]: (parts := path.rsplit(".", 1))[0]
            + ".data."
            + parts[1]
            for path in referenced_schema
        }

        make_python_enums(schema, app.models.pkg("enums"), referenced_classes)
        make_python_data_model(schema, app.models.pkg("data"), referenced_classes)
        referenced_classes = {
            path.rsplit(".", 1)[1]: (parts := path.rsplit(".", 1))[0]
            + ".db."
            + parts[1]
            for path in referenced_schema
        }
        make_python_relational_model(
            schema,
            app.models.pkg("db"),
            app.models.pkg("data"),
            referenced_classes,
        )

        collections = [
            DataCollection(schema.classes[cname]) for cname in api_collections
        ]

        # generate API
        make_python_api(app, collections)

        # generate logic
        make_python_logic(app, collections)
    elif language == Language.Typescript:
        make_typescript_enums(schema, app.models)
        make_typescript_data_model(schema, app.models)

    FileWriter.get_instance().process()
    CacheCleaner(app_dir).cleanup()
    return app


if __name__ == "__main__":
    make_app(
        Path("/Volumes/research/workspace/libs/sera/tests/resources/myapp"),
        [
            Path(
                "/Volumes/research/workspace/libs/sera/tests/resources/schema/product.yml"
            )
        ],
        ["Product", "Category"],
    )
