"""Seed app/data with sample product JSON for all 3 retailers x 4 categories.

Run once during initial setup. Real data should be added later via a refresh
script that hits ScraperAPI or equivalent (see scripts/README.md).
"""
import json
from pathlib import Path
from datetime import datetime, timezone

DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "data"

CATEGORIES = ["area_rug", "outdoor_rug", "hallway_runner", "shag_rug"]

# Synthetic-but-realistic product seed data. Five products per (retailer, category).
# Fields match the FastAPI spec: url, name, price, details[], pattern, image_url, rating, review_count.

# Common detail bullet templates by category — keeps the AI pipeline downstream
# happy by giving it realistic feature descriptions.
DETAIL_TEMPLATES = {
    "area_rug": [
        ["Soft polypropylene pile; stain-resistant for high-traffic areas",
         "Low-pile design fits under furniture and doorways",
         "Non-slip backing keeps the rug in place on hard floors",
         "Vacuum regularly; spot-clean with mild detergent",
         "Available in multiple sizes from 5x7 to 9x12"],
        ["Power-loomed construction for durability",
         "Vintage distressed pattern adds character",
         "Pet-friendly and kid-friendly materials",
         "Easy to clean and maintain",
         "Made with eco-conscious fibers"],
        ["Hand-tufted wool blend for plush texture",
         "Geometric pattern fits modern interiors",
         "Tightly woven to resist shedding",
         "Recommended pad underneath for added grip",
         "Imported, professional cleaning recommended"],
    ],
    "outdoor_rug": [
        ["Weather-resistant polypropylene fibers",
         "UV-protected colors won't fade in sunlight",
         "Mold and mildew resistant for damp conditions",
         "Hose down to clean; air-dry quickly",
         "Ideal for patios, decks, and covered porches"],
        ["Reversible design doubles the look",
         "Flat-weave construction stays in place outdoors",
         "Lightweight and easy to roll up for storage",
         "Fade-resistant for 1000+ hours of sun exposure",
         "Works on uneven surfaces"],
    ],
    "hallway_runner": [
        ["Long, narrow design fits hallways and entryways",
         "Non-skid latex backing prevents sliding",
         "Stain-resistant for high-traffic foot paths",
         "Available in lengths from 6 ft to 14 ft",
         "Machine-washable on gentle cycle"],
        ["Hand-knotted detail in transitional pattern",
         "Compact pile profile fits under doors",
         "Color-bleed-resistant dye",
         "Works in narrow spaces and stairways",
         "Spot-clean with mild soap and water"],
    ],
    "shag_rug": [
        ["1.5\" plush pile for ultimate softness underfoot",
         "Hand-woven shag construction",
         "Hypoallergenic synthetic fibers",
         "Ideal for bedrooms and lounges",
         "Vacuum without beater bar to preserve pile"],
        ["Faux fur texture adds modern luxury",
         "Heat-set polyester yarns resist matting",
         "Available in solid and ombre colorways",
         "Recommended rug pad for hardwood floors",
         "Brush gently to maintain loft"],
    ],
}

PATTERNS_BY_CATEGORY = {
    "area_rug": ["Persian Medallion", "Modern Geometric", "Vintage Distressed", "Tribal Bohemian", "Solid Color"],
    "outdoor_rug": ["Striped", "Trellis", "Geometric", "Solid Color", "Reversible Two-Tone"],
    "hallway_runner": ["Persian", "Trellis", "Tribal", "Solid", "Floral"],
    "shag_rug": ["Solid", "Ombre", "Faux Fur", "Multi-Tone", "Trellis Texture"],
}

# Retailer URL templates (synthetic but plausible structure)
URL_TEMPLATES = {
    "amazon": "https://www.amazon.com/{slug}/dp/{sku}",
    "walmart": "https://www.walmart.com/ip/{slug}/{sku}",
    "wayfair": "https://www.wayfair.com/rugs/pdp/{slug}-{sku}.html",
}

# Image CDN templates
IMG_TEMPLATES = {
    "amazon": "https://m.media-amazon.com/images/I/{sku}AC_SL1500_.jpg",
    "walmart": "https://i5.walmartimages.com/seo/{slug}_{sku}.jpg",
    "wayfair": "https://assets.wfcdn.com/im/{sku}/resize-h400-w400/{slug}.jpg",
}

