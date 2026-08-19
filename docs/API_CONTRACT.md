Yes. I will explain this very simply.

## What “freeze API contract” means

An **API contract** is an agreement between frontend and backend:

> This endpoint will receive this JSON, and return this exact JSON shape.

“Freeze” means:

> All three teammates agree that the field names and JSON structure will not change without discussion.

Example:

If backend returns:

```json
{
  "route_type": "safe",
  "distance_m": 1000,
  "duration_min": 10
}
```

frontend will expect exactly:

```js
route_type
distance_m
duration_min
```

Backend should not suddenly change it to:

```json
{
  "type": "safe",
  "distance": 1000,
  "time": 10
}
```

That would break frontend.

---

# 1. How to freeze API contracts

Create this file:

```text
docs/API_CONTRACT.md
```

Commit it to Git before anyone starts serious coding.

Inside it, write:

1. Endpoint URL
2. Method
3. Request body
4. Success response
5. Error response
6. Owner

For your benchmark layer, freeze these endpoints:

```text
GET  /api/health
POST /api/auth/login
GET  /api/meta/area
GET  /api/scenarios
GET  /api/pois
GET  /api/pois/{id}
GET  /api/map/geojson
POST /api/routes
POST /api/routes/re-route
POST /api/reports/blocked
POST /api/reports/{id}/verify
GET  /api/reports/active
```

---

# 2. Simple API contract you can copy

You can copy this into `docs/API_CONTRACT.md`.

```md
# API Contract v1.0

All requests and responses use JSON.

All errors must use this shape:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```

## Frozen Endpoints

