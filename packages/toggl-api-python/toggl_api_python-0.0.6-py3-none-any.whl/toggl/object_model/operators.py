from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, TYPE_CHECKING
from pydantic import BaseModel

if TYPE_CHECKING:
    from ._object_model_base import ExpressionField



def _get_by_path(obj: Any, path: str) -> Any:
    cur = obj
    for part in path.split("."):
        if cur is None:
            return None

        if isinstance(cur, BaseModel):
            cur = getattr(cur, part)
            continue

        if isinstance(cur, dict):
            cur = cur.get(part)
            continue

        cur = getattr(cur, part)
    return cur


class Expr:
    def evaluate(self, obj: BaseModel) -> bool:
        raise NotImplementedError

    def __and__(self, other: Expr) -> And:
        return And([self, other])

    def __or__(self, other: Expr) -> Or:
        return Or([self, other])

    def to_predicate(self) -> Callable[[BaseModel], bool]:
        return lambda x: self.evaluate(x)

@dataclass(frozen=True)
class Eq(Expr):
    field: ExpressionField
    value: Any
    def evaluate(self, obj: BaseModel) -> bool:
        return _get_by_path(obj, str(self.field)) == self.value


@dataclass(frozen=True)
class Ne(Expr):
    field: ExpressionField
    value: Any
    def evaluate(self, obj: BaseModel) -> bool:
        return _get_by_path(obj, str(self.field)) != self.value


@dataclass(frozen=True)
class Lt(Expr):
    field: ExpressionField
    value: Any
    def evaluate(self, obj: BaseModel) -> bool:
        target_value = _get_by_path(obj, str(self.field))
        return target_value is not None and target_value < self.value


@dataclass(frozen=True)
class Lte(Expr):
    field: ExpressionField
    value: Any
    def evaluate(self, obj: BaseModel) -> bool:
        target_value = _get_by_path(obj, str(self.field))
        return target_value is not None and target_value <= self.value


@dataclass(frozen=True)
class Gt(Expr):
    field: ExpressionField
    value: Any
    def evaluate(self, obj: BaseModel) -> bool:
        target_value = _get_by_path(obj, str(self.field))
        return target_value is not None and target_value > self.value


@dataclass(frozen=True)
class Gte(Expr):
    field: ExpressionField
    value: Any
    def evaluate(self, obj: BaseModel) -> bool:
        target_value = _get_by_path(obj, str(self.field))
        return target_value is not None and target_value >= self.value


@dataclass(frozen=True)
class And(Expr):
    parts: list[Expr]
    def evaluate(self, obj: BaseModel) -> bool:
        return all(p.evaluate(obj) for p in self.parts)


@dataclass(frozen=True)
class Or(Expr):
    parts: list[Expr]
    def evaluate(self, obj: BaseModel) -> bool:
        return any(p.evaluate(obj) for p in self.parts)
    
   