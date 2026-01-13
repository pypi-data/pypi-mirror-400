"""FastAPI router for serving llms.txt."""

from fastapi import APIRouter, FastAPI
from fastapi.responses import PlainTextResponse

from .generator import generate_llms_txt


def create_llms_txt_router(app: FastAPI, path: str = "/llms.txt") -> APIRouter:
    """Create a router that serves the llms.txt endpoint.

    Args:
        app: The FastAPI application instance
        path: The path to mount the endpoint at (default: /llms.txt)

    Returns:
        An APIRouter that can be included in the app

    Example:
        >>> from fastapi import FastAPI
        >>> from fast_llms_txt import create_llms_txt_router
        >>>
        >>> app = FastAPI(title="My API")
        >>> app.include_router(create_llms_txt_router(app), prefix="/docs")
    """
    router = APIRouter()

    @router.get(
        path,
        response_class=PlainTextResponse,
        include_in_schema=False,
        summary="Get LLM-friendly API documentation",
    )
    def get_llms_txt() -> str:
        """Return the API documentation in llms.txt markdown format."""
        openapi_schema = app.openapi()
        return generate_llms_txt(openapi_schema)

    return router