| Endpoint | Method | Owner |
|---|---|---|
| /api/health | GET | Backend Core |
| /api/auth/login | POST | Backend Core |
| /api/meta/area | GET | Backend Core |
| /api/scenarios | GET | Backend Core |
| /api/pois | GET | Backend Core |
| /api/pois/{id} | GET | Backend Core |
| /api/map/geojson | GET | Backend Core |
| /api/routes | POST | AI Routing |
| /api/routes/re-route | POST | AI Routing |
| /api/reports/blocked | POST | Backend Core |
| /api/reports/{id}/verify | POST | Backend Core |
| /api/reports/active | GET | Backend Core |
```

---

# 3. What mock data means

Mock data is fake JSON data that looks like real API responses.

It is used for two things:

1. **Frontend development**
   - Frontend can build UI before backend is ready.

2. **Backend demo fallback**
   - Backend can seed placeholder data if real data is not ready.

Mock data is not final official data. It is only for shape and demo.

---

# 4. Mock files you should create

Create this folder:

```text
frontend/src/mocks/
```

Inside it, create these files:

```text
frontend/src/mocks/health.json
frontend/src/mocks/meta.json
frontend/src/mocks/scenarios.json
frontend/src/mocks/pois.json
frontend/src/mocks/mapGeoJSON.json
frontend/src/mocks/routeResponse.json
frontend/src/mocks/activeReports.json
frontend/src/mocks/login.json
frontend/src/mocks/blockedReportResponse.json
```

Also create backend/demo mock data:

```text
data/mock/roads.geojson
data/velachery/pois.json
data/velachery/scenarios.json
```

---

# 5. Exact mock data to give

Copy these into the files.

---

## 5.1 `frontend/src/mocks/health.json`

```json
{
  "status": "ok",
  "model_loaded": true,
  "active_scenario_id": 3,
  "road_count": 5,
  "poi_count": 4
}
```

---

## 5.2 `frontend/src/mocks/meta.json`

```json
{
  "name": "West Velachery, Chennai",
  "bbox": [12.965, 80.195, 12.995, 80.235],
  "default_center": [12.980, 80.2125],
  "default_zoom": 15,
  "disclaimer": "Demo decision-support tool. Not an official emergency service."
}
```

---

## 5.3 `frontend/src/mocks/scenarios.json`

```json
[
  {
    "id": 1,
    "name": "Normal",
    "description": "Baseline light rainfall",
    "rainfall_mm_24h": 10,
    "rainfall_mm_1h": 0,
    "source": "manual",
    "is_active": false
  },
  {
    "id": 2,
    "name": "Heavy Monsoon",
    "description": "Heavy rainfall for several hours",
    "rainfall_mm_24h": 80,
    "rainfall_mm_1h": 15,
    "source": "manual",
    "is_active": false
  },
  {
    "id": 3,
    "name": "Michaung Replay",
    "description": "Approximately 150 mm rainfall in 24 hours",
    "rainfall_mm_24h": 150,
    "rainfall_mm_1h": 30,
    "source": "Michaung 2023 benchmark",
    "is_active": true
  },
  {
    "id": 4,
    "name": "Extreme Event",
    "description": "250 mm rainfall in 24 hours",
    "rainfall_mm_24h": 250,
    "rainfall_mm_1h": 50,
    "source": "manual",
    "is_active": false
  }
]
```

---

## 5.4 `frontend/src/mocks/pois.json`

These are placeholder important places.

```json
[
  {
    "id": 1,
    "external_id": "POI-HOSP-001",
    "name": "Velachery Hospital (Placeholder)",
    "category": "hospital",
    "lat": 12.9820,
    "lon": 80.2150,
    "address": "Hospital Road",
    "phone": "",
    "status": "open",
    "nearest_node_id": 104,
    "source": "placeholder",
    "notes": "Replace with real hospital data"
  },
  {
    "id": 2,
    "external_id": "POI-SHEL-001",
    "name": "Community Shelter (Placeholder)",
    "category": "shelter",
    "lat": 12.9810,
    "lon": 80.2110,
    "address": "Near Main Road",
    "phone": "",
    "status": "open",
    "nearest_node_id": 101,
    "source": "placeholder",
    "notes": "Replace with GCC relief centre data"
  },
  {
    "id": 3,
    "external_id": "POI-POL-001",
    "name": "Police Station (Placeholder)",
    "category": "police_station",
    "lat": 12.9790,
    "lon": 80.2140,
    "address": "Link Road",
    "phone": "",
    "status": "open",
    "nearest_node_id": 103,
    "source": "placeholder",
    "notes": "Replace with real police station data"
  },
  {
    "id": 4,
    "external_id": "POI-FUEL-001",
    "name": "Petrol Bunk (Placeholder)",
    "category": "petrol_bunk",
    "lat": 12.9795,
    "lon": 80.2120,
    "address": "Inner Road",
    "phone": "",
    "status": "open",
    "nearest_node_id": 102,
    "source": "placeholder",
    "notes": "Replace with real fuel station data"
  }
]
```

---

## 5.5 `frontend/src/mocks/mapGeoJSON.json`

This is the most important mock file for the map.

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [80.2100, 12.9800],
          [80.2150, 12.9800]
        ]
      },
      "properties": {
        "layer_type": "road",
        "segment_id": 1,
        "name": "Velachery Main Road",
        "road_type": "secondary",
        "current_risk_score": 0.12,
        "current_risk_level": "low",
        "predicted_time_to_high_risk_min": 120,
        "blocked": false,
        "flood_status": "safe"
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [80.2100, 12.9780],
          [80.2130, 12.9780]
        ]
      },
      "properties": {
        "layer_type": "road",
        "segment_id": 2,
        "name": "AGS Colony Road",
        "road_type": "residential",
        "current_risk_score": 0.82,
        "current_risk_level": "critical",
        "predicted_time_to_high_risk_min": 0,
        "blocked": true,
        "flood_status": "confirmed_flooded"
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [80.2130, 12.9780],
          [80.2130, 12.9800]
        ]
      },
      "properties": {
        "layer_type": "road",
        "segment_id": 3,
        "name": "Baby Nagar Link",
        "road_type": "residential",
        "current_risk_score": 0.52,
        "current_risk_level": "high",
        "predicted_time_to_high_risk_min": 25,
        "blocked": false,
        "flood_status": "likely_flooded"
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [80.2150, 12.9800],
          [80.2150, 12.9820]
        ]
      },
      "properties": {
        "layer_type": "road",
        "segment_id": 4,
        "name": "Hospital Road",
        "road_type": "residential",
        "current_risk_score": 0.10,
        "current_risk_level": "low",
        "predicted_time_to_high_risk_min": 160,
        "blocked": false,
        "flood_status": "safe"
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [80.2100, 12.9800],
          [80.2130, 12.9780]
        ]
      },
      "properties": {
        "layer_type": "road",
        "segment_id": 5,
        "name": "Low-Lying Shortcut",
        "road_type": "residential",
        "current_risk_score": 0.68,
        "current_risk_level": "high",
        "predicted_time_to_high_risk_min": 18,
        "blocked": false,
        "flood_status": "likely_flooded"
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [80.2150, 12.9820]
      },
      "properties": {
        "layer_type": "poi",
        "poi_id": 1,
        "name": "Velachery Hospital (Placeholder)",
        "category": "hospital",
        "status": "open"
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [80.2110, 12.9810]
      },
      "properties": {
        "layer_type": "poi",
        "poi_id": 2,
        "name": "Community Shelter (Placeholder)",
        "category": "shelter",
        "status": "open"
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [80.2140, 12.9790]
      },
      "properties": {
        "layer_type": "poi",
        "poi_id": 3,
        "name": "Police Station (Placeholder)",
        "category": "police_station",
        "status": "open"
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [80.2120, 12.9795]
      },
      "properties": {
        "layer_type": "poi",
        "poi_id": 4,
        "name": "Petrol Bunk (Placeholder)",
        "category": "petrol_bunk",
        "status": "open"
      }
    }
  ]
}
```

