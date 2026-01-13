from collections.abc import Mapping, MutableMapping
from typing import Any, Generator, List, NamedTuple
from urllib.parse import SplitResult, urlsplit, parse_qsl


class Headers(Mapping[str, str]):
    def __init__(self, headers: Mapping[str, str] | None = None , raw : list[tuple[bytes, bytes]] | None = None, scope : MutableMapping | None = None):
        if headers is not None:
            assert raw is None, "Cannot set both headers and raw"
            assert scope is None, "Cannot set both headers and scope"
            self._list = [(key.lower().encode("latin-1"), value.encode("latin-1")) for key, value in headers.items()]
        elif raw is not None:
            assert scope is None, "Cannot set both scope and raw"
            self._list = raw
        elif scope is not None:
            self._list = list(scope["headers"])
    
    @property
    def raw(self) -> list[tuple[bytes, bytes]]:
        return self._list
    
    def keys(self) -> list[str]:
        return [key.decode("latin-1") for key, _ in self._list]
    
    def values(self):
        return [value.decode("latin-1") for _, value in self._list.values()]
    
    def getlist(self, header_key: str) -> list[str]:
        match_key = header_key.lower().encode("latin-1")
        return [key.decode("latin-1") for key, _ in self._list if key == match_key]

    def __getitem__(self, key: str) -> str:
        get_header_key = key.lower().encode("latin-1")
        for header_key, header_value in self._list:
            if header_key == get_header_key:
                return header_value.decode("latin-1")
        
        raise KeyError(key)
    
    def __contains__(self, key: Any) -> bool:
        get_header_key = key.lower().encode("latin-1")
        for header_key, header_value in self._list:
            if header_key == get_header_key:
                return True
        
        return False
    
    def __iter__(self):
        return iter(self.keys())
    
    def __eq__(self, other : Any) -> bool:
        if not isinstance(other, Headers):
            return False
        
        return sorted(self._list) == sorted(other._list)


class URL:
    def __init__(self, url: str = "", scope: Any = None):
        assert url == "", "Cannot set both 'url' and 'scope'"
        scheme = scope.get("scheme", "http")
        server = scope.get("server", None)
        path = scope.get("path", "")
        query_string = scope.get("query_string", b"")
    
        host_header = None
        for key, value in scope["headers"]:
            if key == b"host":
                host_header = value.decode("latin-1")
                break
        
        if host_header is not None:
            url = f"{scheme}://{host_header}{path}"
        elif server is None:
            url = path
        else:
            host, port = server
            url = f"{scheme}://{host}:{port}{path}"

        if query_string:
            url += "?" + query_string.decode()
        
        self._url = url

    @property
    def components(self) -> SplitResult:
        if not hasattr(self, "components"):
            self._components = urlsplit(self._url)
        return self._components

    @property
    def scheme(self) -> str:
        return self._components.scheme
    
    @property
    def path(self) -> str:
        return self._components.path
    
    @property
    def query(self) -> str:
        return self._components.query
    
    @property
    def port(self) -> int | None:
        return self._components.port
    
    def __eq__(self, other: Any) -> bool:
        return str(self) == str(other)
    
    def __str__(self) -> str:
        return self._url
    
class QueryParams:
    def __init__(self, query_string: bytes):
        if isinstance(query_string, bytes):
            query_string = query_string.decode()
        parsed_query_params = parse_qsl(query_string)

        self._list = [[str(k), str(v)] for k, v in parsed_query_params]
        self.__dict = {str(k) : str(v) for k, v in parsed_query_params}

    def __getitem__(self, key: str) -> str:
        for query_key, query_value in self._list:
            if key == query_key:
                return query_value
        raise KeyError(key)
    
    def getlist(self, key: str) -> List[str]:
        return [v for k, v in self._list if k == key]


    def __len__(self) -> int:
        return len(self._list)

    def __iter__(self) -> Generator[str]:
        return (k for k, v in self._list)
    
    def items(self) -> List[List[str]]:
        return self._list
    
    def __repr__(self):
        return f"Query Params : {self.items()}"

class Address(NamedTuple):
    host: str
    port: int