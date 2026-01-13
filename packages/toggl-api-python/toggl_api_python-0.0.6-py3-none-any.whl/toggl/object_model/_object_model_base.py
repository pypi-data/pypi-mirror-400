from __future__ import annotations
from datetime import datetime
from typing import Any, TYPE_CHECKING, Self, Callable, Optional, ClassVar
from pydantic import BaseModel, Field, model_validator
from .find import FindMany
from .operators import Eq, Gt, Gte, Lt, Lte
from toggl import TogglAPI
from toggl._schemas import ResourceBase


if TYPE_CHECKING:
    from .operators import Expr
    from toggl import TogglAPI
    from toggl._schemas import ApiDataModel




class ExpressionField(str):
    def __getattr__(self, child: str) -> Self:
        return ExpressionField(f"{self}.{child}")
    
    def __eq__(self, other: Any) -> Eq:
        return Eq(self, other)
    
    def __gt__(self, other: Any) -> Gt:
        return Gt(self, other)
    
    def __ge__(self, other: Any) -> Gte:
        return Gte(self, other)
    
    def __lt__(self, other: Any) -> Lt:
        return Lt(self, other)
    
    def __le__(self, other: Any) -> Lte:
        return Lte(self, other)
 
class QueryableProperty(property):
    def __init__(self, fget: Callable[..., Any], fset=None, fdel=None, doc=None, *, name: Optional[str] = None):
        super().__init__(fget, fset, fdel, doc)
        self._query_name = name

    def __set_name__(self, owner, name: str) -> None:
        if self._query_name is None:
            self._query_name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return ExpressionField(self._query_name or self.fget.__name__)
        return super().__get__(obj, objtype)
    
    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__, name=self._query_name)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__, name=self._query_name)

def queryable_property(func=None, *, name: Optional[str] = None):
    if func is None:
        return lambda f: QueryableProperty(f, name=name)
    return QueryableProperty(func, name=name)

class ObjectModelMeta(type(BaseModel)):
    def __getattr__(cls, item: str) -> Any:
        try:
            complete = type.__getattribute__(cls, "__pydantic_complete__")
        except AttributeError:
            complete = False

        if not complete:
            raise AttributeError(item)

        model_fields = type.__getattribute__(cls, "model_fields")
        if item in model_fields:
            return ExpressionField(item)

        return super().__getattr__(item)

class ObjectModel(BaseModel, metaclass=ObjectModelMeta):
    __client__: ClassVar[TogglAPI] = TogglAPI()
    
    id: int | None = Field(default=None)
    at: datetime | None = Field(description="When was last modified", default=None)
    
    def _self_update(self, resource: ResourceBase):
        normalized = type(self).from_resource(resource)
        for name in self.model_fields:
            setattr(self, name, getattr(normalized, name))
        return self
    
    @classmethod
    def _get_api(cls) -> ResourceBase:
        raise NotImplementedError
    
    def _get_by_id_api(self) -> ResourceBase:
        raise NotImplementedError
    
    def _post_api(self) -> ResourceBase:
        raise NotImplementedError
    
    def _put_api(self) -> ResourceBase:
        raise NotImplementedError
    
    def _to_request(self) -> ApiDataModel:
        raise NotImplementedError
    
    @model_validator(mode="before")
    @classmethod
    def _preprocess(cls: type[Self], data: Any) -> Any:
        data = cls._accept_resource(data)
        return data
    
    @classmethod
    def _accept_resource(cls: type[Self], data: Any):
        if isinstance(data, ResourceBase):
            data = data.model_dump()
        return data
    
    @classmethod
    def find(cls: type[Self], expr: Expr | None = None) -> FindMany[Self]:
        resources =  cls._get_api()
        return FindMany(cls, expr, data=[cls.from_resource(resource) for resource in resources])
    
    def save(self):
        if self.id is None:
            resource = self._post_api()
        else:
            resource = self._put_api()
        self._self_update(resource)
    
    def fetch(self):
        resource = self._get_by_id_api()
        self._self_update(resource)


    