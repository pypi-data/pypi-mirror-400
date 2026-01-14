from fastapi import APIRouter, Request

HTTP_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]

default_router = APIRouter()

@default_router.api_route("/{full_path:path}", methods=HTTP_METHODS, include_in_schema=False)
async def default_handler(request: Request, full_path: str, handler_name: str = "default"):
    """
    Default catch-all request handler used as a fallback in the API proxy/router.

    This handler is registered with a wildcard path (``/{full_path:path}``) and
    supports all common HTTP methods. It is intended to act as a *last-resort*
    handler when no specific route or extension matches the incoming request.

    Typical use cases:
    - Development-time API proxying / MITM inspection
    - Debugging and introspecting incoming HTTP requests
    - Serving as a placeholder handler before implementing real endpoints
    - Returning a normalized view of the request for notebooks or tooling

    Behavior:
    - Attempts to parse the request body as JSON; if parsing fails, ``body`` is set to ``None``
    - Collects and returns key request attributes in a structured dictionary:
      - handler name
      - resolved request path
      - HTTP method
      - query parameters
      - headers
      - request body (if JSON)

    Notes:
    - This handler does NOT forward the request upstream.
    - It should typically be placed at the end of the routing chain.
    - ``include_in_schema=False`` ensures it does not appear in OpenAPI docs.

    Parameters
    ----------
    request : fastapi.Request
        The incoming HTTP request object.
    full_path : str
        The full unmatched request path captured by the wildcard route.
    handler_name : str, optional
        Logical name of the handler, useful for debugging or tracing
        (default: "default").

    Returns
    -------
    dict
        A dictionary containing a structured representation of the incoming request.
    """
    try:
        body = await request.json()
    except:
        body = None
    return dict(
        handler_name=handler_name,
        path=full_path,
        method=request.method,
        query=dict(request.query_params),
        headers=dict(request.headers),
        body=body
    )
