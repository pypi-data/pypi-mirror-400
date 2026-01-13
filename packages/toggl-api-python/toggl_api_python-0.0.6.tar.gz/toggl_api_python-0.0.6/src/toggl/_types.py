from httpx import Timeout
from typing import TypedDict, Mapping

Headers = Mapping[str, str]
Query = Mapping[str, object]
Body = object


class RequestOptions(TypedDict, total=False):
    headers: Headers | None = None
    max_retries: int | None = None
    timeout: float | Timeout | None
    params: Query | None = None
    body: Body | None = None
