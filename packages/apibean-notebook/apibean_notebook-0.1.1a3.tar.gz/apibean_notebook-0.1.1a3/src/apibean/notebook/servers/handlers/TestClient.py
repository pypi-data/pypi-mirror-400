import asyncio

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import Response
from fastapi.testclient import TestClient

def create_handler_from_router(router: APIRouter, default_router: APIRouter|None = None):
    """
    Create an async request handler from a FastAPI APIRouter using TestClient.

    This implementation adapts FastAPI's synchronous TestClient
    into an async-compatible handler that can be used inside an
    interception / proxy / dispatch pipeline.

    The router is mounted into a temporary FastAPI app, and all incoming
    requests are forwarded to that app via TestClient.
    """

    # Create a temporary FastAPI application.
    # This app is not served by a real HTTP server; it is invoked internally.
    app = FastAPI()

    # Mount the primary router containing user-defined endpoints.
    app.include_router(router)

    # Optionally mount a default or fallback router.
    if default_router is not None:
        app.include_router(default_router)

    # Initialize FastAPI TestClient.
    #
    # TestClient provides a synchronous, in-process HTTP client
    # backed by Starlette's test utilities.
    client = TestClient(app)

    async def handler(req: Request) -> Response:
        """
        Async request handler that forwards the incoming Request
        to the TestClient and converts the result back into a
        Starlette Response.
        """

        # Read the full request body as raw bytes.
        # This is necessary because the body can only be read once.
        body = await req.body()

        # Copy incoming request headers into a plain dictionary.
        # TestClient expects standard header mappings.
        headers = dict(req.headers)

        # Extract the request path (without scheme, host, or query string).
        # TestClient works with relative URLs inside the app.
        url = req.url.path

        # TestClient only exposes synchronous request methods
        # (client.get, client.post, ...), so we must execute them
        # in a thread pool to avoid blocking the event loop.
        def do_request():
            # Convert HTTP method to lowercase to match TestClient API.
            method = req.method.lower()

            # Dynamically resolve the client method:
            #   client.get, client.post, client.put, etc.
            fn = getattr(client, method)

            # Prepare optional request body arguments.
            body_args = {}

            # Only include body data for methods that support it.
            # GET / DELETE requests should not include a body.
            if method in ['post', 'put', 'patch']:
                body_args.update(data=body)

            # Execute the request synchronously via TestClient.
            #
            # - url: request path inside the app
            # - headers: forwarded headers
            # - params: forwarded query parameters
            # - data: raw request body (if applicable)
            return fn(url, headers=headers, params=req.query_params, **body_args)

        # Get the currently running event loop.
        loop = asyncio.get_event_loop()

        # Offload the synchronous TestClient call to a background thread.
        # This prevents blocking the async event loop.
        response = await loop.run_in_executor(None, do_request)

        # Convert the TestClient response back into a Starlette Response.
        #
        # This allows the handler to integrate seamlessly with FastAPI,
        # middleware, or proxy pipelines.
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )

    return handler
