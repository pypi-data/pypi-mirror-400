"""Generate llms.txt markdown from FastAPI OpenAPI schema for AI agents."""

from .generator import generate_llms_txt
from .router import create_llms_txt_router

__all__ = ["create_llms_txt_router", "generate_llms_txt"]
__version__ = "0.5.4"
