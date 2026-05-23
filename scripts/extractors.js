/* =============================================================================
 * MANUAL DATA-REFRESH EXTRACTORS
 *
 * Three self-contained blocks (one per retailer). Paste the matching block
 * into Chrome DevTools Console on each of the 4 category search pages.
 *
 *   - Each block auto-detects the category from the page URL.
 *   - Each extraction is saved to localStorage (per-origin).
 *   - After all 4 categories for that retailer are extracted, the block
 *     auto-downloads `<retailer>_products.json` to your Downloads folder.
 *
 * Full procedure: see scripts/MANUAL_REFRESH_RUNBOOK.md
 * =============================================================================
 */


/* ---------------------------------------------------------------------------
 *  AMAZON  —  https://www.amazon.com/s?k=area+rug   (etc.)
 *  Paste the block below on each of the 4 Amazon search pages.
 * ---------------------------------------------------------------------------
 */
(async () => {
  const STORAGE_PREFIX = 'wf_amazon_';
  const ALL = ['area_rug', 'outdoor_rug', 'shag_rug', 'hallway_runner'];
  const TARGET_PER_CATEGORY = 30;

  const url = decodeURIComponent(window.location.href).toLowerCase();
  const CATEGORY =
    /outdoor/.test(url) ? 'outdoor_rug' :
    /shag/.test(url)    ? 'shag_rug' :
    /hallway|runner/.test(url) ? 'hallway_runner' :
    /area/.test(url)    ? 'area_rug' : null;

  if (!CATEGORY) {
    console.error('[Amazon] Could not detect category from URL. Visit one of: area+rug, outdoor+rug, shag+rug, hallway+runner.');
    return;
  }
  console.log(`[Amazon] Extracting ${CATEGORY}…`);

  const cards = document.querySelectorAll('div[data-component-type="s-search-result"]');
  console.log(`[Amazon] Found ${cards.length} search-result cards.`);

  const products = [];
  cards.forEach(card => {
    const txt = card.innerText || '';
    const titleEl = card.querySelector('h2 span') || card.querySelector('h2');
    const linkEl  = card.querySelector('h2 a') || card.querySelector('a.a-link-normal[href*="/dp/"]');
    const imgEl   = card.querySelector('img.s-image');
    const name = titleEl ? titleEl.innerText.trim() : null;
    if (!name) return;
    let href = linkEl ? linkEl.getAttribute('href') : null;
    if (href && !href.startsWith('http')) href = `https://www.amazon.com${href.split('?')[0]}`;
    const priceM = txt.match(/\$([\d,]+\.\d{2})/);
    const ratingM = txt.match(/(\d\.\d)\s+out of 5/);
    const reviewsM = txt.match(/(\d[\d,]*)\s+ratings?/) || txt.match(/\(([\d,]+)\)/);
    const reviews = reviewsM ? (reviewsM[1] || reviewsM[2]).replace(/,/g, '') : null;
    products.push({
      category: CATEGORY,
      url: href,
      name,
      price: priceM ? `$${priceM[1]}` : null,
      details: [],
      pattern: null,
      image_url: imgEl ? imgEl.src : null,
      rating: ratingM ? parseFloat(ratingM[1]) : null,
      review_count: reviews ? parseInt(reviews, 10) : null,
    });
  });

  const top = products.slice(0, TARGET_PER_CATEGORY);
  localStorage.setItem(STORAGE_PREFIX + CATEGORY, JSON.stringify(top));
  console.log(`[Amazon] ✅ Saved ${top.length} products for ${CATEGORY}.`);

  const done = ALL.filter(c => localStorage.getItem(STORAGE_PREFIX + c));
  console.log(`[Amazon] Progress: ${done.length}/4 categories → ${done.join(', ')}`);
  if (done.length < 4) {
    const left = ALL.filter(c => !done.includes(c));
    console.log(`[Amazon] Still to do: ${left.join(', ')}`);
    return;
  }

  const all = ALL.flatMap(c => JSON.parse(localStorage.getItem(STORAGE_PREFIX + c)));
  const payload = { retailer: 'amazon', scraped_at: new Date().toISOString(), products: all };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'amazon_products.json';
  document.body.appendChild(a); a.click();
  setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(a.href); }, 1000);
  console.log(`[Amazon] 🎉 Downloaded amazon_products.json (${all.length} total products).`);
  console.log('[Amazon] To reset for next refresh: ' + ALL.map(c => `localStorage.removeItem('${STORAGE_PREFIX + c}')`).join('; '));
})();


