## Proposal: Finding The Nearest MBTA Stop

Flask app: enter a place/address, get the closest MBTA stop on a map.

# Setup

```bash
pip install -r requirements.txt
export MAPBOX_TOKEN="pk.your_token_here"
export MBTA_API_KEY="your_mbta_key_here"
python app.py
```

Open http://localhost:5000.

# How it works

1. User submits a place name.
2. `/api/nearest?place=...` geocodes via Mapbox (biased to eastern MA).
3. Backend calls MBTA `/stops` with `filter[latitude]`, `filter[longitude]`,
   `filter[radius]`, `sort=distance`, `page[limit]=1`. MBTA returns the
   single closest stop by great-circle distance.
4. Frontend drops two markers and fits the map to both.

# Known limitations

- **Straight-line distance only.** A stop across the Charles River might
  appear closest but require a 2-mile detour on foot.
- **Search radius is ~3.5 miles.** Locations outside the MBTA service area
  return "no stop found" even if one exists 10+ miles away. Adjust
  `filter[radius]` in `nearest_stop()` if you want wider coverage — at the
  cost of more meaningless results for out-of-area queries.
- **Single stop returned.** Doesn't distinguish subway, bus, commuter rail,
  or ferry. The "nearest" stop to a downtown address is often a bus stop,
  not the subway station the user probably wanted. A real product would
  filter by `route_type` or show multiple results grouped by mode.
- **Geocoding failures are common** for ambiguous inputs ("Main St",
  "Harvard" — which Harvard?). The bbox biases toward eastern MA but
  doesn't eliminate ambiguity.
- **No caching.** Every query hits both APIs. Mapbox free tier is 100k
  geocodes/month; MBTA anon is 20 req/min, 1000 req/min with a key.
- **Token exposure.** The Mapbox token is embedded in the HTML for map
  tiles. Restrict it to your domain in the Mapbox dashboard. The MBTA key
  stays server-side.
- **No tests, no logging, no error tracking.** Classroom-grade.

## What could break in production

- Mapbox rate limits / billing surprises if the app goes viral.
- MBTA API outages (it goes down occasionally — no fallback here).
- Users pasting SQL, XSS, or 10KB of garbage into the input (length-capped
  to 200 chars, output is escaped, but input validation is minimal).
- Debug mode enabled in `app.run()` — remove before deploying anywhere.