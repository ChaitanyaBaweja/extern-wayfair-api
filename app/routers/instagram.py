"""Instagram trends router."""
import json
import base64
import mimetypes
from typing import Optional, List
from pathlib import Path
from fastapi import APIRouter, Query, HTTPException

from ..config import INSTAGRAM_DATA, INSTAGRAM_ASSETS, VALID_CATEGORIES
from ..models import InstagramResponse, InstagramItem, InstagramDataItem

router = APIRouter(prefix="/api/trends", tags=["Instagram"])


def load_instagram_data() -> List[InstagramDataItem]:
    """Load Instagram metadata from JSON file."""
    if not INSTAGRAM_DATA.exists():
        return []

    try:
        with open(INSTAGRAM_DATA, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [InstagramDataItem(**item) for item in data]
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error loading Instagram data: {e}")
        return []


def get_image_base64(filename: str) -> tuple[str, str]:
    """
    Load image file and return base64 encoded string with mime type.

    Returns:
        tuple: (base64_string, mime_type)
    """
    image_path = INSTAGRAM_ASSETS / filename

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {filename}")

    # Determine MIME type
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if mime_type is None:
        mime_type = "image/jpeg"  # Default fallback

    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = f.read()
        base64_string = base64.b64encode(image_data).decode("utf-8")

    return base64_string, mime_type


@router.get("/instagram", response_model=InstagramResponse)
async def get_instagram_trends(
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
) -> InstagramResponse:
    """
    Get Instagram trend data with base64 encoded images.

    - **category**: Optional filter by rug category (area_rug, outdoor_rug, hallway_runner, shag_rug)
    - **limit**: Maximum number of items to return (default: 10, max: 50)
    """
    # Load data from JSON
    all_items = load_instagram_data()

    # Filter by category if specified
    if category:
        all_items = [item for item in all_items if item.category == category]

    # Apply limit
    all_items = all_items[:limit]

    # Build response with base64 images
    response_items: List[InstagramItem] = []

    for item in all_items:
        try:
            base64_image, mime_type = get_image_base64(item.filename)

            response_items.append(InstagramItem(
                id=item.id,
                url=item.url,
                caption=item.caption,
                hashtags=item.hashtags,
                engagement=item.engagement,
                posted_at=item.posted_at,
                image_base64=base64_image,
                image_mime_type=mime_type
            ))
        except FileNotFoundError as e:
            # Log error but continue with other items
            print(f"Warning: {e}")
            continue

    return InstagramResponse(
        source="instagram",
        category=category,
        items=response_items
    )