---

## 5.6 `frontend/src/mocks/routeResponse.json`

This is the route API response.

```json
{
  "request_id": 1,
  "destination": {
    "type": "poi",
    "poi_id": 1,
    "name": "Velachery Hospital (Placeholder)",
    "category": "hospital"
  },
  "routes": [
    {
      "route_type": "safe",
      "distance_m": 780,
      "duration_min": 6.2,
      "cost_score": 7.1,
      "avg_risk_score": 0.14,
      "high_risk_segments_count": 0,
      "blocked_segments_encountered": 0,
      "predicted_risk_warnings_count": 0,
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [80.2100, 12.9800],
          [80.2150, 12.9800],
          [80.2150, 12.9820]
        ]
      }
    },
    {
      "route_type": "short",
      "distance_m": 620,
      "duration_min": 4.8,
      "cost_score": 4.8,
      "avg_risk_score": 0.66,
      "high_risk_segments_count": 2,
      "blocked_segments_encountered": 0,
      "predicted_risk_warnings_count": 1,
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [80.2100, 12.9800],
          [80.2130, 12.9780],
          [80.2130, 12.9800],
          [80.2150, 12.9800],
          [80.2150, 12.9820]
        ]
      }
    }
  ],
  "warnings": [
    {
      "warning_type": "predicted_flood_before_arrival",
      "segment_id": 5,
      "road_name": "Low-Lying Shortcut",
      "eta_to_segment_min": 25,
      "predicted_time_to_high_risk_min": 18,
      "message": "This road may become high-risk before you reach it."
    }
  ],
  "explanation": {
    "safe_route_adds_min": 1.4,
    "high_risk_segments_avoided": 2,
    "blocked_segments_avoided": 0,
    "summary": "Safe route avoids low-lying shortcut roads and reaches the hospital with lower flood exposure."
  }
}
```

---

## 5.7 `frontend/src/mocks/activeReports.json`

```json
[
  {
    "id": 1,
    "segment_id": 2,
    "road_name": "AGS Colony Road",
    "source": "field_official",
    "verification_status": "confirmed",
    "note": "Waterlogging reported near AGS Colony entrance",
    "created_at": "2026-08-19T09:12:00Z"
  }
]
```

---

## 5.8 `frontend/src/mocks/login.json`

```json
{
  "access_token": "mock-token",
  "token_type": "Bearer",
  "expires_in": 43200,
  "user": {
    "id": 2,
    "username": "reporter",
    "role": "reporter"
  }
}
```

---

## 5.9 `frontend/src/mocks/blockedReportResponse.json`

```json
{
  "report_id": 1,
  "segment_id": 2,
  "verification_status": "confirmed",
  "credibility_score": 0.9,
  "road_status": {
    "blocked": true,
    "flood_status": "confirmed_flooded",
    "current_risk_level": "critical"
  }
}
```

---

# 6. Backend mock/seed data

Now create backend seed data.

Create:

```text
data/velachery/scenarios.json
```

Copy the same scenario JSON:

