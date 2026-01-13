import httpx
from typing import TypeVar, Generic, get_origin, get_args
from pydantic import BaseModel

T = TypeVar('T', BaseModel, list[BaseModel])


class Response(Generic[T]):
    def __init__(
            self,
            raw_response: httpx.Response,
            response_model: type[T] | None
    ):
        self._raw_response = raw_response
        self._status_code = raw_response.status_code
        content = raw_response.json() if raw_response.content else None

        if response_model is None:
            self._content: T = content
            return

        origin = get_origin(response_model)
        args = get_args(response_model)

        if origin is list:
            model = args[0]
            if not (isinstance(model, type) and issubclass(model, BaseModel)):
                raise TypeError("response_model must be list[BaseModel] or BaseModel")
            if content is None:
                self._content: T = []
            elif not isinstance(content, list):
                raise TypeError("Expected list content for list[BaseModel] response")
            else:
                self._content: T = [model.model_validate(item) for item in content]
            return

        if isinstance(response_model, type) and issubclass(response_model, BaseModel):
            self._content: T = response_model.model_validate(content) if content is not None else None
            return

        raise TypeError("response_model must be BaseModel or list[BaseModel]")

    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def content(self) -> T:
        return self._content

    def json(self):
        return self._raw_response.json()
