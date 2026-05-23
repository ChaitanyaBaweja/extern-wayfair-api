# Manual Data Refresh — Runbook

> **Cadence:** every 3–6 weeks (or when student reports show stale products).
> **Time required:** ~30 minutes (mostly waiting between Wayfair pages).
> **Tools required:** Chrome, your AWS SSH access, this repo cloned locally.

The Extern API serves **pre-scraped** product data. There is no live scraping
and no scheduled job. When the data gets stale, follow this runbook to
refresh it. All the heavy lifting is done by three paste-into-Chrome-console
JavaScript blocks that live in `scripts/extractors.js`.

---

## Order of operations

1. **Wayfair first** — PerimeterX rate-limits aggressive sessions, so do
   Wayfair while your IP is fresh. Do Amazon and Walmart afterward.
2. Within each retailer, you'll visit 4 search pages (one per category) and
   paste the same JS block each time.
3. After the 4th category for a retailer, a JSON file auto-downloads to your
   Downloads folder.
4. Move the 3 JSON files into `app/data/`, commit, push, pull on AWS.

---

## STEP 1 — Open Chrome DevTools

In Chrome: hit `F12` (or `Cmd+Opt+I` on Mac) and click the **Console** tab.

Keep DevTools open for the entire session. **Do NOT close the tab between
categories** — your progress is stored in localStorage per-origin, so a new
tab on the same origin is fine, but a fresh incognito window resets you.

---

## STEP 2 — Wayfair (do this first)

Open `scripts/extractors.js`, find the section marked **WAYFAIR**, and copy
the entire `(async () => { … })();` block.

Visit each URL below in turn, **pasting the same block** into the console
and hitting Enter. Wait 5–10 minutes between pages to avoid PerimeterX.

| # | Category | URL |
|---|----------|-----|
| 1 | area_rug | https://www.wayfair.com/rugs/sb0/area-rugs-c1849518.html |
| 2 | outdoor_rug | https://www.wayfair.com/outdoor/sb0/outdoor-rugs-c215386.html |
| 3 | shag_rug | https://www.wayfair.com/rugs/sb1/shag-area-rugs-c1849518-a26168~89321.html |
| 4 | hallway_runner | https://www.wayfair.com/rugs/sb1/runner-area-rugs-c1849518-a44095~414114.html |

**What you'll see in the console:**
```
[Wayfair] Extracting area_rug… (will scroll to trigger lazy loading)
[Wayfair] Found 30 listing cards.
[Wayfair] ✅ Saved 30 products for area_rug.
[Wayfair] Progress: 1/4 categories → area_rug
[Wayfair] Still to do: outdoor_rug, shag_rug, hallway_runner
```

After the 4th category, the script auto-downloads `wayfair_products.json`.

### If Wayfair blocks you

You'll see "Access to this page has been denied" or `[Wayfair] ❌ 0 products
extracted` in the console. Two options:

- **Wait 30+ minutes** and try the blocked category again.
- **Skip it** — uncomment the **PARTIAL DOWNLOAD** block at the bottom of
  `extractors.js` to get whatever you scraped so far. Then merge with the
  existing `app/data/wayfair_products.json` to keep the categories you
  couldn't refresh. (Use the merge snippet below.)

#### Merge snippet (Python)

```python
import json
with open('wayfair_products_partial.json') as f: new = json.load(f)
with open('app/data/wayfair_products.json') as f: old = json.load(f)
refreshed = set(new['partial_categories'])
keep = [p for p in old['products'] if p['category'] not in refreshed]
out = {'retailer': 'wayfair', 'scraped_at': new['scraped_at'],
       'products': keep + new['products']}
with open('app/data/wayfair_products.json', 'w') as f:
    json.dump(out, f, indent=2)