```json
[
  {
    "name": "Normal",
    "description": "Baseline light rainfall",
    "rainfall_mm_24h": 10,
    "rainfall_mm_1h": 0,
    "source": "manual",
    "is_active": true
  },
  {
    "name": "Heavy Monsoon",
    "description": "Heavy rainfall for several hours",
    "rainfall_mm_24h": 80,
    "rainfall_mm_1h": 15,
    "source": "manual",
    "is_active": false
  },
  {
    "name": "Michaung Replay",
    "description": "Approximately 150 mm rainfall in 24 hours",
    "rainfall_mm_24h": 150,
    "rainfall_mm_1h": 30,
    "source": "Michaung 2023 benchmark",
    "is_active": false
  },
  {
    "name": "Extreme Event",
    "description": "250 mm rainfall in 24 hours",
    "rainfall_mm_24h": 250,
    "rainfall_mm_1h": 50,
    "source": "manual",
    "is_active": false
  }
]
```

Create:

```text
data/velachery/pois.json
```

Copy the same POI JSON, but you can remove `nearest_node_id` if backend will calculate it.

```json
[
  {
    "external_id": "POI-HOSP-001",
    "name": "Velachery Hospital (Placeholder)",
    "category": "hospital",
    "lat": 12.9820,
    "lon": 80.2150,
    "address": "Hospital Road",
    "phone": "",
    "status": "open",
    "source": "placeholder",
    "notes": "Replace with real hospital data"
  },
  {
    "external_id": "POI-SHEL-001",
    "name": "Community Shelter (Placeholder)",
    "category": "shelter",
    "lat": 12.9810,
    "lon": 80.2110,
    "address": "Near Main Road",
    "phone": "",
    "status": "open",
    "source": "placeholder",
    "notes": "Replace with GCC relief centre data"
  },
  {
    "external_id": "POI-POL-001",
    "name": "Police Station (Placeholder)",
    "category": "police_station",
    "lat": 12.9790,
    "lon": 80.2140,
    "address": "Link Road",
    "phone": "",
    "status": "open",
    "source": "placeholder",
    "notes": "Replace with real police station data"
  },
  {
    "external_id": "POI-FUEL-001",
    "name": "Petrol Bunk (Placeholder)",
    "category": "petrol_bunk",
    "lat": 12.9795,
    "lon": 80.2120,
    "address": "Inner Road",
    "phone": "",
    "status": "open",
    "source": "placeholder",
    "notes": "Replace with real fuel station data"
  }
]
```

Create:

```text
data/mock/roads.geojson
```

This is a tiny fake road network.

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "osm_id": "mock-1",
        "name": "Velachery Main Road",
        "highway": "secondary",
        "hazard_category": "low"
      },
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [80.2100, 12.9800],
          [80.2150, 12.9800]
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "osm_id": "mock-2",
        "name": "AGS Colony Road",
        "highway": "residential",
        "hazard_category": "very_high"
      },
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [80.2100, 12.9780],
          [80.2130, 12.9780]
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "osm_id": "mock-3",
        "name": "Baby Nagar Link",
        "highway": "residential",
        "hazard_category": "high"
      },
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [80.2130, 12.9780],
          [80.2130, 12.9800]
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "osm_id": "mock-4",
        "name": "Hospital Road",
        "highway": "residential",
        "hazard_category": "low"
      },
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [80.2150, 12.9800],
          [80.2150, 12.9820]
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "osm_id": "mock-5",
        "name": "Low-Lying Shortcut",
        "highway": "residential",
        "hazard_category": "high"
      },
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [80.2100, 12.9800],
          [80.2130, 12.9780]
        ]
      }
    }
  ]
}
```

---

# 7. How frontend should use mock data

Create this file:

```text
frontend/.env
```

Add:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCKS=true
```

When `VITE_USE_MOCKS=true`, frontend should use mock JSON.

Later, when backend is ready, change it to:

```env
VITE_USE_MOCKS=false
```

Example API client:

```ts
import mockPois from "../mocks/pois.json";
import mockScenarios from "../mocks/scenarios.json";
import mockMapGeoJSON from "../mocks/mapGeoJSON.json";
import mockRouteResponse from "../mocks/routeResponse.json";

const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === "true";
const API_BASE = import.meta.env.VITE_API_BASE_URL;

export async function getPois() {
  if (USE_MOCKS) {
    return mockPois;
  }

  const response = await fetch(`${API_BASE}/api/pois`);
  return response.json();
}

export async function getScenarios() {
  if (USE_MOCKS) {
    return mockScenarios;
  }

  const response = await fetch(`${API_BASE}/api/scenarios`);
  return response.json();
}

export async function getMapGeoJSON(scenarioId: number) {
  if (USE_MOCKS) {
    return mockMapGeoJSON;
  }

  const response = await fetch(
    `${API_BASE}/api/map/geojson?scenario_id=${scenarioId}`
  );
  return response.json();
}

export async function createRoute(payload: any) {
  if (USE_MOCKS) {
    return mockRouteResponse;
  }

  const response = await fetch(`${API_BASE}/api/routes`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  return response.json();
}
```

