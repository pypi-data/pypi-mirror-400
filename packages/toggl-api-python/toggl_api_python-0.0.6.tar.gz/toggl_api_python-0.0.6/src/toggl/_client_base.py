import logging
from typing import TypeVar, Generic, Union
from urllib.parse import urljoin
from pydantic import BaseModel
import httpx
from httpx import URL, Headers
from ._response import Response
from ._models import Request
from pydantic import BaseModel, Field
from pydantic_core import Url
from ._types import RequestOptions
from ._exceptions import APIError, APITimeoutError, APIStatusError, APIConnectionError

logger = logging.getLogger(__name__)

HttpClientT = TypeVar(
    'HttpClientT', bound=Union[httpx.Client, httpx.AsyncClient])

ResponseT = TypeVar('ResponseT', bound=BaseModel)

class APIClientBase(Generic[HttpClientT]):
    _base_url: URL
    _client: HttpClientT

    def __init__(
            self,
            base_url: str | URL
    ) -> None:
        self._base_url = URL(base_url)

    def _build_headers(self, headers: Headers) -> httpx.Headers:
        # TODO: validate headers
        if headers is None:
            headers = {}
        return httpx.Headers(dict(headers) | self.default_headers)

    def _build_request(self, request: Request) -> httpx.Request:
        headers = self._build_headers(headers=request.headers)
        return self._client.build_request(
            headers=headers,
            method=request.method,
            url=request.url,
            params=request.query_params,
            json=request.body
        )

    @property
    def auth_headers(self) -> dict[str, str]:
        return {}

    @property
    def default_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "charset": "utf8",
            **self.auth_headers
        }


class SyncAPIClient(APIClientBase[httpx.Client]):
    def __init__(
        self,
        base_url: str | URL,
        http_client: httpx.Client = None
    ) -> None:
        super().__init__(
            base_url=base_url
        )
        self._client = http_client or httpx.Client(base_url=base_url)
        self._base_url = base_url
        
    def get(self, path: str, options: RequestOptions = {}, ResponseT: type[ResponseT] = None):
        url = self._build_url(path=path)
        return self._request(Request(url=url, method="get", query_params=options.get("params")), ResponseT=ResponseT)

    def post(self, path: str, options: RequestOptions = {}, ResponseT: type[ResponseT] = None):
        url = self._build_url(path=path)
        return self._request(Request(url=url, method="post", query_params=options.get("params"), body=options.get("body")), ResponseT=ResponseT)

    def put(self, path: str, options: RequestOptions = {}, ResponseT: type[ResponseT] = None):
        url = self._build_url(path=path)
        return self._request(Request(url=url, method="put", body=options.get("body")), ResponseT=ResponseT)

    def patch(self, path: str, options: RequestOptions = {}, ResponseT: type[ResponseT] = None):
        url = self._build_url(path=path)
        return self._request(Request(url=url, method="patch", body=options.get("body")), ResponseT=ResponseT)
    
    def delete(self, path: str, options: RequestOptions = {}, ResponseT: type[ResponseT] = None):
        url = self._build_url(path=path)
        return self._request(Request(url=url, method="delete", query_params=options.get("params"), body=options.get("body")), ResponseT=ResponseT)

    def _request(self, request: Request, ResponseT: type[ResponseT]) -> Response[ResponseT]:
        http_request = self._build_request(request=request)
        try:
            raw_response = self._client.send(request=http_request)
        except httpx.TimeoutException as err:
            raise APITimeoutError(request=http_request) from err
        except httpx.HTTPStatusError as err:
            raise APIStatusError(request=http_request) from err
        except httpx.ConnectError as err:
            raise APIConnectionError(request=http_request) from err
        except Exception as err:
            raise err
        if (raw_response.status_code == 200):
                response = Response(raw_response=raw_response, response_model=ResponseT)
                return response.content
        else:
            raise APIError(message=f'encountered  an unexpected error.\nstatus code:{raw_response.status_code}\nmessage: {raw_response.text}',
                            request=http_request, body=raw_response.content)

    def _build_url(self, path: str):
        return urljoin(self._base_url, path).rstrip('/')


class AsyncAPIClient(APIClientBase[httpx.AsyncClient]):
    def __init__(
        self,
        base_url: str | URL,
        http_client: httpx.AsyncClient = None
    ) -> None:
        super().__init__(
            base_url=base_url
        )
        self._client = http_client or httpx.AsyncClient(base_url=base_url)
        self._base_url = base_url
        
    async def get(self, path: str, options: RequestOptions = {}, ResponseT: type[ResponseT] = None):
        url = self._build_url(path=path)
        return await self._request(Request(url=url, method="get", query_params=options.get("params")), ResponseT=ResponseT)

    async def post(self, path: str, options: RequestOptions = {}, ResponseT: type[ResponseT] = None):
        url = self._build_url(path=path)
        return await self._request(Request(url=url, method="post", query_params=options.get("params"), body=options.get("body")), ResponseT=ResponseT)

    async def put(self, path: str, options: RequestOptions = {}, ResponseT: type[ResponseT] = None):
        url = self._build_url(path=path)
        return await self._request(Request(url=url, method="put", body=options.get("body")), ResponseT=ResponseT)

    async def patch(self, path: str, options: RequestOptions = {}, ResponseT: type[ResponseT] = None):
        url = self._build_url(path=path)
        return await self._request(Request(url=url, method="patch", body=options.get("body")), ResponseT=ResponseT)
    
    async def delete(self, path: str, options: RequestOptions = {}, ResponseT: type[ResponseT] = None):
        url = self._build_url(path=path)
        return await self._request(Request(url=url, method="delete", query_params=options.get("params"), body=options.get("body")), ResponseT=ResponseT)
    
    async def _request(self, request: Request, ResponseT: type[ResponseT]) -> Response[ResponseT]:
        http_request = self._build_request(request=request)
        try:
            logger.debug(f"Sending request: {http_request}")
            raw_response = await self._client.send(request=http_request)
        except httpx.TimeoutException as err:
            raise APITimeoutError(request=http_request) from err
        except httpx.HTTPStatusError as err:
            raise APIStatusError(request=http_request) from err
        except httpx.ConnectError as err:
            raise APIConnectionError(request=http_request) from err
        except Exception as err:
            raise err

        if raw_response.status_code == 200:
            response = Response(raw_response=raw_response, response_model=ResponseT)
            return response.content
        raise APIError(
            message=f'encountered  an unexpected error.\nstatus code:{raw_response.status_code}\nmessage: {raw_response.text}',
            request=http_request,
            body=raw_response.content,
        )

    def _build_url(self, path: str):
        return urljoin(self._base_url, path).rstrip('/')
