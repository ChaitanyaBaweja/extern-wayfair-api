"""Pydantic models for Extern Trends API."""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import date


# ============================================
# Instagram Models
# ============================================

class InstagramItem(BaseModel):
    """Single Instagram post with image data."""
    id: str = Field(..., description="Unique identifier for the post")
    url: str = Field(..., description="URL to the Instagram post")
    caption: str = Field(..., description="Post caption text")
    hashtags: List[str] = Field(default_factory=list, description="Hashtags from the post")
    engagement: int = Field(0, description="Engagement count (likes + comments)")
    posted_at: str = Field(..., description="Date posted (YYYY-MM-DD)")
    image_base64: str = Field(..., description="Base64 encoded image data")
    image_mime_type: str = Field("image/jpeg", description="MIME type of the image")


class InstagramResponse(BaseModel):
    """Response for Instagram trends endpoint."""
    source: str = Field("instagram", description="Data source identifier")
    category: Optional[str] = Field(None, description="Category filter applied")
    items: List[InstagramItem] = Field(default_factory=list, description="List of Instagram posts")


# ============================================
# Pinterest Models
# ============================================

class PinterestItem(BaseModel):
    """Single Pinterest pin with image data."""
    id: str = Field(..., description="Unique identifier for the pin")
    url: str = Field(..., description="URL to the Pinterest pin")
    caption: str = Field(..., description="Pin description text")
    hashtags: List[str] = Field(default_factory=list, description="Related hashtags")
    engagement: int = Field(0, description="Save/repin count")
    posted_at: str = Field(..., description="Date pinned (YYYY-MM-DD)")
    image_base64: str = Field(..., description="Base64 encoded image data")
    image_mime_type: str = Field("image/jpeg", description="MIME type of the image")


class PinterestResponse(BaseModel):
    """Response for Pinterest trends endpoint."""
    source: str = Field("pinterest", description="Data source identifier")
    category: Optional[str] = Field(None, description="Category filter applied")
    items: List[PinterestItem] = Field(default_factory=list, description="List of Pinterest pins")


# ============================================
# Blog Models
# ============================================

class BlogItem(BaseModel):
    """Single blog article with extracted content."""
    id: str = Field(..., description="Unique identifier for the blog")
    url: str = Field(..., description="URL to the blog article")
    title: str = Field(..., description="Article title")
    excerpt: str = Field(..., description="Short excerpt/summary")
    source_name: str = Field(..., description="Name of the blog/publication")
    published_at: str = Field(..., description="Date published (YYYY-MM-DD)")
    content: str = Field(..., description="Full extracted text content from PDF")


class BlogsResponse(BaseModel):
    """Response for blogs trends endpoint."""
    source: str = Field("blogs", description="Data source identifier")
    category: Optional[str] = Field(None, description="Category filter applied")
    items: List[BlogItem] = Field(default_factory=list, description="List of blog articles")


# ============================================
# Category Models
# ============================================

class CategoryCounts(BaseModel):
    """Content counts per source for a category."""
    instagram: int = Field(0, description="Number of Instagram posts")
    pinterest: int = Field(0, description="Number of Pinterest pins")
    blogs: int = Field(0, description="Number of blog articles")
    amazon: int = Field(0, description="Number of Amazon products")
    walmart: int = Field(0, description="Number of Walmart products")
    wayfair: int = Field(0, description="Number of Wayfair products")


class CategoryInfo(BaseModel):
    """Information about a single category."""
    id: str = Field(..., description="Category identifier (snake_case)")
    name: str = Field(..., description="Display name for the category")
    counts: CategoryCounts = Field(..., description="Content counts per source")


class CategoriesResponse(BaseModel):
    """Response for categories endpoint."""
    categories: List[CategoryInfo] = Field(default_factory=list, description="List of available categories")


# ============================================
# Product Models
# ============================================

class ProductItem(BaseModel):
    """Single product from a retailer (Amazon, Walmart, Wayfair)."""
    url: str = Field(..., description="Canonical product URL")
    name: str = Field(..., description="Product title")
    price: str = Field("", description='Price formatted as "NN.NN" (no $, no thousand separators). Empty if not found.')
    details: List[str] = Field(default_factory=list, description="Feature bullets")
    pattern: str = Field("", description="Pattern/variant name. Empty if not found.")
    image_url: str = Field("", description="Main product image URL. Empty if not found.")
    rating: str = Field("", description='Format "X.X out of 5 stars". Empty if not found.')
    review_count: str = Field("", description='Numeric string, no parens or thousand separators (e.g., "3902"). Empty if not found.')


class ProductsResponse(BaseModel):
    """Response for product endpoints (Amazon, Walmart, Wayfair)."""
    source: str = Field(..., description="Retailer identifier: amazon, walmart, or wayfair")
    category: str = Field(..., description="Category key that was requested")
    total_products: int = Field(0, description="Count of products returned; equal to len(products)")
    scraped_at: Optional[str] = Field(None, description="ISO 8601 timestamp of when the underlying dataset was refreshed")
    products: List[ProductItem] = Field(default_factory=list, description="Products for the requested category")


class ProductDataItem(BaseModel):
    """Product item as stored in JSON file. Same shape as ProductItem plus category."""
    category: str
    url: str
    name: str
    price: str = ""
    details: List[str] = Field(default_factory=list)
    pattern: str = ""
    image_url: str = ""
    rating: str = ""
    review_count: str = ""


class ProductDataset(BaseModel):
    """Top-level shape of a {retailer}_products.json file."""
    retailer: str
    scraped_at: Optional[str] = None
    products: List[ProductDataItem] = Field(default_factory=list)


# ============================================
# Health Check Model
# ============================================

class HealthResponse(BaseModel):
    """Response for health check endpoint."""
    status: str = Field("healthy", description="Server status")
    version: str = Field(..., description="API version")
    assets_loaded: Dict[str, int] = Field(..., description="Count of loaded assets per source")


# ============================================
# Internal Data Models (for JSON files)
# ============================================

class InstagramDataItem(BaseModel):
    """Instagram item as stored in JSON file (references filename, not base64)."""
    id: str
    filename: str
    category: str
    url: str
    caption: str
    hashtags: List[str]
    engagement: int
    posted_at: str


class PinterestDataItem(BaseModel):
    """Pinterest item as stored in JSON file (references filename, not base64)."""
    id: str
    filename: str
    category: str
    url: str
    caption: str
    hashtags: List[str]
    engagement: int
    posted_at: str


class BlogDataItem(BaseModel):
    """Blog item as stored in JSON file (references PDF filename)."""
    id: str
    filename: str
    category: str
    blog_type: str = "guide"  # "trends", "market", or "guide"
    url: str
    title: str
    excerpt: str
    source_name: str
    published_at: str
