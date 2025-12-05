# Extern Trends API

FastAPI server providing curated rug trend data for Wayfair's n8n market trend analysis workflow.

## Current Status

| Component | Status |
|-----------|--------|
| Instagram images | 8 images (2 per category) |
| Pinterest images | 8 images (2 per category) |
| Blog PDFs | 4 PDFs (1 per category) |
| Metadata JSON files | Populated |
| API endpoints | Working |

## Features

- **Instagram Trends** - Social media posts with base64 encoded images
- **Pinterest Trends** - Pin data with base64 encoded images
- **Blog Content** - Editorial articles with extracted PDF text
- **Category Filtering** - All endpoints support filtering by rug category

## Project Structure

```
extern-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── models.py            # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── instagram.py     # Instagram endpoint
│   │   ├── pinterest.py     # Pinterest endpoint
│   │   └── blogs.py         # Blogs endpoint (with PDF extraction)
│   ├── data/
│   │   ├── instagram.json   # Instagram metadata
│   │   ├── pinterest.json   # Pinterest metadata
│   │   └── blogs.json       # Blog metadata
│   └── assets/
│       ├── instagram/       # Instagram images (8 total)
│       ├── pinterest/       # Pinterest images (8 total)
│       └── blogs/           # Blog PDFs (4 total)
├── requirements.txt
├── .env
└── README.md
```

---

## Asset File Naming Conventions

### Instagram Images
Place in: `app/assets/instagram/`

| Filename | Category |
|----------|----------|
| `area_rug_1.jpg` | area_rug |
| `area_rug_2.jpg` | area_rug |
| `outdoor_rug_1.jpg` | outdoor_rug |
| `outdoor_rug_2.jpg` | outdoor_rug |
| `hallway_runner_1.jpg` | hallway_runner |
| `hallway_runner_2.jpg` | hallway_runner |
| `shag_rug_1.jpg` | shag_rug |
| `shag_rug_2.jpg` | shag_rug |

### Pinterest Images
Place in: `app/assets/pinterest/`

| Filename | Category |
|----------|----------|
| `area_rug_1.jpg` | area_rug |
| `area_rug_2.jpg` | area_rug |
| `outdoor_rug_1.jpg` | outdoor_rug |
| `outdoor_rug_2.jpg` | outdoor_rug |
| `hallway_runner_1.jpg` | hallway_runner |
| `hallway_runner_2.jpg` | hallway_runner |
| `shag_rug_1.jpg` | shag_rug |
| `shag_rug_2.jpg` | shag_rug |

### Blog PDFs
Place in: `app/assets/blogs/`

| Filename | Category |
|----------|----------|
| `area_rug.pdf` | area_rug |
| `outdoor_rug.pdf` | outdoor_rug |
| `hallway_runner.pdf` | hallway_runner |
| `shag_rug.pdf` | shag_rug |

**Note:** Images can be `.jpg`, `.jpeg`, or `.png` format.

---

## Setup Instructions

### 1. Create Virtual Environment

```bash
cd extern-api
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Server

> **Note:** Assets and metadata JSON files are already populated. Skip to running the server.

```bash
# Option 1: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Python
python -m app.main
```

### 4. Verify It's Running

Open in browser: http://localhost:8000/docs

---

## Adding/Updating Assets (Optional)

If you need to update the assets:

1. **Add image/PDF files** to the appropriate directories:
   - `app/assets/instagram/` - Instagram images
   - `app/assets/pinterest/` - Pinterest images
   - `app/assets/blogs/` - Blog PDFs

2. **Update metadata JSON files** in `app/data/`:
   - `instagram.json` - Instagram post metadata
   - `pinterest.json` - Pinterest pin metadata
   - `blogs.json` - Blog article metadata

3. **Restart the server** to pick up changes (or it auto-reloads in dev mode)

---

## API Endpoints

### Health Check
```
GET /api/health
```

### Instagram Trends
```
GET /api/trends/instagram
GET /api/trends/instagram?category=outdoor_rug&limit=3
```

### Pinterest Trends
```
GET /api/trends/pinterest
GET /api/trends/pinterest?category=shag_rug&limit=3
```

### Blog Trends
```
GET /api/trends/blogs
GET /api/trends/blogs?category=area_rug&limit=2
```

### Categories
```
GET /api/categories
```

---

## Testing with curl

```bash
# Health check
curl http://localhost:8000/api/health

# Get all Instagram posts
curl http://localhost:8000/api/trends/instagram

# Get outdoor rug Pinterest pins (limit 2)
curl "http://localhost:8000/api/trends/pinterest?category=outdoor_rug&limit=2"

# Get all categories with counts
curl http://localhost:8000/api/categories
```

---

## Response Examples

### Instagram Response
```json
{
  "source": "instagram",
  "category": "outdoor_rug",
  "items": [
    {
      "id": "ig_outdoor_rug_1",
      "url": "https://instagram.com/p/example123",
      "caption": "Summer patio goals! This outdoor rug ties everything together",
      "hashtags": ["#outdoorrug", "#patiodecor", "#summerstyle"],
      "engagement": 1847,
      "posted_at": "2024-12-01",
      "image_base64": "iVBORw0KGgo...",
      "image_mime_type": "image/jpeg"
    }
  ]
}
```

### Categories Response
```json
{
  "categories": [
    {
      "id": "area_rug",
      "name": "Area Rug",
      "counts": {
        "instagram": 2,
        "pinterest": 2,
        "blogs": 1
      }
    }
  ]
}
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `DEBUG` | `false` | Enable debug mode (auto-reload) |

---

## Rug Categories

| ID | Name | Description |
|----|------|-------------|
| `area_rug` | Area Rug | Movable floor covering for room sections. 3'×5' to 10'×14'+. |
| `outdoor_rug` | Outdoor Rug | Weather-resistant for patios, decks. Thin, quick-drying. |
| `hallway_runner` | Hallway Runner | Long, narrow for pathways. 2'-3' wide, 6'-14'+ long. |
| `shag_rug` | Shag Rug | High-pile (1"+), plush texture. For bedrooms, lounges. |

---

## Integration with n8n

Set the environment variable in your n8n instance:

```
EXTERN_API_URL=http://localhost:8000
```

Or if running on EC2:
```
EXTERN_API_URL=http://your-ec2-ip:8000
```

---

## Troubleshooting

### "No items returned"
- Check that JSON metadata files are populated (not empty arrays)
- Verify image/PDF files exist in the correct directories
- Check category parameter matches one of: `area_rug`, `outdoor_rug`, `hallway_runner`, `shag_rug`

### "Image not found" warnings
- Check file naming matches exactly what's in the JSON metadata
- Ensure files are in the correct subdirectory (instagram/, pinterest/, blogs/)

### "PDF extraction failed"
- Ensure PyPDF2 is installed: `pip install PyPDF2`
- Verify PDF files are not corrupted

### CORS issues
- CORS is enabled for all origins by default
- Check that the API is accessible from your n8n instance

### Server won't start
- Check port 8000 is not in use: `netstat -ano | findstr :8000` (Windows)
- Ensure virtual environment is activated
- Verify all dependencies installed: `pip install -r requirements.txt`
