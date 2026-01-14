import threading
import asyncio

from typing import Callable, Optional

from fastapi import APIRouter, FastAPI, Request

import uvicorn

from .handlers import HANDLER_TYPE
from .handlers import create_handler_from_router

from .fastapi_util import HTTP_METHODS
from .fastapi_util import default_handler
from .fastapi_util import default_router

from .middlewares.PrettyJSONMiddleware import PrettyJSONMiddleware

from ..utils.net_util import is_port_available

class EmbeddedAPIServerBase:
    def __init__(self, host="0.0.0.0", port=8000, log_level:str="error",
            control_base_path: str = "__notebook__",
            pretty_json_response: bool = True):
        # service settings
        self.host = host
        self.port = port
        self.log_level = log_level
        self.control_base_path = control_base_path
        self.pretty_json_response = pretty_json_response
        # private properties
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._server: Optional[uvicorn.Server] = None
        self._running: bool = False
        self._handler = None

    def _create_app(self) -> FastAPI:
        app = FastAPI()

        if self.pretty_json_response:
            app.add_middleware(PrettyJSONMiddleware)

        @app.get(f"/{self.control_base_path}/status")
        async def status_endpoint():
            return self.status()

        @app.api_route("/{full_path:path}", methods=HTTP_METHODS, include_in_schema=False)
        async def main_handler(request: Request, full_path: str):
            if self._handler:
                return await self._handler(request)
            return await default_handler(request, full_path, handler_name="universal")

        return app

    def _run_server(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        app = self._create_app()
        config = uvicorn.Config(app, host=self.host, port=self.port, log_level=self.log_level,
                loop="asyncio")
        self._server = uvicorn.Server(config)

        self._running = True
        try:
            self._loop.run_until_complete(self._server.serve())
        finally:
            self._loop.close()
        self._running = False

    def _print_info(self, msg):
        print(msg)

    def start(self):
        if self._running:
            self._print_info("⚠️ Server is already running.")
            return

        if not is_port_available(port=self.port, host=self.host):
            self._print_info(f"❌ Address ('{self.host}', {self.port}) already in use")
            return

        self._thread = threading.Thread(target=self._run_server, daemon=True)
        self._thread.start()
        self._print_info(f"✅ Server started at http://{self.host}:{self.port}")

    def stop(self):
        if self._server:
            self._print_info("🛑 Stopping server...")
            self._server.should_exit = True
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=5)
            self._thread = None
            self._server = None
            self._loop = None
        else:
            self._print_info("⚠️ Server not running.")

    def restart(self):
        self.stop()
        self.start()

    def status(self) -> dict:
        return {
            "running": self._running,
            "thread_alive": self._thread.is_alive() if self._thread else False,
            "host": self.host,
            "port": self.port,
            "handler_set": self._handler is not None
        }

    def update_handler(self, func: Optional[Callable[..., dict]]):
        self._handler = func
        self._print_info("✅ Handler updated.")

    def update_router(self, router: Optional[APIRouter], handler_type: HANDLER_TYPE | None = None):
        handler = create_handler_from_router(router,
                default_router=default_router,
                handler_type=handler_type) if router is not None else None
        self.update_handler(handler)
