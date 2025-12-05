# Routers package
from .instagram import router as instagram_router
from .pinterest import router as pinterest_router
from .blogs import router as blogs_router

__all__ = ["instagram_router", "pinterest_router", "blogs_router"]