# Product name pools per category — pick top N for each retailer to keep variety
NAME_POOLS = {
    "area_rug": [
        ("Vintage Distressed Area Rug, 8x10, Soft Indoor Carpet for Living Room",
         "vintage-distressed-area-rug-8x10"),
        ("Modern Geometric Area Rug, Machine Washable, Non-Slip Backing",
         "modern-geometric-area-rug-washable"),
        ("Traditional Persian-Style Wool Blend Rug, 6x9, Burgundy",
         "traditional-persian-wool-blend-rug-6x9"),
        ("Bohemian Tribal Indoor Area Rug, Beige and Cream, 5x7",
         "bohemian-tribal-area-rug-5x7"),
        ("Contemporary Solid Color Area Rug, Charcoal Gray, 9x12",
         "contemporary-solid-area-rug-9x12-charcoal"),
        ("Hand-Tufted Wool Area Rug with Floral Motif, 8x10",
         "hand-tufted-wool-floral-rug-8x10"),
    ],
    "outdoor_rug": [
        ("Indoor/Outdoor Striped Patio Rug, 8x10, Fade-Resistant Polypropylene",
         "indooroutdoor-striped-patio-rug-8x10"),
        ("Reversible Outdoor Rug, Geometric Pattern, 5x7, Weather-Resistant",
         "reversible-outdoor-rug-geometric-5x7"),
        ("Flat-Weave Outdoor Rug for Deck and Porch, 9x12, Navy and White",
         "flatweave-outdoor-rug-9x12-navy"),
        ("UV-Protected Outdoor Rug, Trellis Pattern, 6x9, Sand",
         "uv-protected-outdoor-rug-trellis-6x9"),
        ("Lightweight Polypropylene Outdoor Mat, 4x6, Easy to Clean",
         "lightweight-polypropylene-outdoor-mat-4x6"),
        ("Bohemian Outdoor Rug, Multicolor Stripes, 8x10",
         "bohemian-outdoor-rug-multicolor-8x10"),
    ],
    "hallway_runner": [
        ("Persian Style Hallway Runner Rug, 2x10 ft, Non-Slip Backing",
         "persian-style-hallway-runner-2x10"),
        ("Vintage Distressed Hallway Runner, 2x12, Machine Washable",
         "vintage-distressed-hallway-runner-2x12"),
        ("Modern Trellis Runner Rug, 2.5x8, Stain Resistant",
         "modern-trellis-runner-rug-25x8"),
        ("Tribal Bohemian Long Runner, 3x14, Beige and Rust",
         "tribal-bohemian-long-runner-3x14"),
        ("Solid Gray Hallway Runner, 2x10, Pet-Friendly",
         "solid-gray-hallway-runner-2x10"),
        ("Floral Cotton Blend Hallway Runner, 2x12, Cream",
         "floral-cotton-blend-runner-2x12-cream"),
    ],
    "shag_rug": [
        ("Plush High-Pile Shag Area Rug, 8x10, Cream",
         "plush-shag-area-rug-8x10-cream"),
        ("Soft Faux Fur Shag Rug for Bedroom, 5x7, White",
         "soft-faux-fur-shag-rug-5x7-white"),
        ("Modern Ombre Shag Rug, 6x9, Gray Gradient",
         "modern-ombre-shag-rug-6x9-gray"),
        ("Cozy Multi-Tone Shag Rug, 8x10, Beige and Charcoal",
         "cozy-multitone-shag-rug-8x10"),
        ("Luxe High-Pile Shag Rug, 5x7, Blush Pink",
         "luxe-highpile-shag-rug-5x7-blush"),
        ("Shaggy Faux Wool Rug, 7x9, Ivory",
         "shaggy-fauxwool-rug-7x9-ivory"),
    ],
}

# Price ranges by category (in dollars; midpoint × small variance)
PRICE_BANDS = {
    "area_rug": [79.99, 124.99, 189.50, 249.00, 349.00, 478.00],
    "outdoor_rug": [49.99, 79.00, 119.99, 169.50, 219.00, 289.00],
    "hallway_runner": [39.99, 59.99, 89.00, 124.00, 159.99, 199.00],
    "shag_rug": [89.99, 129.99, 179.00, 249.00, 329.00, 419.00],
}

RATINGS = ["4.2 out of 5 stars", "4.4 out of 5 stars", "4.5 out of 5 stars",
           "4.6 out of 5 stars", "4.7 out of 5 stars", "4.8 out of 5 stars"]
REVIEWS = ["143", "287", "512", "894", "1247", "2103", "3902", "5614"]


def fake_sku(retailer: str, idx: int) -> str:
    """Generate a plausible SKU/ID string for the retailer."""
    if retailer == "amazon":
        return f"B0{retailer[0].upper()}{idx:08d}"[:10]
    if retailer == "walmart":
        return f"{1000000000 + idx * 7919}"
    # wayfair
    return f"w0{idx:08d}"[:10]


def build_product(retailer: str, category: str, name_idx: int, var_idx: int) -> dict:
    """Build one product dict for the given retailer + category."""
    name, slug = NAME_POOLS[category][name_idx]
    sku = fake_sku(retailer, name_idx * 11 + var_idx + hash(retailer) % 7)
    details = DETAIL_TEMPLATES[category][var_idx % len(DETAIL_TEMPLATES[category])]
    pattern = PATTERNS_BY_CATEGORY[category][name_idx % len(PATTERNS_BY_CATEGORY[category])]
    price_band = PRICE_BANDS[category]
    price = f"{price_band[(name_idx + var_idx) % len(price_band)]:.2f}"
    rating = RATINGS[(name_idx + var_idx) % len(RATINGS)]
    review_count = REVIEWS[(name_idx * 3 + var_idx) % len(REVIEWS)]

    return {
        "category": category,
        "url": URL_TEMPLATES[retailer].format(slug=slug, sku=sku),
        "name": name,
        "price": price,
        "details": list(details),
        "pattern": pattern,
        "image_url": IMG_TEMPLATES[retailer].format(slug=slug, sku=sku),
        "rating": rating,
        "review_count": review_count,
    }


def build_dataset(retailer: str) -> dict:
    """Build the full dataset for a retailer: 5 products per category, 4 categories = 20 products."""
    products = []
    for category in CATEGORIES:
        for i in range(5):
            var_idx = i % len(DETAIL_TEMPLATES[category])
            products.append(build_product(retailer, category, i, var_idx))
    return {
        "retailer": retailer,
        "scraped_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "note": "SAMPLE DATA — synthetic products for testing. Replace with real scraped data via scripts/refresh_dataset.py.",
        "products": products,
    }


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for retailer in ["amazon", "walmart", "wayfair"]:
        dataset = build_dataset(retailer)
        out_path = DATA_DIR / f"{retailer}_products.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=2)
        print(f"Wrote {out_path} ({len(dataset['products'])} products)")


if __name__ == "__main__":
    main()
