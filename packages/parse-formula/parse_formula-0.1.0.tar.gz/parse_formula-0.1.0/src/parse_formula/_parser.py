from __future__ import annotations

import sys
import unicodedata
from collections import defaultdict
from collections.abc import Callable, Sequence
from functools import lru_cache
from typing import Generic, TypeVar

import lark

if sys.version_info < (3, 9):  # no cover
    import importlib_resources as resources
else:
    from importlib import resources

T = TypeVar("T")


@lru_cache(maxsize=1)
def get_parser() -> lark.Lark:
    grammar = (
        resources.files("parse_formula").joinpath("grammar.lark").read_text("utf-8")
    )
    return lark.Lark(grammar, parser="lalr")


class FormulaSyntaxError(ValueError):
    def __init__(self, message: str, context: str) -> None:
        msg = f"{message}\n\n{context}"
        super().__init__(msg)


class FormulaValueError(ValueError): ...


class Transformer(lark.Transformer, Generic[T]):
    def __init__(
        self,
        visit_tokens: bool = True,
        *,
        parse_number: Callable[[str], T],
    ) -> None:
        super().__init__(visit_tokens)
        self.parse_number = parse_number
        self._zero = self.parse_number("0")
        self._one = self.parse_number("1")

    def formula(self, items: Sequence[dict[str, T]]) -> dict[str, T]:
        result = defaultdict(lambda: self._zero)
        for item in items:
            for k, v in item.items():
                result[k] += v  # type: ignore
        return result

    @lark.v_args(inline=True)
    def atom(self, symbol: lark.Token, count: T | None) -> dict[str, T]:
        count = self._one if count is None else count
        return {str(symbol.value): count}

    @lark.v_args(inline=True)
    def group(self, formula: dict[str, T], count: T | None) -> dict[str, T]:
        count = self._one if count is None else count
        return {k: v * count for k, v in formula.items()}  # type: ignore

    @lark.v_args(inline=True)
    def count(self, v: lark.Token) -> T:
        return self.parse_number(v.value)


def parse_formula(
    formula: str,
    *,
    parse_number: Callable[[str], T] = int,
) -> dict[str, T]:
    formula = unicodedata.normalize("NFKC", formula)

    try:
        tree = get_parser().parse(formula)
    except lark.UnexpectedInput as e:
        context = e.get_context(formula)
        if isinstance(e, lark.exceptions.UnexpectedCharacters):
            msg = f"Unexpected character '{e.char}' found"
        elif isinstance(e, lark.exceptions.UnexpectedToken):
            if e.token.type == "$END":
                msg = "Unexpected end of formula. Missing closing parenthesis?"
            else:
                msg = f"Unexpected token '{e.token.value}'."
        else:  # no cover
            msg = "Invalid syntax"

        raise FormulaSyntaxError(msg, context) from e

    try:
        r = Transformer(parse_number=parse_number).transform(tree)
    except lark.exceptions.VisitError as e:
        if "int()" in str(e.orig_exc) and parse_number is int:
            hint = "\n\nHint: Try calling `parse_formula(..., parse_number=float)`"
            raise FormulaValueError(str(e.orig_exc) + hint) from None

        raise e  # no cover

    return dict(r)
