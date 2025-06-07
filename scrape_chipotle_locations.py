#!/usr/bin/env python3
# geocode_chipotle.py
# Reads all_sitemap_links.json, extracts address components from each URL,
# geocodes via OpenStreetMap Nominatim HTTP API, and writes the results to geocoded_chipotle_locations.json

import requests
import json
import time
from urllib.parse import urlparse

# Configuration
LINKS_FILE = "all_sitemap_links.json"           # Input: list of store URLs
OUTPUT_FILE = "geocoded_chipotle_locations.json"  # Output: structured store data
USER_AGENT = "chipotle_geocoder/1.0"

# Parse the URL path into state, city, and street components
# e.g. '/al/decatur/1109-beltline-rd-se' -> ('AL', 'Decatur', '1109 Beltline Rd Se')
def parse_url(url):
    path = urlparse(url).path.strip('/')
    parts = path.split('/')
    if len(parts) < 3:
        return None
    state = parts[0].upper()
    city = parts[1].replace('-', ' ').title()
    street = parts[2].replace('-', ' ').title()
    return state, city, street

# Geocode an address string using Nominatim
# Returns (latitude, longitude) or (None, None)
def geocode_address(address):
    endpoint = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json',
        'limit': 1
    }
    headers = {'User-Agent': USER_AGENT}
    resp = requests.get(endpoint, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    results = resp.json()
    if not results:
        return None, None
    lat = float(results[0]['lat'])
    lon = float(results[0]['lon'])
    return lat, lon

# Main script
if __name__ == '__main__':
    # Load all store URLs
    with open(LINKS_FILE, 'r', encoding='utf-8') as f:
        urls = json.load(f)

    results = []
    for idx, url in enumerate(urls, 1):
        parsed = parse_url(url)
        if not parsed:
            print(f"Skipping malformed URL: {url}")
            continue
        state, city, street = parsed
        full_address = f"{street}, {city}, {state}, USA"

        try:
            lat, lon = geocode_address(full_address)
        except Exception as e:
            print(f"Geocode error for '{full_address}': {e}")
            lat = lon = None

        record = {
            "name": "Chipotle Mexican Grill",
            "address": street,
            "city": city,
            "state": state,
            "zip": "",
            "latitude": lat,
            "longitude": lon,
            "full_address": full_address
        }
        results.append(record)
        print(f"[{idx}/{len(urls)}] {full_address} -> ({lat}, {lon})")
        time.sleep(1)  # respect Nominatim rate limit

    # Write output to a new file to avoid clobbering old data
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"Saved {len(results)} geocoded records to '{OUTPUT_FILE}'")
    # Show first few entries for verification
    for rec in results[:5]:
        print(rec)