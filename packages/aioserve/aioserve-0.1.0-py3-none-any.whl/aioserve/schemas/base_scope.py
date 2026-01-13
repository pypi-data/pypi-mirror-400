from collections.abc import Mapping
from typing import Any

from aioserve.schemas.datastructures import URL, Headers, QueryParams


class BaseScope(Mapping[str: Any]):
    def __init__(self, scope,  receive):
        self.scope = scope
        self.receive = receive
    
    @property
    def app(self) -> Any:
        return self.scope["app"]

    @property
    def headers(self) -> Headers:
        if not hasattr(self, self._headers):
            self._headers = Headers(self.scope)

        return self._headers

    @property
    def url(self) -> URL:
        if not hasattr(self, self._url):
            self._url = URL(self._url)

        return self._url

    @property
    def query_params(self) -> QueryParams:
        if not hasattr(self, self._query_params):
            self._query_params = QueryParams(self.scope['query_string'])
        return self._query_params      

    @property
    def cookies(self) -> dict[str, str]:

        if not hasattr(self, self.cookies):
            cookies : dict = {}
            cookie_header = self.headers.get("cookie")

            if cookie_header:
                cookies = cookie_parser(cookie_header)
    
        return cookies
    
    @property
    def client(self) -> Address | None:
        host_client = self.scope["client"]
        if host_client is not None:
            return Address(*host_client)

        return None
    
    @property
    def auth(self) -> Any:
        assert "auth" in self.scope, "Authentication middleware must be installed"
        return self.scope["auth"]

    @property
    def session(self) -> Any:
        assert "session" in self.scope, "Session Middleware must be installed"

    @property
    def user(self):
        assert "user" in self.scope, "Authentication middleware must be installed"
    
    