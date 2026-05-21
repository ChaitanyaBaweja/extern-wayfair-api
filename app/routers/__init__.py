# Routers package
from .instagram import router as instagram_router
from .pinterest import router as pinterest_router
from .blogs import router as blogs_router
from .products import router as products_router
from .template import router as template_router

__all__ = [
    "instagram_router",
    "pinterest_router",
    "blogs_router",
    "products_router",
    "template_router",
]
