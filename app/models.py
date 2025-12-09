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


class CategoryInfo(BaseModel):
    """Information about a single category."""
    id: str = Field(..., description="Category identifier (snake_case)")
    name: str = Field(..., description="Display name for the category")
    counts: CategoryCounts = Field(..., description="Content counts per source")


class CategoriesResponse(BaseModel):
    """Response for categories endpoint."""
    categories: List[CategoryInfo] = Field(default_factory=list, description="List of available categories")


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
