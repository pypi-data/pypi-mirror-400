from __future__ import annotations
from typing import Generic, Iterable, Iterator, Optional, TypeVar, TYPE_CHECKING, Self
from .operators import Expr, And
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class FindMany(Generic[T]):
    def __init__(self, model: type[T], expr: Optional[Expr], data: Iterable[T]):
        self.model = model
        self.expr = expr
        self.data = data

    def where(self, expr: Expr) -> Self:
        self.expr = expr if self.expr is None else And([self.expr, expr])
        return self

    def _iter(self) -> Iterator[T]:
        if self.expr is None:
            yield from self.data
            return
        pred = self.expr.to_predicate()
        for x in self.data:
            if pred(x):
                yield x

    def to_list(self) -> list[T]:
        return list(self._iter())
    