from typing import Literal
import httpx


class PyTogglError(Exception):
    pass


class APIError(PyTogglError):
    message: str
    request: httpx.Request
    body: object | None

    def __init__(self, *, request: httpx.Request, message: str | None = None, body: object | None = None) -> None:
        super().__init__(message)
        self.request = request
        self.body = body

class APITimeoutError(APIError):
    def __init__(self, request: httpx.Request):
        super().__init__(message="Request timed out.", request=request)

class APIStatusError(APIError):
    response: httpx.Response
    status_code: int

    def __init__(self, message: str, *, request: httpx.Request, body: object | None = None):
        super().__init__(message, request=request, body=body)

class APIConnectionError(APIError):
    def __init__(self, request: httpx.Request):
        super().__init__(message="Connection error.", request=request)