/* ---------------------------------------------------------------------------
 *  WALMART  —  https://www.walmart.com/search?q=area+rug   (etc.)
 *  Paste the block below on each of the 4 Walmart search pages.
 * ---------------------------------------------------------------------------
 */
(async () => {
  const STORAGE_PREFIX = 'wf_walmart_';
  const ALL = ['area_rug', 'outdoor_rug', 'shag_rug', 'hallway_runner'];
  const TARGET_PER_CATEGORY = 30;

  const url = decodeURIComponent(window.location.href).toLowerCase();
  const CATEGORY =
    /outdoor/.test(url) ? 'outdoor_rug' :
    /shag/.test(url)    ? 'shag_rug' :
    /hallway|runner/.test(url) ? 'hallway_runner' :
    /area/.test(url)    ? 'area_rug' : null;

  if (!CATEGORY) {
    console.error('[Walmart] Could not detect category from URL.');
    return;
  }
  console.log(`[Walmart] Extracting ${CATEGORY}…`);

  // Scroll a bit to trigger any lazy-loaded tiles
  for (let i = 0; i < 4; i++) {
    window.scrollBy(0, 1200);
    await new Promise(r => setTimeout(r, 500));
  }
  window.scrollTo(0, 0);

  const cards = document.querySelectorAll('div[data-item-id]');
  console.log(`[Walmart] Found ${cards.length} item cards.`);

  const products = [];
  cards.forEach(card => {
    const txt = card.innerText || '';
    const linkEl  = card.querySelector('a[href*="/ip/"], a[href*="/sp/track"]');
    const imgEl   = card.querySelector('img[src*="walmartimages"]') || card.querySelector('img');
    const titleEl = card.querySelector('[data-automation-id="product-title"]') || card.querySelector('span.w_iUH7') || card.querySelector('span');
    const name = titleEl ? titleEl.innerText.trim() : null;
    if (!name || name.length < 8) return;

    let href = linkEl ? linkEl.getAttribute('href') : null;
    // Walmart sponsored links route through /sp/track?...&rd=<real-url>
    if (href && href.includes('/sp/track')) {
      const m = href.match(/[?&]rd=([^&]+)/);
      if (m) href = decodeURIComponent(m[1]);
    }
    if (href && !href.startsWith('http')) href = `https://www.walmart.com${href}`;
    if (href) href = href.split('?')[0];

    const priceM = txt.match(/\$([\d,]+\.\d{2})/) || txt.match(/Now\s*\$([\d,]+\.\d{2})/);
    const ratingM = txt.match(/(\d(?:\.\d)?)\s*out of 5\s*Stars/i) || txt.match(/\b(\d\.\d)\b\s*\(/);
    const reviewsM = txt.match(/\((\d[\d,]*)\)/);

    products.push({
      category: CATEGORY,
      url: href,
      name,
      price: priceM ? `$${priceM[1]}` : null,
      details: [],
      pattern: null,
      image_url: imgEl ? imgEl.src : null,
      rating: ratingM ? parseFloat(ratingM[1]) : null,
      review_count: reviewsM ? parseInt(reviewsM[1].replace(/,/g, ''), 10) : null,
    });
  });

  // Dedupe by URL within category
  const seen = new Set();
  const unique = products.filter(p => {
    if (!p.url || seen.has(p.url)) return false;
    seen.add(p.url);
    return true;
  });
  const top = unique.slice(0, TARGET_PER_CATEGORY);
  localStorage.setItem(STORAGE_PREFIX + CATEGORY, JSON.stringify(top));
  console.log(`[Walmart] ✅ Saved ${top.length} products for ${CATEGORY}.`);

  const done = ALL.filter(c => localStorage.getItem(STORAGE_PREFIX + c));
  console.log(`[Walmart] Progress: ${done.length}/4 categories → ${done.join(', ')}`);
  if (done.length < 4) {
    const left = ALL.filter(c => !done.includes(c));
    console.log(`[Walmart] Still to do: ${left.join(', ')}`);
    return;
  }

  const all = ALL.flatMap(c => JSON.parse(localStorage.getItem(STORAGE_PREFIX + c)));
  const payload = { retailer: 'walmart', scraped_at: new Date().toISOString(), products: all };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'walmart_products.json';
  document.body.appendChild(a); a.click();
  setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(a.href); }, 1000);
  console.log(`[Walmart] 🎉 Downloaded walmart_products.json (${all.length} total products).`);
  console.log('[Walmart] To reset for next refresh: ' + ALL.map(c => `localStorage.removeItem('${STORAGE_PREFIX + c}')`).join('; '));
})();


