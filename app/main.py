"""
Extern Trends API - FastAPI Application

Provides curated rug trend data for Wayfair's n8n trend analysis workflow.
Serves Instagram posts, Pinterest pins, and blog content with images encoded as base64.
"""
import json
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .config import (
    HOST, PORT, DEBUG,
    INSTAGRAM_DATA, PINTEREST_DATA, BLOGS_DATA,
    AMAZON_PRODUCTS, WALMART_PRODUCTS, WAYFAIR_PRODUCTS,
    VALID_CATEGORIES, CATEGORY_NAMES
)
from .models import (
    HealthResponse,
    CategoriesResponse,
    CategoryInfo,
    CategoryCounts
)
from .routers import (
    instagram_router, pinterest_router, blogs_router,
    products_router, template_router,
)


# ============================================
# FastAPI Application
# ============================================

app = FastAPI(
    title="Extern Trends API",
    description="""
API server providing curated rug trend data for Wayfair's market analysis workflow.

## Features

- **Instagram Trends** - Social media posts with images and engagement data
- **Pinterest Trends** - Pin data with images and save counts
- **Blog Content** - Editorial articles with extracted PDF text

## Categories

All content is tagged with one of four rug categories:
- `area_rug` - Movable floor covering for room sections
- `outdoor_rug` - Weather-resistant for patios and decks
- `hallway_runner` - Long, narrow rugs for pathways
- `shag_rug` - High-pile, plush texture rugs
    """,
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)


# ============================================
# CORS Middleware
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for n8n integration
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Include Routers
# ============================================

app.include_router(instagram_router)
app.include_router(pinterest_router)
app.include_router(blogs_router)
app.include_router(products_router)
app.include_router(template_router)


# ============================================
# Helper Functions
# ============================================

def count_items_by_category(data_file, category: str) -> int:
    """Count items in a JSON data file for a specific category."""
    if not data_file.exists():
        return 0

    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return len([item for item in data if item.get("category") == category])
    except Exception:
        return 0


def count_total_items(data_file) -> int:
    """Count total items in a JSON data file."""
    if not data_file.exists():
        return 0

    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return len(data)
    except Exception:
        return 0


def count_products_by_category(data_file, category: str) -> int:
    """Count products in a {retailer}_products.json file for a specific category.

    Supports both shapes:
      - {"retailer": ..., "products": [...]}  (preferred)
      - [...]  (bare list)
    """
    if not data_file.exists():
        return 0
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        products = data if isinstance(data, list) else data.get("products", [])
        return len([p for p in products if p.get("category") == category])
    except Exception:
        return 0


def count_total_products(data_file) -> int:
    """Count total products in a {retailer}_products.json file (across all categories)."""
    if not data_file.exists():
        return 0
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        products = data if isinstance(data, list) else data.get("products", [])
        return len(products)
    except Exception:
        return 0


# ============================================
# Root & Health Endpoints
# ============================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Extern Trends API",
        "version": __version__,
        "docs": "/docs",
        "health": "/api/health"
    }


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns server status and count of loaded assets per source.
    """
    return HealthResponse(
        status="healthy",
        version=__version__,
        assets_loaded={
            "instagram": count_total_items(INSTAGRAM_DATA),
            "pinterest": count_total_items(PINTEREST_DATA),
            "blogs": count_total_items(BLOGS_DATA),
            "amazon_products": count_total_products(AMAZON_PRODUCTS),
            "walmart_products": count_total_products(WALMART_PRODUCTS),
            "wayfair_products": count_total_products(WAYFAIR_PRODUCTS),
        }
    )


# ============================================
# Categories Endpoint
# ============================================

@app.get("/api/categories", response_model=CategoriesResponse, tags=["Categories"])
async def get_categories():
    """
    Get list of available rug categories with content counts per source.

    Returns all four rug categories with the number of items available
    for each source (Instagram, Pinterest, Blogs).
    """
    categories: List[CategoryInfo] = []

    for cat_id in VALID_CATEGORIES:
        categories.append(CategoryInfo(
            id=cat_id,
            name=CATEGORY_NAMES.get(cat_id, cat_id),
            counts=CategoryCounts(
                instagram=count_items_by_category(INSTAGRAM_DATA, cat_id),
                pinterest=count_items_by_category(PINTEREST_DATA, cat_id),
                blogs=count_items_by_category(BLOGS_DATA, cat_id),
                amazon=count_products_by_category(AMAZON_PRODUCTS, cat_id),
                walmart=count_products_by_category(WALMART_PRODUCTS, cat_id),
                wayfair=count_products_by_category(WAYFAIR_PRODUCTS, cat_id),
            )
        ))

    return CategoriesResponse(categories=categories)


# ============================================
# Run with Uvicorn (for direct execution)
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG
    )
