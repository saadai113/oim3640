"""
Flask app: find the nearest MBTA stop to a user-provided place/address.

Realism notes:
- "Nearest" = straight-line (haversine) distance. Actual walking distance
  will usually be longer due to rivers, highways, one-way streets, etc.
- API keys are read from environment variables. Do not commit them.
- No caching, no rate limiting, no retries. Fine for local/classroom use;
  not fine for production.
"""

import os
import math
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

MAPBOX_TOKEN = os.environ.get("MAPBOX_TOKEN", "")
MBTA_API_KEY = os.environ.get("MBTA_API_KEY", "")

MAPBOX_GEOCODE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json"
MBTA_STOPS_URL = "https://api-v3.mbta.com/stops"

# Request timeout in seconds. Short enough to fail fast on a dead network,
# long enough to tolerate a slow upstream.
HTTP_TIMEOUT = 8


def geocode(place: str):
    """Resolve a place string to (lat, lon, display_name).

    Returns None on any failure (network error, no results, bad response).
    Callers must handle None.
    """
    if not MAPBOX_TOKEN:
        return None
    if not place or not place.strip():
        return None

    # Bias results toward Greater Boston so "Main St" doesn't resolve to Kansas.
    # proximity = roughly downtown Boston. bbox limits to eastern MA.
    params = {
        "access_token": MAPBOX_TOKEN,
        "limit": 1,
        "proximity": "-71.0589,42.3601",
        "bbox": "-71.9,41.9,-70.5,43.0",
        "country": "US",
    }
    try:
        resp = requests.get(
            MAPBOX_GEOCODE_URL.format(query=requests.utils.quote(place.strip())),
            params=params,
            timeout=HTTP_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return None

    features = data.get("features") or []
    if not features:
        return None

    feat = features[0]
    lon, lat = feat.get("center", [None, None])
    if lat is None or lon is None:
        return None
    return {
        "lat": lat,
        "lon": lon,
        "display_name": feat.get("place_name", place),
    }


def haversine_miles(lat1, lon1, lat2, lon2):
    """Great-circle distance in miles. Used as a fallback / display value."""
    r = 3958.8  # Earth radius in miles
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlam / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def nearest_stop(lat: float, lon: float):
    """Return the closest MBTA stop to (lat, lon), or None on failure.

    Uses the MBTA API's built-in sort-by-distance. The API returns stops
    ordered by distance from the given lat/lon when sort=distance is set.
    """
    headers = {}
    if MBTA_API_KEY:
        headers["x-api-key"] = MBTA_API_KEY

    params = {
        "filter[latitude]": lat,
        "filter[longitude]": lon,
        # radius is in degrees (~0.02 deg ≈ 1.4 mi at this latitude).
        # Large enough to find something in most of the service area,
        # small enough to avoid pulling the whole network.
        "filter[radius]": 0.05,
        "sort": "distance",
        "page[limit]": 1,
    }
    try:
        resp = requests.get(
            MBTA_STOPS_URL, params=params, headers=headers, timeout=HTTP_TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return None

    stops = data.get("data") or []
    if not stops:
        return None

    s = stops[0]
    attrs = s.get("attributes", {})
    slat = attrs.get("latitude")
    slon = attrs.get("longitude")
    if slat is None or slon is None:
        return None

    return {
        "id": s.get("id"),
        "name": attrs.get("name", "Unknown stop"),
        "description": attrs.get("description") or "",
        "lat": slat,
        "lon": slon,
        "wheelchair_boarding": attrs.get("wheelchair_boarding", 0),
        "distance_mi": round(haversine_miles(lat, lon, slat, slon), 2),
    }


@app.route("/")
def index():
    # Pass the Mapbox token to the template ONLY for the public map tiles.
    # Restrict this token's scope (URL allowlist) in the Mapbox dashboard.
    return render_template("index.html", mapbox_token=MAPBOX_TOKEN)


@app.route("/api/nearest")
def api_nearest():
    place = request.args.get("place", "").strip()
    if not place:
        return jsonify({"error": "Missing 'place' query parameter."}), 400
    if len(place) > 200:
        return jsonify({"error": "Query too long."}), 400

    geo = geocode(place)
    if not geo:
        return jsonify({"error": f"Could not geocode '{place}'."}), 404

    stop = nearest_stop(geo["lat"], geo["lon"])
    if not stop:
        return jsonify(
            {
                "error": "No MBTA stop found nearby. The location may be outside "
                "the MBTA service area.",
                "origin": geo,
            }
        ), 404

    return jsonify({"origin": geo, "stop": stop})


if __name__ == "__main__":
    # Debug mode is for local development only. Never enable in production.
    if not MAPBOX_TOKEN:
        print("WARNING: MAPBOX_TOKEN not set. Geocoding and map tiles will fail.")
    if not MBTA_API_KEY:
        print("WARNING: MBTA_API_KEY not set. You'll hit the 20 req/min anon limit.")
    app.run(debug=True, port=5000)