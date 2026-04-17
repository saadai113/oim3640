# Project Proposal: Nearest MBTA Stop Lookup
 - A small Flask web application that accepts a place name or address in the Greater Boston area, geocodes it via the Mapbox Geocoding API, and returns the closest MBTA stop using the MBTA v3 API's distance-sorted stop endpoint. 
 - The frontend displays the origin and the nearest stop on a Mapbox-rendered map.

## 1. Objectives
 - The project should do the  following:
 - A user can submit a place name through a web form and receive the name, ID, and coordinates of the nearest MBTA stop.
 - 1. The origin and stop are plotted on a map.
 - 2. The system fails when an upstream API is unreachable.
 - 3. API keys are kept out of source control and loaded from environment variables.

## 2. Approach

The application is structured as a thin Flask service with two routes:

- `GET /` renders the map page and passes the public Mapbox token for tile rendering.
- `GET /api/nearest?place=<query>` geocodes the query, queries the MBTA stops endpoint with `sort=distance`, and returns a JSON payload containing the resolved origin and nearest stop.

Distance is computed two ways. The MBTA API does the actual sort using `filter[latitude]`, `filter[longitude]`, and `filter[radius]`. A separate haversine calculation is performed in Python to produce a human-readable miles value for display. Both are straight-line distances and will understate real walking distance.

To reduce ambiguous geocoding results, the Mapbox request is biased toward downtown Boston using the `proximity` parameter and constrained to an eastern-Massachusetts bounding box. This is a heuristic, not a guarantee.

## 3. Scope and Assumptions
 - Single-user local Flask app. Greater Boston only. Plain HTML/JS frontend. Synchronous request handling. Manual testing.
 - Assumptions that may not hold.**
The Mapbox proximity bias and bounding box correctly disambiguate most local queries. False matches are likely for generic street names.
- A 0.05-degree radius (roughly 3.5 miles at this latitude) is wide enough to find a stop for most queries inside the service area and narrow enough to keep response payloads small. Queries from the edges of the service area may return no results.
- Both upstream APIs remain available and backwards-compatible during the project window. The MBTA API has historically been stable but is not guaranteed.

## 4. Risks and Failure Modes

A realistic accounting of what can go wrong:

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Mapbox returns the wrong location for ambiguous queries (e.g., "Main Street") | High | Returns a nearest stop that has nothing to do with what the user meant | Display the resolved address back to the user so they can confirm; bias by proximity and bbox |
| User queries a location outside the MBTA service area | Medium | No stop returned | Return a clear error message; do not silently fall back |
| Upstream API outage or rate limiting | Medium | App appears broken | Short request timeouts (8s), explicit error responses; document the MBTA 20 req/min anonymous limit |
| API key leakage via committed `.env` or template exposure | Medium | Quota theft, possible billing exposure on Mapbox | `.env` in `.gitignore`; restrict the public Mapbox token to specific URLs in the dashboard |
| Straight-line distance misleads users | High | Suggested stop may be across a river, highway, or otherwise unwalkable | Document the limitation; out of scope to fix in this version |
| Scope creep into routing or scheduling | Medium | Project does not finish | Hold the line on the non-goals listed above |


## 4. Timeline

A realistic estimate, with buffer:

| Week | Work | Slip risk |
|---|---|---|
| 1 | Flask backend and API integration (largely done) | Low |
| 2 | Frontend map, error states, manual testing | Medium — Mapbox JS quirks |
| 3 | Documentation, testing, learning log | Low |
| 4 | Buffer for unforeseen issues | — |

## 5. Evaluation

Success will be measured by:

- All four objectives demonstrably met on a fresh clone.
- Manually tested queries covering: valid Boston addresses, ambiguous street names, out-of-area locations, empty input, malformed input, and a query during a simulated upstream failure.
- Documentation sufficient that another student could run the project without verbal instructions.

Failure modes that would not count as success: a working demo that only handles the queries shown during a presentation; a deployment that exposes API keys.