"""
Extract Facebook Marketplace listing details from a scraped HTML file.

Reads HTML that contains embedded JSON (script type="application/json") with
marketplace_search.feed_units.edges, and outputs a JSON file with initial
listing details: listing_url, name, location, price, seller_name, subtitle.

Usage:
  python extract_listings.py scrape_20260226_235329_html.html
  python extract_listings.py scrape_20260226_235329_html.html -o listings.json
"""

import argparse
import json
import re
import sys
from pathlib import Path


LISTING_BASE_URL = "https://www.facebook.com/marketplace/item/"


def _find_marketplace_feed_units(obj):
    """Recursively find the feed_units.edges array in parsed JSON."""
    if isinstance(obj, dict):
        if "marketplace_search" in obj:
            ms = obj["marketplace_search"]
            if isinstance(ms, dict) and "feed_units" in ms:
                fu = ms["feed_units"]
                if isinstance(fu, dict) and "edges" in fu:
                    return fu["edges"]
        for v in obj.values():
            found = _find_marketplace_feed_units(v)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = _find_marketplace_feed_units(item)
            if found is not None:
                return found
    return None


def _listing_from_node(node):
    """Build a flat listing dict from a feed edge node (node.listing)."""
    listing = node.get("listing") if isinstance(node, dict) else None
    if not listing or not isinstance(listing, dict):
        return None

    listing_id = listing.get("id")
    if not listing_id:
        return None

    # Location: city_page.display_name or city + state
    location = ""
    loc = listing.get("location") or {}
    if isinstance(loc, dict):
        rg = loc.get("reverse_geocode") or {}
        if isinstance(rg, dict):
            city_page = rg.get("city_page") or {}
            if isinstance(city_page, dict) and city_page.get("display_name"):
                location = city_page["display_name"]
            else:
                city = rg.get("city") or ""
                state = rg.get("state") or ""
                location = f"{city}, {state}".strip(", ") if city or state else ""

    # Price
    price_obj = listing.get("listing_price") or {}
    price = price_obj.get("formatted_amount", "") if isinstance(price_obj, dict) else ""

    # Seller
    seller_obj = listing.get("marketplace_listing_seller") or {}
    seller_name = seller_obj.get("name", "") if isinstance(seller_obj, dict) else ""

    # Subtitle (e.g. mileage)
    subtitle = ""
    sub_titles = listing.get("custom_sub_titles_with_rendering_flags") or []
    if isinstance(sub_titles, list) and sub_titles and isinstance(sub_titles[0], dict):
        subtitle = sub_titles[0].get("subtitle") or ""

    return {
        "listing_url": f"{LISTING_BASE_URL}{listing_id}/",
        "listing_id": listing_id,
        "name": listing.get("marketplace_listing_title") or listing.get("custom_title") or "",
        "location": location,
        "price": price,
        "seller_name": seller_name,
        "subtitle": subtitle,
    }


def extract_listings_from_html(html_path: Path) -> list[dict]:
    """Parse HTML file, find embedded marketplace JSON, return list of listing dicts."""
    text = html_path.read_text(encoding="utf-8", errors="replace")

    # Find all script type="application/json" contents
    script_pattern = re.compile(
        r'<script\s+type=["\']application/json["\'][^>]*>(.*?)</script>',
        re.DOTALL | re.IGNORECASE,
    )
    listings = []
    seen_ids = set()

    for match in script_pattern.finditer(text):
        blob = match.group(1).strip()
        if "marketplace_search" not in blob or "feed_units" not in blob:
            continue
        try:
            data = json.loads(blob)
        except json.JSONDecodeError:
            continue

        edges = _find_marketplace_feed_units(data)
        if not edges or not isinstance(edges, list):
            continue

        for edge in edges:
            if not isinstance(edge, dict):
                continue
            node = edge.get("node")
            if not node:
                continue
            record = _listing_from_node(node)
            if record and record["listing_id"] not in seen_ids:
                seen_ids.add(record["listing_id"])
                listings.append(record)

    return listings


def main():
    parser = argparse.ArgumentParser(
        description="Extract Facebook Marketplace listing details from scraped HTML into JSON."
    )
    parser.add_argument(
        "html_file",
        type=Path,
        help="Path to the scraped HTML file (e.g. scrape_*.html)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output JSON file path (default: <html_file_stem>_listings.json)",
    )
    args = parser.parse_args()

    if not args.html_file.is_file():
        print(f"Error: File not found: {args.html_file}", file=sys.stderr)
        sys.exit(1)

    listings = extract_listings_from_html(args.html_file)
    out_path = args.output or args.html_file.with_name(
        args.html_file.stem + "_listings.json"
    )

    out_path.write_text(
        json.dumps({"listings": listings, "count": len(listings)}, indent=2),
        encoding="utf-8",
    )
    print(f"Extracted {len(listings)} listings to {out_path}")


if __name__ == "__main__":
    main()
