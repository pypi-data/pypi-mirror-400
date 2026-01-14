import httpx
from fastapi import APIRouter, FastAPI, Request, Response

# HTTP methods that are allowed to carry a request body.
# According to HTTP semantics, GET and HEAD should not include a body.
METHODS_WITH_BODY = {"POST", "PUT", "PATCH", "DELETE"}

def create_handler_from_router(router: APIRouter, default_router: APIRouter|None = None):
    """
    Create an async request handler from a FastAPI APIRouter using httpx.AsyncClient
    with ASGITransport.

    This approach executes the FastAPI application fully in-memory, without
    starting a real HTTP server, while preserving:
      - full ASGI lifecycle
      - async execution
      - streaming compatibility (on the ASGI side)

    It is the cleanest and most production-aligned approach for interception
    and proxying inside an async application.
    """

    # Create a temporary FastAPI application.
    # This app is never exposed on a network port.
    app = FastAPI()

    # Mount the primary router containing user-defined endpoints.
    app.include_router(router)

    # Optionally mount a fallback router (e.g. catch-all or default handler).
    if default_router is not None:
        app.include_router(default_router)

    # Create an AsyncClient that talks directly to the FastAPI app
    # via ASGITransport.
    #
    # - ASGITransport bypasses the network stack entirely.
    # - Requests are executed in-process using the ASGI protocol.
    # - base_url is required by httpx for URL resolution,
    #   but does not correspond to a real network host.
    client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app),
        base_url="http://internal")  # Arbitrary internal base URL (httpx >= 0.23)

    async def handler(request: Request) -> Response:
        """
        Async handler that forwards an incoming FastAPI Request
        to the internal ASGI application using httpx.AsyncClient,
        then converts the httpx response back into a FastAPI Response.
        """

        # Normalize HTTP method to uppercase.
        # httpx accepts uppercase method names.
        method = request.method.upper()

        # Build the request options for httpx.
        #
        # These fields are forwarded from the incoming request
        # to the internal FastAPI app.
        opts = dict(
            method = method,

            # Only the path portion is needed because base_url
            # is already defined on the client.
            url = request.url.path,

            # Forward all incoming HTTP headers.
            # These are converted into a plain dict for httpx.
            headers = dict(request.headers),

            # Forward query parameters as a dict.
            params = dict(request.query_params),
        )

        # Only include a request body for methods that support it.
        #
        # Reading the body consumes the request stream, so it must
        # be done exactly once.
        if method in METHODS_WITH_BODY:
            body = await request.body()

            # httpx accepts raw bytes via the `content` argument.
            opts.update(content=body)

        # Execute the request asynchronously against the internal ASGI app.
        #
        # This call:
        #   - enters the ASGI app
        #   - runs routing, dependencies, middleware
        #   - produces an httpx.Response
        resp = await client.request(**opts)

        # Convert the httpx.Response into a FastAPI / Starlette Response.
        #
        # This makes the handler compatible with:
        #   - FastAPI endpoints
        #   - middleware pipelines
        #   - proxy / intercept engines
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=dict(resp.headers)
        )

    return handler
