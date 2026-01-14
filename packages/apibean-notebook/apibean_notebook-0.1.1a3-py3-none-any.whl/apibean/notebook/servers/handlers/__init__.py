from typing import Literal

from fastapi import APIRouter

HANDLER_TYPE = Literal['ac', 'rr', 'tc']

from .AsyncClient import create_handler_from_router as create_handler_from_router_ac
from .RawResponder import create_handler_from_router as create_handler_from_router_rr
from .TestClient import create_handler_from_router as create_handler_from_router_tc

def create_handler_from_router(router: APIRouter, default_router: APIRouter|None = None,
    handler_type: str | None = 'ac',
):
    if handler_type == 'rr':
        return create_handler_from_router_rr(router, default_router=default_router)

    if handler_type == 'tc':
        return create_handler_from_router_tc(router, default_router=default_router)

    return create_handler_from_router_ac(router, default_router=default_router)
