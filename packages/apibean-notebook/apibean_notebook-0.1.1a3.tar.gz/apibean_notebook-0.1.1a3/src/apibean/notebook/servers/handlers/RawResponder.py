from typing import Callable, Awaitable

from fastapi import FastAPI, Request
from fastapi.routing import APIRouter
from starlette.responses import Response
from starlette.types import Receive, Scope, Send


def create_handler_from_router(router: APIRouter, default_router: APIRouter|None = None) \
        -> Callable[[Request], Awaitable[Response]]:
    """
    Build an async request handler from a FastAPI APIRouter.

    Internally, this function mounts the router into a temporary FastAPI app,
    then executes that app manually as an ASGI callable in order to:
      - intercept request/response flow
      - extract the generated response
      - return it as a normal Starlette Response object

    This pattern is useful for proxying, interception, and dynamic dispatch.
    """

    # Create a temporary FastAPI application.
    # This app is NOT served by uvicorn; it is only executed programmatically.
    temp_app = FastAPI()

    # Mount the main router (user-defined API routes).
    temp_app.include_router(router)

    # Optionally mount a fallback router (e.g. default / catch-all handler).
    if default_router is not None:
        temp_app.include_router(default_router)

    async def handler(req: Request) -> Response:
        """
        This handler adapts an ASGI-based FastAPI app into a callable
        that accepts a Request and returns a Response.
        """

        # A simple buffer to capture ASGI "send" messages.
        # In ASGI, responses are emitted via the `send()` callable.
        send_buffer = {}

        async def send(message):
            """
            ASGI send callable.

            FastAPI / Starlette will call this function with messages like:
              - http.response.start
              - http.response.body

            We intercept and store them so we can reconstruct a Response object.
            """
            send_buffer["message"] = message

        # Execute the FastAPI app as a raw ASGI application.
        #
        # temp_app itself is an ASGI callable with signature:
        #   await app(scope, receive, send)
        #
        # Here we reuse the original request's scope and receive channel,
        # but override `send` to capture the response instead of sending it
        # to a real network socket.
        responder = temp_app
        await responder(req.scope, req.receive, send)

        # Extract the last ASGI message that was sent.
        message = send_buffer.get("message")
        if message is None:
            # No ASGI response was produced — this should not normally happen.
            return Response("No response", status_code=500)

        # Handle ASGI response start message.
        #
        # http.response.start contains status code and headers,
        # but the actual body is sent separately via http.response.body.
        if message["type"] == "http.response.start":
            # Attempt to retrieve a previously captured body message.
            # (Note: this implementation only captures a single message;
            # real-world implementations usually collect all body chunks.)
            body_msg = send_buffer.get("body_message")
            body = body_msg["body"] if body_msg else b""
            return Response(content=body, status_code=message["status"])

        # Handle ASGI response body message directly.
        elif message["type"] == "http.response.body":
            return Response(content=message["body"], status_code=200)

        # Fallback for unexpected ASGI message types.
        return Response("Unhandled response", status_code=500)

    return handler