This allows Member C to build the full UI without waiting for backend.

---

# 8. How backend should use mock data

Backend should use mock data only until real data is ready.

Example seed logic:

```text
If data/velachery/roads.geojson exists:
    import real roads
Else:
    import data/mock/roads.geojson

If data/velachery/pois.json exists:
    import real POIs
Else:
    use placeholder POIs
```

This way your demo will always run.

---

# 9. What exactly should be frozen?

Freeze these field names.

Do not change them later without team approval.

## Road feature fields

```text
layer_type
segment_id
name
road_type
current_risk_score
current_risk_level
predicted_time_to_high_risk_min
blocked
flood_status
```

## POI fields

```text
layer_type
poi_id
name
category
status
```

## POI list fields

```text
id
external_id
name
category
lat
lon
address
phone
status
nearest_node_id
source
notes
```

## Scenario fields

```text
id
name
description
rainfall_mm_24h
rainfall_mm_1h
source
is_active
```

## Route response fields

```text
request_id
destination
routes
warnings
explanation
```

## Route object fields

```text
route_type
distance_m
duration_min
cost_score
avg_risk_score
high_risk_segments_count
blocked_segments_encountered
predicted_risk_warnings_count
geometry
```

## Warning fields

```text
warning_type
segment_id
road_name
eta_to_segment_min
predicted_time_to_high_risk_min
message
```

## Explanation fields

```text
safe_route_adds_min
high_risk_segments_avoided
blocked_segments_avoided
summary
```

---

# 10. What to tell your agent

You can give your agent this prompt:

```text
Read benchmark_layer.md and docs/API_CONTRACT.md.

Create the frontend mock layer first.

Create these files exactly:
frontend/src/mocks/health.json
frontend/src/mocks/meta.json
frontend/src/mocks/scenarios.json
frontend/src/mocks/pois.json
frontend/src/mocks/mapGeoJSON.json
frontend/src/mocks/routeResponse.json
frontend/src/mocks/activeReports.json
frontend/src/mocks/login.json
frontend/src/mocks/blockedReportResponse.json

Use the frozen API contract exactly.
Do not change field names.
Do not implement chatbot.
Do not implement live weather.
Do not use real external APIs except OSM map tiles.

Then build the React dashboard using these mock files.

The dashboard must show:
1. Map
2. Roads
3. POIs
4. Search bar
5. Category chips
6. Route panel
7. Warnings panel
8. Explanation panel
9. Login button
10. Report modal UI

Use VITE_USE_MOCKS=true for now.
```

---

# 11. What to tell backend agent

```text
Read benchmark_layer.md and docs/API_CONTRACT.md.

Create backend seed data using:
data/mock/roads.geojson
data/velachery/pois.json
data/velachery/scenarios.json

Implement these endpoints exactly according to the frozen contract:
GET /api/health
GET /api/meta/area
GET /api/scenarios
GET /api/pois
GET /api/map/geojson
POST /api/auth/login
POST /api/reports/blocked
GET /api/reports/active
POST /api/reports/{id}/verify

Do not change response field names.
Do not implement chatbot.
Do not implement satellite or CCTV features.
Use SQLite.
Use placeholder data if real data is missing.
```

---

# 12. What to tell AI/routing agent

```text
Read benchmark_layer.md and docs/API_CONTRACT.md.

Implement:
POST /api/routes
POST /api/routes/re-route

Use the frozen route response format exactly.

The route response must include:
request_id
destination
routes
warnings
explanation

Routes must include:
route_type
distance_m
duration_min
cost_score
avg_risk_score
high_risk_segments_count
blocked_segments_encountered
predicted_risk_warnings_count
geometry

Do not change frontend.
Do not change POI API.
Do not change database models unless absolutely required.
If database changes are required, list them separately.
```

---

# 13. Final simple rule

If you remember only one thing:

> Frontend and backend must agree on the exact JSON shape before coding starts.

That is the API contract.

Mock data is simply:

> fake JSON that follows that exact shape.

