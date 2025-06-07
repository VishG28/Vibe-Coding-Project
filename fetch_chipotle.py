# fetch_chipotle.py
#!/usr/bin/env python3
import requests
import json
import xml.etree.ElementTree as ET

# Constants
ROOT_SITEMAP = "https://locations.chipotle.com/sitemap.xml"
LINKS_FILE   = "all_sitemap_links.json"
HEADERS      = {"User-Agent": "Mozilla/5.0"}
NS_DECL      = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'

# Fetch all store URLs from the root sitemap and save to JSON
def main():
    # 1) Download the root sitemap XML
    resp = requests.get(ROOT_SITEMAP, headers=HEADERS)
    resp.raise_for_status()

    # 2) Strip XML namespace for simpler parsing
    xml = resp.text.replace(NS_DECL, '')
    root = ET.fromstring(xml)

    # 3) Extract every <loc> URL
    urls = [loc.text for loc in root.findall('.//loc')]

    # 4) Filter store pages: must be full store path (>=3 segments), exclude delivery pages
    store_links = [
        u for u in urls
        if u.startswith("https://locations.chipotle.com/")
        and u.count("/") >= 5  # protocol://domain + 3 segments = 5 slashes
        and 'order-delivery' not in u
    ]

    # 5) Dedupe, sort, and save
    store_links = sorted(set(store_links))
    with open(LINKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(store_links, f, indent=2)

    print(f"Saved {len(store_links)} store links to {LINKS_FILE}")

if __name__ == '__main__':
    main()