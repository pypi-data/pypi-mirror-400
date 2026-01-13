import json
import typing

class Request:
    def __init__(self, scope: dict, receive: typing.Callable):
        self.scope = scope
        self.receive = receive
        self._body = b""
        self._json = None

    @property
    def method(self) -> str:
        return self.scope['method']

    @property
    def path(self) -> str:
        return self.scope['path']

    @property
    def query_params(self) -> dict:
        query_string = self.scope.get('query_string', b'').decode()
        return dict(qc.split('=') for qc in query_string.split('&') if '=' in qc)

    async def body(self) -> bytes:
        if not self._body:
            body = b""
            while True:
                event = await self.receive()
                if event["type"] == "http.request":
                    body += event.get("body", b"")
                    if not event.get("more_body", False):
                        break
            self._body = body
        return self._body

    async def json(self) -> typing.Any:
        if self._json is None:
            body = await self.body()
            self._json = json.loads(body)
        return self._json

class Response:
    def __init__(self, content: typing.Any = None, status_code: int = 200, headers: dict = None, media_type: str = None):
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}
        self.media_type = media_type

    async def __call__(self, scope: dict, receive: typing.Callable, send: typing.Callable):
        body = self.render(self.content)
        headers = [
            (b"content-length", str(len(body)).encode()),
            (b"content-type", self.media_type.encode() if self.media_type else b"text/plain"),
        ]
        for key, value in self.headers.items():
            headers.append((key.encode(), value.encode()))

        await send({
            "type": "http.response.start",
            "status": self.status_code,
            "headers": headers,
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })

    def render(self, content: typing.Any) -> bytes:
        if isinstance(content, bytes):
            return content
        return str(content).encode("utf-8")

class JSONResponse(Response):
    def __init__(self, content: typing.Any, status_code: int = 200, headers: dict = None):
        super().__init__(content, status_code, headers, media_type="application/json")

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(content).encode("utf-8")

class PlainTextResponse(Response):
    def __init__(self, content: typing.Any, status_code: int = 200, headers: dict = None):
        super().__init__(content, status_code, headers, media_type="text/plain")
