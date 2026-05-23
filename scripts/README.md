# Scripts

Operational utilities that live **outside** the FastAPI app. The runtime API
only reads files; these scripts produce or update those files.

## Files

| File | Purpose |
|------|---------|
| `extractors.js` | Three Chrome-console JS blocks (Amazon / Walmart / Wayfair) that scrape each retailer's category pages and auto-download `<retailer>_products.json`. |
| `MANUAL_REFRESH_RUNBOOK.md` | Step-by-step procedure for refreshing the product datasets — what URLs to visit, what to paste, how to push and deploy. **Read this first** when product data needs refreshing. |
| `seed_sample_data.py` | One-shot script that fills `app/data/*_products.json` with synthetic sample data for local dev / CI. Useful for a brand-new clone before the first real refresh. |

## Refreshing product data

See **[MANUAL_REFRESH_RUNBOOK.md](./MANUAL_REFRESH_RUNBOOK.md)**.

The refresh is intentionally manual (not automated): three retailers, no
budget for scraping APIs, student-facing demo data only. Manual every few
weeks is more reliable than fighting bot detection in a cron job.

## Initial dev setup

For a new clone with empty `app/data/`:

```bash
python scripts/seed_sample_data.py
```

This generates synthetic-but-realistic data (5 products × 4 categories per
retailer) so the API responds to all endpoints. Replace with real data via
the runbook when you're ready.

## Notes on hosting

`scripts/` does not need to be on the production server. Run the refresh
locally, push the data JSONs, and pull on the server. See the runbook's
STEP 7.
