# Facebook Browser & Marketplace Listings

Browser automation via [HyperBrowser](https://hyperbrowser.ai) (Browser Use + Scrape API). Supports login flows and, with a saved profile, scraping Facebook Marketplace to extract listing data as JSON.

## Requirements

- Python 3.x
- Dependencies: `pip install -r requirements.txt`

## Setup

1. Create a `.env` file in the project root and set:

| Variable | Required | Description |
|----------|----------|-------------|
| `HYPERBROWSER_API_KEY` | Yes | API key from HyperBrowser |
| `TARGET_URL` | No | Login page URL (default: entreaseai.com) |
| `TARGET_URL1` | No | Page to scrape when using a profile (default: Facebook Marketplace vehicles) |
| `LOGIN_EMAIL` or `FACEBOOK_EMAIL` | When no profile | Login email |
| `LOGIN_PASSWORD` or `FACEBOOK_PASSWORD` | When no profile | Login password |
| `HYPERBROWSER_FACEBOOK_PROFILE_ID` or `PROFILE_ID` | No | Saved browser profile ID (skip login, run scrape) |
| `SCRAPE_OUTPUT_DIR` | No | Directory for output files (default: current directory) |

2. Ensure `.env` is in `.gitignore` and never committed.

## Usage

**Without a profile (first run or login flow):**

- Run task (non-blocking):  
  `python facebook_browser.py`
- Run and wait for result:  
  `python facebook_browser.py --wait`

After the task completes, the script prints a profile ID. Add it to `.env` as `HYPERBROWSER_FACEBOOK_PROFILE_ID` (or `PROFILE_ID`) to reuse the session.

**With a profile (scrape Marketplace → listings JSON):**

- With `PROFILE_ID` (or `HYPERBROWSER_FACEBOOK_PROFILE_ID`) set in `.env`:  
  `python facebook_browser.py` or `python facebook_browser.py --wait`

The script scrapes `TARGET_URL1` with the logged-in profile, saves the page as `scrape_YYYYMMDD_HHMMSS.html` (so you can inspect the structure), then extracts listings and writes `listings_YYYYMMDD_HHMMSS.json` in `SCRAPE_OUTPUT_DIR`. The JSON has the form:

```json
{
  "listings": [
    {
      "listing_url": "https://www.facebook.com/marketplace/item/...",
      "listing_id": "...",
      "name": "...",
      "location": "...",
      "price": "...",
      "seller_name": "...",
      "subtitle": "..."
    }
  ],
  "count": 0
}
```

## Project layout

- `facebook_browser.py` — Entrypoint: login/scrape orchestration and listing extraction from scraped HTML.
- `requirements.txt` — Python dependencies.
- `.env` — Local config and secrets (do not commit).