print(f"Merged: {len(out['products'])} total")
```

---

## STEP 3 — Amazon

Copy the **AMAZON** block from `scripts/extractors.js`. Paste on each:

| # | Category | URL |
|---|----------|-----|
| 1 | area_rug | https://www.amazon.com/s?k=area+rug |
| 2 | outdoor_rug | https://www.amazon.com/s?k=outdoor+rug |
| 3 | shag_rug | https://www.amazon.com/s?k=shag+rug |
| 4 | hallway_runner | https://www.amazon.com/s?k=hallway+runner |

After the 4th category, `amazon_products.json` auto-downloads.

---

## STEP 4 — Walmart

Copy the **WALMART** block from `scripts/extractors.js`. Paste on each:

| # | Category | URL |
|---|----------|-----|
| 1 | area_rug | https://www.walmart.com/search?q=area+rug |
| 2 | outdoor_rug | https://www.walmart.com/search?q=outdoor+rug |
| 3 | shag_rug | https://www.walmart.com/search?q=shag+rug |
| 4 | hallway_runner | https://www.walmart.com/search?q=hallway+runner |

After the 4th category, `walmart_products.json` auto-downloads.

---

## STEP 5 — Sanity-check the downloads

You should now have 3 files in `Downloads/`:

```
amazon_products.json
walmart_products.json
wayfair_products.json
```

Quick check in PowerShell or bash:
```bash
for f in amazon walmart wayfair; do
  python -c "
import json
d = json.load(open('${f}_products.json'))
print('${f}:', len(d['products']), 'products')
from collections import Counter
print('  by category:', dict(Counter(p['category'] for p in d['products'])))
print('  url coverage:', sum(1 for p in d['products'] if p['url']) / len(d['products']))
print('  image coverage:', sum(1 for p in d['products'] if p['image_url']) / len(d['products']))
"
done
```

Expected: ~30 products per category, ≥95% url+image coverage.
If any category has 0 or way fewer than expected, re-run that category.

---

## STEP 6 — Push to GitHub

Copy the 3 files into `app/data/` (overwriting), then:

```bash
cd extern-wayfair-api
cp ~/Downloads/{amazon,walmart,wayfair}_products.json app/data/
git add app/data/amazon_products.json app/data/walmart_products.json app/data/wayfair_products.json
git commit -m "Refresh product datasets ($(date +%Y-%m-%d))"
git push origin main
```

---

## STEP 7 — Deploy on AWS

```bash
ssh ubuntu@ip-172-31-81-100
cd ~/extern-wayfair-api
git pull
# restart the API service (whatever command you use — systemctl/pm2/screen)
```

If `git pull` complains about local changes:
```bash
git stash      # park whatever's dirty
git pull       # take the new data
# (don't `git stash pop` unless you actually want those changes back)
```

---

## STEP 8 — Smoke test

From your local machine:

```bash
# Call twice — should return DIFFERENT products (shuffle is working)
curl 'http://34.196.186.128:8000/api/products/amazon?category=area_rug&limit=3'
curl 'http://34.196.186.128:8000/api/products/amazon?category=area_rug&limit=3'

# Check Wayfair pool size matches what you scraped
curl 'http://34.196.186.128:8000/api/products/wayfair?category=area_rug&limit=50' \
  | python -c "import json,sys; print('pool size:', json.load(sys.stdin)['total_products'])"
```

Done. The n8n workflows will start serving the fresh data on their next run.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Console says "Could not detect category" | URL doesn't contain a known keyword. Edit `CATEGORY` constant at top of block, or visit the right URL. |
| Block runs but extracts 0 products | Selector probably changed. Compare against `extractors.js` source against the live page DOM. |
| Wayfair "Access denied" page | PerimeterX rate-limit. Wait 30+ min or use VPN. |
| Browser asks "Allow multiple downloads?" | Click Allow. Happens if you somehow ran multiple retailers' download triggers in one tab. |
| `git pull` blocked on AWS | `git stash` then `git pull`. Local changes shouldn't exist on the box; if they do they were probably test edits. |
| Want to start over | In console: `Object.keys(localStorage).filter(k=>k.startsWith('wf_')).forEach(k=>localStorage.removeItem(k))` |