/* ---------------------------------------------------------------------------
 *  WAYFAIR  —  https://www.wayfair.com/rugs/sb0/area-rugs-c1849518.html  (etc.)
 *
 *  ⚠️  WAYFAIR HAS PERIMETERX BOT DETECTION. Tips:
 *   - Refresh Wayfair categories FIRST, before Amazon/Walmart, while IP is fresh.
 *   - Wait 5–10 min between Wayfair pages.
 *   - If you see "Access to this page has been denied" use a VPN or wait 30+ min.
 *   - If only 2-3 categories make it through, that's OK — the API endpoint
 *     falls back to whatever data is in app/data/wayfair_products.json,
 *     so partial refresh is fine. Re-paste the un-scraped categories' old
 *     entries from the existing wayfair_products.json before committing.
 *
 *  Paste the block below on each of the 4 Wayfair category pages.
 * ---------------------------------------------------------------------------
 */
(async () => {
  const STORAGE_PREFIX = 'wf_wayfair_';
  const ALL = ['area_rug', 'outdoor_rug', 'shag_rug', 'hallway_runner'];
  const TARGET_PER_CATEGORY = 30;

  const url = decodeURIComponent(window.location.href).toLowerCase();
  const CATEGORY =
    /outdoor/.test(url) ? 'outdoor_rug' :
    /shag/.test(url)    ? 'shag_rug' :
    /hallway|runner/.test(url) ? 'hallway_runner' :
    /area/.test(url)    ? 'area_rug' : null;

  if (!CATEGORY) {
    console.error('[Wayfair] Could not detect category from URL.');
    return;
  }
  console.log(`[Wayfair] Extracting ${CATEGORY}… (will scroll to trigger lazy loading)`);

  // Scroll to trigger lazy-loaded ListingCards
  const SCROLL_STEPS = 10;
  for (let i = 0; i < SCROLL_STEPS; i++) {
    window.scrollBy(0, 1500);
    await new Promise(r => setTimeout(r, 800));
  }
  window.scrollTo(0, 0);
  await new Promise(r => setTimeout(r, 600));

  const cards = document.querySelectorAll('[data-test-id="ListingCard"]');
  console.log(`[Wayfair] Found ${cards.length} listing cards.`);

  const products = [];
  cards.forEach(card => {
    const txt = card.innerText || '';
    const linkEl = card.querySelector('a[href*="/pdp/"]') || card.querySelector('a[href*=".html"]');
    const imgEl  = card.querySelector('img');
    const nameEl = card.querySelector('[data-test-id="CardLink"]') || linkEl;
    const name = nameEl ? nameEl.innerText.trim().split('\n')[0] : null;
    if (!name) return;
    let href = linkEl ? linkEl.getAttribute('href') : null;
    if (href && !href.startsWith('http')) href = `https://www.wayfair.com${href}`;
    if (href) href = href.split('?')[0];

    const priceM = txt.match(/\$([\d,]+\.\d{2})/) || txt.match(/\$([\d,]+)/);
    const ratingM = txt.match(/(\d(?:\.\d)?)\s*\(/) || txt.match(/(\d\.\d)\s*out of 5/);
    const reviewsM = txt.match(/\((\d[\d,]*)\)/);

    products.push({
      category: CATEGORY,
      url: href,
      name,
      price: priceM ? `$${priceM[1]}` : null,
      details: [],
      pattern: null,
      image_url: imgEl ? imgEl.src : null,
      rating: ratingM ? parseFloat(ratingM[1]) : null,
      review_count: reviewsM ? parseInt(reviewsM[1].replace(/,/g, ''), 10) : null,
    });
  });

  const seen = new Set();
  const unique = products.filter(p => {
    if (!p.url || seen.has(p.url)) return false;
    seen.add(p.url);
    return true;
  });
  const top = unique.slice(0, TARGET_PER_CATEGORY);

  if (top.length === 0) {
    console.error('[Wayfair] ❌ 0 products extracted. Possible PerimeterX block or selector change. Check page in browser.');
    return;
  }

  localStorage.setItem(STORAGE_PREFIX + CATEGORY, JSON.stringify(top));
  console.log(`[Wayfair] ✅ Saved ${top.length} products for ${CATEGORY}.`);

  const done = ALL.filter(c => localStorage.getItem(STORAGE_PREFIX + c));
  console.log(`[Wayfair] Progress: ${done.length}/4 categories → ${done.join(', ')}`);
  if (done.length < 4) {
    const left = ALL.filter(c => !done.includes(c));
    console.log(`[Wayfair] Still to do: ${left.join(', ')}`);
    console.log('[Wayfair] Wait 5-10 min before next category to avoid PerimeterX rate limit.');
    return;
  }

  const all = ALL.flatMap(c => JSON.parse(localStorage.getItem(STORAGE_PREFIX + c)));
  const payload = { retailer: 'wayfair', scraped_at: new Date().toISOString(), products: all };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'wayfair_products.json';
  document.body.appendChild(a); a.click();
  setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(a.href); }, 1000);
  console.log(`[Wayfair] 🎉 Downloaded wayfair_products.json (${all.length} total products).`);
  console.log('[Wayfair] To reset for next refresh: ' + ALL.map(c => `localStorage.removeItem('${STORAGE_PREFIX + c}')`).join('; '));
})();


/* ---------------------------------------------------------------------------
 *  PARTIAL DOWNLOAD (Wayfair fallback)
 *  If PerimeterX blocks you mid-refresh and you only got 2-3 categories,
 *  paste this on any Wayfair page to download what you have so you can
 *  merge it manually with the existing wayfair_products.json.
 * ---------------------------------------------------------------------------
 */
/*
(() => {
  const STORAGE_PREFIX = 'wf_wayfair_';
  const ALL = ['area_rug', 'outdoor_rug', 'shag_rug', 'hallway_runner'];
  const done = ALL.filter(c => localStorage.getItem(STORAGE_PREFIX + c));
  const all = done.flatMap(c => JSON.parse(localStorage.getItem(STORAGE_PREFIX + c)));
  const payload = { retailer: 'wayfair', scraped_at: new Date().toISOString(), products: all, partial_categories: done };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'wayfair_products_partial.json';
  document.body.appendChild(a); a.click();
  setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(a.href); }, 1000);
  console.log(`Downloaded ${all.length} products across ${done.length} categories: ${done.join(', ')}`);
})();
*/
