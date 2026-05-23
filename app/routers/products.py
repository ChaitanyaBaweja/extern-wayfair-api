"""Products router — serves pre-scraped Amazon/Walmart/Wayfair product data.

Three endpoints share the same request/response shape:
  GET /api/products/amazon
  GET /api/products/walmart
  GET /api/products/wayfair

The server does NOT scrape live. Data is read from app/data/{retailer}_products.json,
which is refreshed offline by scripts/refresh_dataset.py (see scripts/README.md).
"""
import json
import random
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException

from ..config import (
    AMAZON_PRODUCTS, WALMART_PRODUCTS, WAYFAIR_PRODUCTS,
    VALID_CATEGORIES
)
from ..models import (
    ProductItem,
    ProductsResponse,
    ProductDataItem,
    ProductDataset,
)

router = APIRouter(prefix="/api/products", tags=["Products"])


# Map retailer slug -> data file path
RETAILER_FILES = {
    "amazon": AMAZON_PRODUCTS,
    "walmart": WALMART_PRODUCTS,
    "wayfair": WAYFAIR_PRODUCTS,
}


def load_dataset(retailer: str) -> ProductDataset:
    """Load a retailer's product dataset from JSON. Returns an empty dataset if file is missing/empty."""
    path = RETAILER_FILES.get(retailer)
    if path is None or not path.exists():
        return ProductDataset(retailer=retailer)

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        # Tolerate both wrapped shape {"retailer":..., "products":[...]} and bare list [...]
        if isinstance(raw, list):
            return ProductDataset(
                retailer=retailer,
                products=[ProductDataItem(**p) for p in raw],
            )
        return ProductDataset(
            retailer=raw.get("retailer", retailer),
            scraped_at=raw.get("scraped_at"),
            products=[ProductDataItem(**p) for p in raw.get("products", [])],
        )
    except (json.JSONDecodeError, Exception) as e:
        # Log + return empty so the workflow's Has Products? gate handles it cleanly
        print(f"Error loading {retailer} dataset: {e}")
        return ProductDataset(retailer=retailer)


def get_products_for(
    retailer: str,
    category: str,
    limit: int,
    focus: Optional[str],
) -> ProductsResponse:
    """Shared helper: filter a retailer's dataset by category, apply limit, return envelope.

    The `focus` parameter is accepted but ignored in v1 (reserved for future ranking/filtering).
    """
    if category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unknown category '{category}'. "
                f"Supported keys: {', '.join(VALID_CATEGORIES)}."
            ),
        )
    dataset = load_dataset(retailer)
    filtered: List[ProductDataItem] = [
        p for p in dataset.products if p.category == category
    ]
    # Shuffle so students get a varied subset on each call.
    # Mirrors the pattern used by /api/trends/instagram, /pinterest, etc.
    random.shuffle(filtered)
    selected = filtered[:limit]

    products = [
        ProductItem(
            url=p.url,
            name=p.name,
            price=p.price,
            details=p.details,
            pattern=p.pattern,
            image_url=p.image_url,
            rating=p.rating,
            review_count=p.review_count,
        )
        for p in selected
    ]
    return ProductsResponse(
        source=retailer,
        category=category,
        total_products=len(products),
        scraped_at=dataset.scraped_at,
        products=products,
    )


@router.get("/amazon", response_model=ProductsResponse)
async def get_amazon_products(
    category: str = Query(
        ...,
        description="Filter by rug category (required)",
        enum=VALID_CATEGORIES,
    ),
    limit: int = Query(
        10, ge=1, le=50,
        description="Maximum number of products to return",
    ),
    focus: Optional[str] = Query(
        None,
        max_length=200,
        description="Optional keyword hint. Currently accepted but ignored; reserved for future use.",
    ),
) -> ProductsResponse:
    """Pre-scraped Amazon products for a category."""
    return get_products_for("amazon", category, limit, focus)


@router.get("/walmart", response_model=ProductsResponse)
async def get_walmart_products(
    category: str = Query(
        ...,
        description="Filter by rug category (required)",
        enum=VALID_CATEGORIES,
    ),
    limit: int = Query(10, ge=1, le=50),
    focus: Optional[str] = Query(None, max_length=200),
) -> ProductsResponse:
    """Pre-scraped Walmart products for a category."""
    return get_products_for("walmart", category, limit, focus)


@router.get("/wayfair", response_model=ProductsResponse)
async def get_wayfair_products(
    category: str = Query(
        ...,
        description="Filter by rug category (required)",
        enum=VALID_CATEGORIES,
    ),
    limit: int = Query(10, ge=1, le=50),
    focus: Optional[str] = Query(None, max_length=200),
) -> ProductsResponse:
    """Pre-scraped Wayfair products for a category."""
    return get_products_for("wayfair", category, limit, focus)
