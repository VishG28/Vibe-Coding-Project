# scrape_chipotle_locations.py
#!/usr/bin/env python3
import requests
import json
import time
from bs4 import BeautifulSoup

# Constants
LINKS_FILE  = "all_sitemap_links.json"  # Input: list of store URLs
OUTPUT_FILE = "chipotle_locations.json"  # Output: store details
HEADERS     = {"User-Agent": "Mozilla/5.0"}

# Extract the JSON-LD block for the store (Restaurant or LocalBusiness)
def extract_store_data(soup):
    for script in soup.select('script[type="application/ld+json"]'):
        text = script.get_text(strip=True)
        if not text:
            continue
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            continue

        # If it's a list, search entries
        candidates = []
        if isinstance(obj, dict):
            if '@graph' in obj and isinstance(obj['@graph'], list):
                candidates = obj['@graph']
            else:
                candidates = [obj]
        elif isinstance(obj, list):
            candidates = obj

        # Look for the correct type
        for entry in candidates:
            t = entry.get('@type') or entry.get('type')
            if t in ('Restaurant', 'LocalBusiness'):
                return entry
    return None

# Scrape a single store URL for its details
def scrape_store(url):
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    data = extract_store_data(soup)
    if not data:
        raise ValueError('No JSON-LD restaurant data found')

    addr = data.get('address', {}) or {}
    geo  = data.get('geo', {}) or {}

    return {
        "name":      data.get('name', ''),
        "address":   addr.get('streetAddress', ''),
        "city":      addr.get('addressLocality', ''),
        "state":     addr.get('addressRegion', ''),
        "zip":       addr.get('postalCode', ''),
        "latitude":  geo.get('latitude'),
        "longitude": geo.get('longitude')
    }

# Main execution: load URLs, scrape each, and save
if __name__ == '__main__':
    # Load list of store URLs
    with open(LINKS_FILE, 'r', encoding='utf-8') as f:
        urls = json.load(f)

    locations = []
    for idx, url in enumerate(urls, 1):
        try:
            loc = scrape_store(url)
            locations.append(loc)
            print(f"[{idx}/{len(urls)}] Scraped: {url}")
        except Exception as e:
            print(f"Error ({idx}) {url}: {e}")
        time.sleep(0.2)  # polite delay

    # Write output JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(locations, f, indent=2)
    print(f"Saved {len(locations)} locations to {OUTPUT_FILE}")