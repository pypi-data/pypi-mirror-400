from __future__ import annotations

from typing import TypedDict

from codegen.models import PredefinedFn, expr

from sera.models._property import GetSCPropValueFunc


class AvailableVars(TypedDict, total=False):
    self: expr.Expr
    user: expr.Expr


def get_controlled_property_value(
    update_func: GetSCPropValueFunc,
    available_vars: AvailableVars,
) -> expr.Expr:
    if update_func.func == "getattr":
        if update_func.args[0] == "user":
            if len(update_func.args) != 2:
                raise NotImplementedError(
                    f"Unsupported update function: {update_func.func} with args {update_func.args}"
                )

            return PredefinedFn.attr_getter(
                available_vars["user"], expr.ExprIdent(update_func.args[1])
            )
        elif update_func.args[0] == "self":
            return PredefinedFn.attr_getter(
                available_vars["self"], expr.ExprIdent(update_func.args[1])
            )
        else:
            raise NotImplementedError(
                f"Unsupported update function: {update_func.func} with args {update_func.args}"
            )
    else:
        raise NotImplementedError(update_func.func)
