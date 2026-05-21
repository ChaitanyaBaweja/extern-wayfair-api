# Scripts

Operational utilities that live **outside** the FastAPI app. The runtime API only reads files; these scripts produce or update those files.

## `seed_sample_data.py`

One-shot script that populates `app/data/amazon_products.json`, `walmart_products.json`, and `wayfair_products.json` with **synthetic-but-realistic sample products** (5 per category × 4 categories = 20 products per retailer = 60 total).

Use this for:
- Initial local development
- CI tests that need predictable product data
- A new dev's first-time setup

```bash
python scripts/seed_sample_data.py
```

The script is idempotent — running it again regenerates fresh sample files with current timestamps.

The sample data is clearly marked in each JSON file via a `"note"` field so downstream consumers know it's not real:

```json
{
  "retailer": "amazon",
  "scraped_at": "2026-05-21T...",
  "note": "SAMPLE DATA - synthetic products for testing. Replace with real scraped data via scripts/refresh_dataset.py.",
  "products": [ ... ]
}
```

---

## `refresh_dataset.py` (to be implemented)

**Status:** not yet implemented. This README describes what it should do.

The refresh script runs **offline** (cron, GitHub Actions, or manual TA-triggered) and produces the same JSON files that `seed_sample_data.py` produces, but with real scraped product data.

### Inputs

| Input | Source |
|-------|--------|
| ScraperAPI key | `.env` file: `SCRAPER_API_KEY=...` |
| Categories list | `app/config.py` → `VALID_CATEGORIES` |
| Per-category search URL mapping | Inline constant in the script (Amazon: `?k=area+rugs`, etc.) |

### Outputs

Same JSON shape as `seed_sample_data.py` produces:

```
app/data/
├── amazon_products.json
├── walmart_products.json
└── wayfair_products.json
```

Each file shape:

```json
{
  "retailer": "amazon",
  "scraped_at": "<ISO 8601 timestamp>",
  "products": [
    {
      "category": "area_rug",
      "url": "<canonical URL>",
      "name": "<product title>",
      "price": "78.48",
      "details": ["bullet 1", "bullet 2", ...],
      "pattern": "...",
      "image_url": "...",
      "rating": "4.4 out of 5 stars",
      "review_count": "3902"
    },
    ...
  ]
}
```

### Per-retailer steps

For each `(category, retailer)`:

1. **Resolve search URL** from internal category → URL mapping
2. **Fetch the search results** via ScraperAPI (use `&country_code=us&device_type=desktop`)
3. **Extract up to 10 product URLs** from the search results HTML
4. **For each product URL**, fetch the product page via ScraperAPI
5. **Parse each product page** into the schema above
6. **Dedupe by canonical URL** (Amazon redirects can produce multiple raw URLs pointing at the same `/dp/XXXX`)

### Field extraction notes (per retailer)

**Amazon:**
- `url` → from `<link rel="canonical">`
- `name` → `#productTitle`
- `price` → `span.a-price-whole` + `span.a-price-fraction`
- `details` → `#feature-bullets ul li span.a-list-item`
- `pattern` → `#inline-twister-expanded-dimension-text-pattern_name`
- `image_url` → `#landingImage` (data-old-hires preferred, src fallback)
- `rating` → `span.a-icon-alt` filtered by "out of 5"
- `review_count` → `#acrCustomerReviewText` (strip parentheses)

**Walmart:**
- Product links via `a[href*="/ip/"]` from search results
- Per-product fields parsed via product page HTML (Walmart uses `data-testid` attributes — see existing P3 patterns)

**Wayfair:**
- Product links via `[data-test-id="ListingCard"]` cards on search/browse pages
- Per-product fields from card markup AND PDP if needed
- The largest `<img>` per card (skipping "Wayfair Verified" badges) is the product image

### Recommended cadence

| Cadence | Pros | Cons |
|---------|------|------|
| Weekly | Reasonably current | Most ops work |
| Monthly | Less effort | Students may notice stale products |
| Manual / on-demand | Fully under your control | Risk of forgetting |

Default recommendation: **weekly**.

### ScraperAPI usage estimate

Per refresh:
- 4 categories × 3 retailers × (1 search + 10 products) = **132 ScraperAPI credits per refresh**

Weekly: ~528 credits/month. Well under the 1000/month free tier.

### Implementation hints

- Use `httpx` (async) for concurrent fetches; keep per-domain concurrency low (3-5) to be polite
- Save intermediate progress — if the script crashes 60% of the way through, you don't want to start over
- Validate each product (URL non-empty, name non-empty) before adding to output
- Write to a `.tmp` file first, then rename to the final filename — avoids partial writes serving from disk
- Log per-retailer success/failure counts; alert on >50% failure rate

### Reference implementations

The current P2/P3 workflow JSON files contain working parsers in their Code nodes:

| File | Useful for |
|------|------------|
| `Wayfair final bots/Wayfair Market Trend Discovery Agent Final.json` → `Read Item Details` node | Amazon product page parsing logic |
| `Wayfair final bots/updated bots/P3_Competitor_Monitoring_Agent.json` → `Extract Walmart Links` node | Walmart search-result link extraction |
| `Wayfair final bots/updated bots/P3_Competitor_Monitoring_Agent.json` → `Extract Rug Products` node | Wayfair PDP listing card parsing |

Port the JavaScript regex/selectors to Python (`selectolax` or `BeautifulSoup4` is recommended).

---

## Notes on hosting

When deployed on AWS (or wherever the API runs), `scripts/` does **not** need to be on the server unless you're scheduling refreshes there via cron. A common pattern is:

- **Option A — Cron on the API server:** copy `scripts/` to the same machine, install scraper deps, schedule via `cron` or `systemd timer`
- **Option B — Refresh elsewhere, deploy data files:** run `scripts/refresh_dataset.py` on a separate machine (TA laptop, GitHub Actions runner), then `scp` / `rsync` the resulting `.json` files into `app/data/` on the API server. Simplest if you don't want scraper deps on the production box.

Both are fine. Pick whichever matches your existing ops workflow.
