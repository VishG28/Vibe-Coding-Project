import requests
import json
import time
from bs4 import BeautifulSoup

OUTPUT_FILE = "chipotle_locations.json"
BASE_URL = "https://locations.chipotle.com/sitemap.xml"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_state_urls():
    resp = requests.get(BASE_URL, headers=HEADERS)
    resp.raise_for_status()
    # Extract state URLs from the sitemap
    import xml.etree.ElementTree as ET
    root = ET.fromstring(resp.text)
    ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = [elem.text for elem in root.findall('.//ns:loc', ns)]
    # Filter for US state URLs (e.g., https://locations.chipotle.com/us/ca)
    state_urls = [u for u in urls if u.startswith("https://locations.chipotle.com/us/")]
    return state_urls

def get_location_urls(state_url):
    # Each state page has a sitemap.xml with city/location URLs
    sitemap_url = state_url.rstrip('/') + "/sitemap.xml"
    resp = requests.get(sitemap_url, headers=HEADERS)
    if resp.status_code != 200:
        return []
    import xml.etree.ElementTree as ET
    root = ET.fromstring(resp.text)
    ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = [elem.text for elem in root.findall('.//ns:loc', ns)]
    # Filter for store URLs
    store_urls = [u for u in urls if "/chipotle-" in u]
    return store_urls

def get_location_data(location_url):
    # Scrape the location page for address info
    resp = requests.get(location_url, headers=HEADERS)
    if resp.status_code != 200:
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    script = soup.find("script", type="application/ld+json")
    if not script:
        return None
    try:
        data = json.loads(script.string)
        # Only keep relevant fields
        return {
            "name": data.get("name"),
            "address": data.get("address", {}),
            "telephone": data.get("telephone"),
            "latitude": data.get("geo", {}).get("latitude"),
            "longitude": data.get("geo", {}).get("longitude"),
            "url": location_url
        }
    except Exception:
        return None

def main():
    all_locations = []
    state_urls = get_state_urls()
    print(f"Found {len(state_urls)} state URLs.")
    for state_url in state_urls:
        print(f"Processing {state_url} ...")
        location_urls = get_location_urls(state_url)
        print(f"  Found {len(location_urls)} locations.")
        for loc_url in location_urls:
            data = get_location_data(loc_url)
            if data:
                all_locations.append(data)
            time.sleep(0.2)  # Be polite to the server
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_locations, f, indent=2)
    print(f"Saved {len(all_locations)} locations to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()