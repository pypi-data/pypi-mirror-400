import sys
from typing import ClassVar, Literal
from pydantic import BaseModel
import sympy
from sympy import (
    Ge,
    Gt,
    Le,
    Lt,
    Ne,
    Not,
    Symbol,
    Eq,
    Or,
    And,
    simplify,
    simplify_logic,
    SOPform,
)
from sympy.logic.boolalg import Boolean


class SympyToSqlHelper:
    columns: list[str]

    @staticmethod
    def to_sql_where(expr: Boolean) -> str:
        # expr = simplify_logic(expr=expr, form="dnf")
        return SympyToSqlHelper._to_sql_impl(expr)

    @staticmethod
    def _to_sql_impl(expr: Boolean) -> str:
        """
        Recursively translates a Sympy expression into a sql where clause.
        """
        # --- Logical Operators ---
        conv = [SympyToSqlHelper._to_sql_impl(arg) for arg in expr.args]

        if isinstance(expr, And):
            return f"( {' AND '.join(conv)} )"

        if isinstance(expr, Or):
            return f"( {' OR '.join(conv)} )"

        if isinstance(expr, Not):
            return f" NOT {conv[0]} "

        # --- Comparison Operators ---
        if isinstance(expr, Eq):
            return f" {conv[0]}={conv[1]} "
        if isinstance(expr, Ne):
            return f" {conv[0]}<>{conv[1]} "
        if isinstance(expr, Ge):
            return f" {conv[0]}>={conv[1]} "
        if isinstance(expr, Gt):
            return f" {conv[0]}>{conv[1]} "
        if isinstance(expr, Lt):
            return f" {conv[0]}<{conv[1]} "
        if isinstance(expr, Le):
            return f" {conv[0]}<={conv[1]} "

        # --- Base Cases (End of Recursion) ---
        if isinstance(expr, Symbol):
            name = str(expr)
            if name in SympyToSqlHelper.columns:
                return f'"{name}"'
            else:
                return f"'{name}'"

        if isinstance(expr, sympy.core.numbers.Number):
            return f"{float(expr)}"

        raise TypeError(f"Unknown Sympy type to convert: {type(expr)}")


class SympyContainer(BaseModel):
    feat_name: str
    operator: Literal["=", "<", "<=", ">", ">=", "!=", "not in", "in", "between"]
    value: str | int | float | list[str] | list[int] | list[float]
    assumptions: dict[str, bool]
    feature_symbol_map: ClassVar[dict[str, Symbol]] = {}
    feature_value_symbol_map: ClassVar[dict[str, dict[int | str, Symbol]]] = {}

    @staticmethod
    def get_value_symbol(feature_name: str, value) -> Symbol | int:
        if isinstance(value, int):
            return value
        return SympyContainer.feature_value_symbol_map.setdefault(
            feature_name, {}
        ).setdefault(value, Symbol(value))

    @staticmethod
    def get_symbol(
        feature_name: str, assumptions: dict[str, bool] | None = None
    ) -> Symbol:
        assumptions = assumptions if assumptions is not None else {}
        return SympyContainer.feature_symbol_map.setdefault(
            feature_name, Symbol(feature_name, **assumptions)
        )

    def get_sympy(self) -> Boolean:
        x = self.get_symbol(self.feat_name, self.assumptions)

        match self.operator:
            case "=":
                return Eq(x, self.get_value_symbol(self.feat_name, self.value))
            case "!=":
                return Ne(x, self.get_value_symbol(self.feat_name, self.value))
            case "in":
                return Or(
                    *[
                        Eq(x, self.get_value_symbol(self.feat_name, value))
                        for value in self.value
                    ]
                )
            case "not in":
                return Not(
                    Or(
                        *[
                            Eq(x, self.get_value_symbol(self.feat_name, value))
                            for value in self.value
                        ]
                    )
                )
            case "<":
                return Lt(x, self.value)
            case "<=":
                return Le(x, self.value)
            case ">":
                return Gt(x, self.value)
            case ">=":
                return Ge(x, self.value)
            case "between":
                return And(Gt(x, self.value[0]), Le(x, self.value[1]))
        raise NotImplementedError(f"{self.operator} not implemented.")


class Filter:
    def __init__(self, combine: Boolean):
        self.combine = combine

    def sql(self, do_invert: bool = False) -> str:
        combine = Not(self.combine) if do_invert else self.combine
        return SympyToSqlHelper.to_sql_where(combine)
