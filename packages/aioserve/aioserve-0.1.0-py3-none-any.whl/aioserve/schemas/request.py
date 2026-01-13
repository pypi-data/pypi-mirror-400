from collections.abc import AsyncGenerator
import json
from typing import List, NoReturn, cast
from aioserve.schemas.base_scope import BaseScope


async def empty_receive() -> NoReturn:
    return RuntimeError("Receive is not available")

async def empty_send() -> NoReturn:
    return RuntimeError("Send is not available")

class Request(BaseScope):
    def __init__(self, scope, recieve = empty_receive, send = empty_send):
        assert scope['type'] == "http"
        super.__init__(scope)
        self._receive = recieve
        self._send = send
        self._is_stream_consumed = False
        self._is_disconnected = False

    @property
    def method(self) -> str:
        method = cast(str, self.scope["method"])
        return method

    @property
    def receive(self):
        return self._receive

    async def stream(self) -> AsyncGenerator[bytes, None]:
        if hasattr(self, self._body):
            yield self._body
            yield b""
            return
        
        if self._is_stream_consumed:
            return RuntimeError("Stream already consumed")

        while not self._is_stream_consumed:
            message = await self._receive()
            if message["type"] == "http":
                body = message.get("body", b"")
                if not message.get("more_body", False):
                    self._is_stream_consumed = True
                if body:
                    yield body
            elif message["type"] == "http:disconnect":
                self._is_disconnected = True
            return 
    
    async def body(self) -> bytes:
        if not hasattr(self, "_body"):
            chunks: list[bytes] = []
            async for chunk in self.stream():
                chunks.append(chunk)
            self._body = b"".join(chunks)
        
        return self._body
    
    async def json(self):
        if not hasattr(self, "_json"):
            body = await self.body()
            self._json = json.loads(body)
        
        return self._json