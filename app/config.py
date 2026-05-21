"""Configuration settings for Extern Trends API."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

# Asset subdirectories
INSTAGRAM_ASSETS = ASSETS_DIR / "instagram"
PINTEREST_ASSETS = ASSETS_DIR / "pinterest"
BLOGS_ASSETS = ASSETS_DIR / "blogs"

# Data files
INSTAGRAM_DATA = DATA_DIR / "instagram.json"
PINTEREST_DATA = DATA_DIR / "pinterest.json"
BLOGS_DATA = DATA_DIR / "blogs.json"

# Product data files (pre-scraped)
AMAZON_PRODUCTS = DATA_DIR / "amazon_products.json"
WALMART_PRODUCTS = DATA_DIR / "walmart_products.json"
WAYFAIR_PRODUCTS = DATA_DIR / "wayfair_products.json"

# Dashboard template (P5)
DASHBOARD_TEMPLATE = DATA_DIR / "dashboard_template.html"

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Valid categories
VALID_CATEGORIES = [
    "area_rug",
    "outdoor_rug",
    "hallway_runner",
    "shag_rug"
]

# Category display names
CATEGORY_NAMES = {
    "area_rug": "Area Rug",
    "outdoor_rug": "Outdoor Rug",
    "hallway_runner": "Hallway Runner",
    "shag_rug": "Shag Rug"
}
