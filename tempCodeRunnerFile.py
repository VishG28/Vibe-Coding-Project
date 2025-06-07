#!/usr/bin/env python3
import requests
import json
import xml.etree.ElementTree as ET

# Constants\ nBASE_SITEMAP = "https://locations.chipotle.com/sitemap.xml"
HEADERS = {"User-Agent": "Mozilla/5.0"}
OUTPUT_FILE = "all_sitemap_links.json"

# Fetch and save all store page URLs

def main():
    # 1) Download the root sitemap
    resp = requests.get(BASE_SITEMAP, headers=HEADERS)
    resp.raise_for_status()

    # 2) Remove the XML namespace so <loc> is easy to find
    xml = resp.text.replace(
        'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"', ''
    )

    # 3) Parse XML and extract every <loc>
    root = ET.fromstring(xml)
    all_urls = [elem.text for elem in root.findall('.//loc')]

    # 4) Filter for actual store pages:
    #    - must have at least 3 path segments after the domain
    #    - exclude any & order-delivery pages
    store_urls = [
        u for u in all_urls
        if u.count('/') >= 5 and 'order-delivery' not in u
    ]

    # 5) Write the store URLs to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(store_urls, f, indent=2)

    print(f"Saved {len(store_urls)} store links to {OUTPUT_FILE}")

if __name__ == '__main__':
    main()