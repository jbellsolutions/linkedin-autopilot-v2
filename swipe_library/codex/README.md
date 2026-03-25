# Codex Web Swipe Archive

This folder contains a public-web archive for each copywriter in scope.

Total archived public pages: `481`

Per-copywriter folders contain:

- `manifest.json`: URL-level index with title, description, word count, and file paths
- `README.md`: human-readable page summary
- `raw_html/`: raw HTML snapshots
- `text/`: cleaned text extracted from each page

Current archive counts:

- `alex_hormozi`: 60 pages
- `bill_mueller`: 0 pages archived automatically
- `brian_kurtz`: 80 pages
- `jay_abraham`: 100 pages
- `jon_buchan`: 120 pages
- `lead_gen_jay`: 0 pages archived automatically
- `liam_ottley`: 7 pages
- `todd_brown`: 40 pages
- `tom_bilyeu`: 74 pages

Blocked or partial cases:

- `bill_mueller`: direct requests to `storysalesmachine.com` are blocked by a Cloudflare challenge from this environment. See `ACCESS_NOTES.md`.
- `lead_gen_jay`: direct requests to the detected official domains are blocked by network/SSL interception from this environment. See `ACCESS_NOTES.md`.
- `liam_ottley`: the accessible public footprint is much smaller than the others; this archive includes `liamottley.com` plus reachable `morningside.ai` pages.

Scraper assets:

- `configs/`: per-copywriter scrape configs
- `scripts/public_site_scraper.py`: reusable public-site archiver
