"""Blogs trends router with PDF text extraction."""
import json
from typing import Optional, List
from pathlib import Path
from fastapi import APIRouter, Query, HTTPException

try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("Warning: PyPDF2 not installed. PDF extraction will not work.")

from ..config import BLOGS_DATA, BLOGS_ASSETS, VALID_CATEGORIES
from ..models import BlogsResponse, BlogItem, BlogDataItem

router = APIRouter(prefix="/api/trends", tags=["Blogs"])


def load_blogs_data() -> List[BlogDataItem]:
    """Load blog metadata from JSON file."""
    if not BLOGS_DATA.exists():
        return []

    try:
        with open(BLOGS_DATA, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [BlogDataItem(**item) for item in data]
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error loading blogs data: {e}")
        return []


def extract_pdf_text(filename: str) -> str:
    """
    Extract text content from a PDF file.

    Args:
        filename: Name of the PDF file in the blogs assets directory

    Returns:
        Extracted text content from all pages
    """
    if not PDF_SUPPORT:
        return "[PDF extraction not available - PyPDF2 not installed]"

    pdf_path = BLOGS_ASSETS / filename

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {filename}")

    try:
        text_content = []

        with open(pdf_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)

            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text.strip())

        full_text = "\n\n".join(text_content)

        # Clean up the text (remove excessive whitespace)
        lines = full_text.split("\n")
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        return "\n".join(cleaned_lines)

    except Exception as e:
        print(f"Error extracting PDF text from {filename}: {e}")
        return f"[Error extracting PDF content: {str(e)}]"


@router.get("/blogs", response_model=BlogsResponse)
async def get_blog_trends(
    category: Optional[str] = Query(
        None,
        description="Filter by rug category",
        enum=VALID_CATEGORIES
    ),
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="Maximum number of items to return"
    )
) -> BlogsResponse:
    """
    Get blog trend data with extracted PDF content.

    - **category**: Optional filter by rug category (area_rug, outdoor_rug, hallway_runner, shag_rug)
    - **limit**: Maximum number of items to return (default: 10, max: 50)
    """
    # Load data from JSON
    all_items = load_blogs_data()

    # Filter by category if specified
    if category:
        all_items = [item for item in all_items if item.category == category]

    # Apply limit
    all_items = all_items[:limit]

    # Build response with extracted PDF content
    response_items: List[BlogItem] = []

    for item in all_items:
        try:
            pdf_content = extract_pdf_text(item.filename)

            response_items.append(BlogItem(
                id=item.id,
                url=item.url,
                title=item.title,
                excerpt=item.excerpt,
                source_name=item.source_name,
                published_at=item.published_at,
                content=pdf_content
            ))
        except FileNotFoundError as e:
            # Log error but continue with other items
            print(f"Warning: {e}")
            # Include item with error message in content
            response_items.append(BlogItem(
                id=item.id,
                url=item.url,
                title=item.title,
                excerpt=item.excerpt,
                source_name=item.source_name,
                published_at=item.published_at,
                content=f"[PDF file not found: {item.filename}]"
            ))

    return BlogsResponse(
        source="blogs",
        category=category,
        items=response_items
    )
