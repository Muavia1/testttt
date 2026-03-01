"""
Test script: open Marketplace in a HyperBrowser session, scroll, then extract
listing IDs/URLs from page HTML (links only — no JSON parsing, faster).

Requires: PROFILE_ID and HYPERBROWSER_API_KEY in .env, and playwright installed.

Usage:
  python marketplace_scroll_scrape.py
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

LISTING_BASE_URL = "https://www.facebook.com/marketplace/item/"
from hyperbrowser import Hyperbrowser
from hyperbrowser.models import CreateSessionParams, CreateSessionProfile

load_dotenv()

PROFILE_ID = (
    os.getenv("HYPERBROWSER_FACEBOOK_PROFILE_ID") or os.getenv("PROFILE_ID") or ""
).strip()
TARGET_URL1 = os.getenv(
    "TARGET_URL1",
    "https://www.facebook.com/marketplace/category/vehicles?sortBy=creation_time_descend&topLevelVehicleType=car_truck&exact=false",
).strip()
HYPERBROWSER_API_KEY = os.getenv("HYPERBROWSER_API_KEY", "").strip()
SCRAPE_OUTPUT_DIR = os.getenv("SCRAPE_OUTPUT_DIR", ".").strip()
SCROLL_COUNT = 2
SCROLL_WAIT_SEC = 2  # Give FB time to fetch and inject next batch before we capture HTML
PAGE_ZOOM = 0.2  # Zoom out so more listings fit in viewport per scroll


def extract_listing_ids_from_html_links(html: str) -> list[dict]:
    """Find /marketplace/item/<id>/ links in HTML. Returns minimal records (id + url only)."""
    # Match marketplace item URLs; ID is numeric
    pattern = re.compile(r"/marketplace/item/(\d+)/?")
    seen = set()
    out = []
    for match in pattern.finditer(html):
        lid = match.group(1)
        if lid not in seen:
            seen.add(lid)
            out.append({
                "listing_id": lid,
                "listing_url": f"{LISTING_BASE_URL}{lid}/",
            })
    return out


def main():
    if not HYPERBROWSER_API_KEY:
        print("Error: HYPERBROWSER_API_KEY is not set in .env")
        sys.exit(1)
    if not PROFILE_ID:
        print("Error: PROFILE_ID (or HYPERBROWSER_FACEBOOK_PROFILE_ID) is not set in .env")
        sys.exit(1)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Error: playwright is required. Run: pip install playwright && playwright install chromium")
        sys.exit(1)

    client = Hyperbrowser(api_key=HYPERBROWSER_API_KEY)
    session = client.sessions.create(
        params=CreateSessionParams(
            profile=CreateSessionProfile(id=PROFILE_ID, persist_changes=False),
        )
    )

    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(session.ws_endpoint)
            default_context = browser.contexts[0]
            page = default_context.pages[0]

            print(f"Navigating to {TARGET_URL1}...")
            # Use "domcontentloaded" or "load" — "networkidle" often never fires on Facebook
            page.goto(TARGET_URL1, wait_until="domcontentloaded", timeout=90_000)
            #page.wait_for_timeout(3000)  # Allow feed to start rendering before scrolling
            page.evaluate(f"document.documentElement.style.zoom = '{PAGE_ZOOM}'")
            page.wait_for_timeout(500)  # Let zoom apply before scrolling

            # Links-only extraction (no JSON parsing) — faster. Capture after each scroll and merge.
            seen_ids = set()
            listings = []
            for i in range(SCROLL_COUNT):
                print(f"Scroll {i + 1}/{SCROLL_COUNT}...")
                page.evaluate("window.scrollBy(0, window.innerHeight)")
                page.wait_for_timeout(SCROLL_WAIT_SEC * 1000)
                html = page.content()
                batch = extract_listing_ids_from_html_links(html)
                for rec in batch:
                    if rec["listing_id"] not in seen_ids:
                        seen_ids.add(rec["listing_id"])
                        listings.append(rec)
                if batch:
                    print(f"  -> {len(batch)} in page, {len(listings)} total")

            browser.close()
    finally:
        client.sessions.stop(session.id)
    out_dir = Path(SCRAPE_OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"listings_scroll_{ts}.json"
    out_path.write_text(
        json.dumps({"listings": listings, "count": len(listings)}, indent=2),
        encoding="utf-8",
    )
    print(f"Extracted {len(listings)} listings to {out_path}")


if __name__ == "__main__":
    main()
