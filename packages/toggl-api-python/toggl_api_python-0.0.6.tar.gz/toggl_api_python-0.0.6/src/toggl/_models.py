from typing import Mapping, final, Any, Literal, Sequence
from pydantic import BaseModel, Field, ConfigDict

@final
class Request(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    url: str
    method: str
    headers: Mapping[str, str] | None = None
    query_params: Mapping[str, (str | int | float | bool) | Sequence[str | int | float | bool]] = {}
    body: (str | int | float | bool | None) | dict[str, Any] | list[Any] = None






