import typing
from .http import Request, Response, PlainTextResponse, JSONResponse

class App:
    def __init__(self):
        self.routes: list[tuple[str, str, typing.Callable]] = []

        self.middleware_stack = []
        self.app = self.build_app()

    def build_app(self):
        async def app(scope, receive, send):
            protocol = scope['type']
            if protocol == "http":
                await self.handle_http(scope, receive, send)
            elif protocol == "websocket":
                pass
            elif protocol == "lifespan":
                pass
        
        # Wrap the core app with middlewares in reverse order
        for middleware_cls, options in reversed(self.middleware_stack):
            app = middleware_cls(app, **options)
        return app

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)

    def add_middleware(self, middleware_cls, **options):
        self.middleware_stack.append((middleware_cls, options))
        self.app = self.build_app()


    async def handle_http(self, scope: dict, receive: typing.Callable, send: typing.Callable):
        request = Request(scope, receive)
        try:
            handler = self.find_handler(request)
            if handler:
                response = await handler(request)
                if not isinstance(response, Response):
                     # Auto-wrap if not already a Response (optional helper, mostly for strings)
                     if isinstance(response, (dict, list)):
                         response = JSONResponse(response)
                     else:
                         response = PlainTextResponse(str(response))
                await response(scope, receive, send)
            else:
                response = PlainTextResponse("Not Found", status_code=404)
                await response(scope, receive, send)
        except Exception as e:
            print(f"Error handling request: {e}") # Simple logging
            response = PlainTextResponse("Internal Server Error", status_code=500)
            await response(scope, receive, send)

    def find_handler(self, request: Request) -> typing.Optional[typing.Callable]:
        for path, method, handler in self.routes:
            if path == request.path and method == request.method:
                return handler
        return None

    def add_route(self, path: str, method: str, handler: typing.Callable):
        self.routes.append((path, method, handler))

    def get(self, path: str):
        def decorator(func: typing.Callable):
            self.add_route(path, "GET", func)
            return func
        return decorator

    def post(self, path: str):
        def decorator(func: typing.Callable):
            self.add_route(path, "POST", func)
            return func
        return decorator

    def put(self, path: str):
        def decorator(func: typing.Callable):
            self.add_route(path, "PUT", func)
            return func
        return decorator

    def delete(self, path: str):
        def decorator(func: typing.Callable):
            self.add_route(path, "DELETE", func)
            return func
        return decorator

app = App()
