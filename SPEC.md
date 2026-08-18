# SPEC.md

Project: SafeRoute Velachery — AI Emergency Evacuation & Safe Route Planning  
Version: 1.0.0  
Status: Implementation-ready hackathon MVP  
Target area: West Velachery, Chennai, Tamil Nadu  
Primary hazard: Urban flooding due to intense northeast monsoon rainfall and cyclonic events  
Primary demo event: Cyclone Michaung replay, approximately 150 mm rainfall in 24 hours

---

## 1. Project Vision, Problem, Target Users, Goals, and Non-Goals

### 1.1 Vision

Build a demo-ready, AI-assisted evacuation decision-support system for one flood-prone neighborhood. The system predicts flood risk at road-segment level, identifies reachable shelters, and recommends the safest evacuation route rather than merely the shortest route.

### 1.2 Problem

During floods and storms, normal navigation may send people along flooded, blocked, or low-lying roads. Emergency responders and residents need to know:

1. Which road segments are likely unsafe.
2. Which shelters are reachable and suitable.
3. Which evacuation route minimizes flood exposure.
4. How routes change when a road becomes blocked.

### 1.3 Target Users

| Role | Description |
|---|---|
| Public Resident | Views flood risk, selects origin, receives safest route to shelter. |
| Emergency Responder | Logs in, marks blocked roads, resolves reports, reviews route impacts. |
| Administrator | Manages scenarios, users, shelters, and recomputation jobs. |

### 1.4 Goals

1. Build a working MVP for one neighborhood: West Velachery, Chennai.
2. Use AI to estimate road-segment flood/blockage propensity.
3. Compute safest evacuation routes using risk-weighted routing.
4. Support simulated blocked-road reports and dynamic rerouting.
5. Show measurable comparison between shortest route and safest route.
6. Provide a stable demo that works without live emergency data.

### 1.5 Non-Goals

The MVP will not:

1. Cover all of Chennai or multiple cities.
2. Provide turn-by-turn voice navigation.
3. Integrate live police, fire, ambulance, or official emergency dispatch systems.
4. Guarantee life-safety-grade routing.
5. Process satellite imagery in real time.
6. Build native mobile apps.
7. Support multi-language UI in MVP.
8. Use real-time crowdsourced data from external social media.

---

## 2. Complete Feature List

### MVP Features

| ID | Feature |
|---|---|
| F1 | Authentication and Role-Based Access |
| F2 | Public Map Dashboard and GeoJSON Layers |
| F3 | Scenario Management and Rainfall Simulation |
| F4 | AI Road Segment Flood Risk Engine |
| F5 | Shelter Directory and Suitability Scoring |
| F6 | Evacuation Route Planning |
| F7 | Route Comparison and Explanation |
| F8 | Blocked Road Reporting |
| F9 | Dynamic Re-routing After Blocked Reports |
| F10 | Data Import and Demo Seeding |
| F11 | Health, Validation, and Diagnostics |

### Optional Features

| ID | Feature |
|---|---|
| O1 | Historical backtest panel |
| O2 | Live Open-Meteo rainfall refresh |
| O3 | SMS/WhatsApp alert mock |
| O4 | Multi-user responder coordination dashboard |
| O5 | Tamil/English UI toggle |

Optional features must not be implemented until all MVP features pass acceptance criteria.

---

## 3. User Roles, Permissions, and Workflows

### 3.1 Roles

| Role | Permissions |
|---|---|
| viewer/public | Read map, shelters, scenarios, routes, risk layers. Create route requests without authentication. |
| responder | All public permissions plus create and resolve blocked-road reports. Activate scenarios. |
| admin | All responder permissions plus create users, create scenarios, manage shelters, force risk recomputation. |

### 3.2 Permission Matrix

| Action | Public | Responder | Admin |
|---|---:|---:|---:|
| GET /api/health | Yes | Yes | Yes |
| GET /api/meta/area | Yes | Yes | Yes |
| GET /api/scenarios | Yes | Yes | Yes |
| POST /api/scenarios | No | No | Yes |
| POST /api/scenarios/{id}/activate | No | Yes | Yes |
| GET /api/map/geojson | Yes | Yes | Yes |
| GET /api/shelters | Yes | Yes | Yes |
| POST /api/routes | Yes | Yes | Yes |
| POST /api/reports/blocked | No | Yes | Yes |
| POST /api/reports/blocked/{id}/resolve | No | Yes | Yes |
| POST /api/admin/recompute-risk | No | No | Yes |
| GET /api/validation/summary | Yes | Yes | Yes |

### 3.3 High-Level Workflows

#### Resident Workflow

1. Open dashboard.
2. View active flood scenario and road risk colors.
3. Click map to set origin.
4. Request evacuation route.
5. System selects best shelter if no shelter is chosen.
6. System displays safest route and shortest route.
7. User reads explanation and warnings.

#### Responder Workflow

1. Login.
2. View active scenario and risk map.
3. Receive or simulate field report.
4. Enter report mode.
5. Click affected road segment.
6. Submit blocked-road report.
7. Risk layer updates.
8. Request route again to confirm rerouting.
9. Resolve report when road becomes passable.

#### Admin Workflow

1. Login.
2. Create or activate scenario.
3. Trigger risk recomputation.
4. Review validation summary.
5. Confirm demo data is stable.

---

## 4. Complete User Journeys and System Workflows

### 4.1 Journey: Resident Finds Safest Evacuation Route

Preconditions:

1. Backend is running.
2. Road network, shelters, and scenarios are seeded.
3. At least one shelter is open and routable.

Journey:

1. User opens `/`.
2. Frontend calls `GET /api/meta/area`.
3. Frontend calls `GET /api/scenarios`.
4. Frontend calls `GET /api/map/geojson?scenario_id={activeScenarioId}&include=roads,shelters`.
5. Map renders roads colored by risk and shelters as markers.
6. User clicks “Set Origin” and clicks a map location.
7. Frontend stores origin coordinates.
8. User clicks “Plan Safest Route”.
9. Frontend calls `POST /api/routes`.
10. Backend snaps origin to nearest graph node.
11. Backend computes shelter suitability and route costs.
12. Backend returns safest route, shortest route, chosen shelter, and explanation.
13. Frontend draws both routes and displays explanation.

### 4.2 Journey: Responder Blocks a Road

Preconditions:

1. Responder is authenticated.
2. Map is loaded.
3. At least one road segment is visible.

Journey:

1. Responder clicks “Report Blockage”.
2. UI enters report mode.
3. Responder clicks a road segment.
4. Modal appears with segment ID and optional note.
5. Responder submits.
6. Frontend calls `POST /api/reports/blocked`.
7. Backend creates report, marks segment blocked, sets risk to critical.
8. Frontend refreshes map GeoJSON.
9. User requests route again.
10. Backend avoids blocked segment if an alternate path exists.

### 4.3 Journey: Scenario Switch

1. User selects “Michaung Replay” from scenario dropdown.
2. Frontend sets local `scenarioId`.
3. Frontend calls `GET /api/map/geojson?scenario_id=3`.
4. Backend computes or retrieves risk for that scenario.
5. Map recolors roads.
6. Route requests made afterward use selected scenario unless overridden.

---

## 5. Functional and Non-Functional Requirements

### 5.1 Functional Requirements

| ID | Requirement |
|---|---|
| FR-1 | The system shall load a road network for West Velachery and render it on a map. |
| FR-2 | The system shall support at least four predefined rainfall scenarios. |
| FR-3 | The system shall compute a flood risk score from 0.0 to 1.0 for each road segment. |
| FR-4 | The system shall classify risk into low, moderate, high, and critical. |
| FR-5 | The system shall compute safest and shortest evacuation routes. |
| FR-6 | The system shall select a shelter automatically if no destination shelter is specified. |
| FR-7 | The system shall allow authenticated responders to mark road segments blocked. |
| FR-8 | The system shall avoid blocked road segments when an alternate path exists. |
| FR-9 | The system shall explain why the safest route was chosen. |
| FR-10 | The system shall provide health and validation endpoints. |

### 5.2 Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-1 | Route response time must be under 2 seconds for a road graph with up to 1000 segments. |
| NFR-2 | Map GeoJSON response time must be under 800 ms for cached active scenario. |
| NFR-3 | Frontend initial load must be under 4 seconds on standard hackathon Wi-Fi. |
| NFR-4 | The system must work in demo mode without external internet except map tiles. |
| NFR-5 | All API errors must return structured JSON. |
| NFR-6 | Passwords must be stored using bcrypt hashing. |
| NFR-7 | Authentication tokens must be JWTs with expiry. |
| NFR-8 | The system must not expose SECRET_KEY to the frontend. |
| NFR-9 | The database must be SQLite for MVP. |
| NFR-10 | The frontend must poll for updated map data every 30 seconds when dashboard is open. |

---

## 6. Complete System Architecture

### 6.1 Architecture Overview

```text
Browser
  |
React + Vite Frontend
  |
HTTP JSON API
  |
FastAPI Backend
  |
  |-- Auth Service
  |-- Scenario Service
  |-- Risk Service
  |-- AI Model Service
  |-- Graph Service
  |-- Routing Service
  |-- Shelter Service
  |-- Explanation Service
  |-- Report Service
  |
SQLite Database
  |
Static Data Files
  |-- roads.geojson
  |-- shelters.json
  |-- scenarios.json
  |-- flood_labels.json
```

### 6.2 Component Responsibilities

| Component | Responsibility |
|---|---|
| Frontend | Renders map, collects user input, calls APIs, displays routes and explanations. |
| FastAPI Backend | Provides REST API, business logic, routing, risk calculation, authentication. |
| Graph Service | Builds and caches in-memory road graph from database. |
| Risk Service | Computes road-segment flood risk for scenarios. |
| AI Model Service | Trains and loads flood propensity model. |
| Routing Service | Computes shortest and safest paths using Dijkstra. |
| Shelter Service | Scores shelters and selects best destination. |
| Report Service | Manages blocked-road reports. |
| SQLite | Persists users, roads, shelters, scenarios, reports, routes, risk snapshots. |

### 6.3 High-Level Request Flow for Route Planning

```text
POST /api/routes
  |
  v
Validate payload
  |
  v
Snap origin to nearest node
  |
  v
Load active or requested scenario
  |
  v
Load risk cache for scenario
  |
  v
If destination absent:
    score all open shelters
    compute route to each candidate shelter
    select best adjusted cost
  |
  v
Compute safest path and shortest path
  |
  v
Generate explanation
  |
  v
Persist route request and route results
  |
  v
Return JSON response
```

---

## 7. Technology Stack

| Technology | Exact Purpose |
|---|---|
| Python 3.11 | Backend runtime. |
| FastAPI | REST API framework. |
| Uvicorn | ASGI server. |
| SQLAlchemy 2 | ORM and database access. |
| SQLite | MVP database. |
| Pydantic v2 | Request/response validation. |
| Pydantic Settings | Environment configuration. |
| NetworkX or custom Dijkstra | Graph representation and pathfinding. MVP may use custom Dijkstra for dynamic edge costs. |
| scikit-learn | IsolationForest flood propensity model. |
| joblib | Model serialization. |
| Pandas | Data import and feature preparation. |
| passlib[bcrypt] | Password hashing. |
| python-jose | JWT creation and validation. |
| React 18 | Frontend UI. |
| Vite | Frontend build tool. |
| TypeScript | Frontend type safety. |
| Leaflet 1.9 | Interactive map. |
| Zustand | Lightweight frontend state management. |
| React Router | Page routing. |
| Fetch API | HTTP client. |
| Pytest | Backend tests. |

---

## 8. Complete Folder/File Structure

```text
/saf route-velachery
|-- SPEC.md
|-- .env.example
|-- .gitignore
|-- README.md
|
|-- backend
|   |-- requirements.txt
|   |-- app
|   |   |-- __init__.py
|   |   |-- main.py
|   |   |-- config.py
|   |   |-- database.py
|   |   |-- models.py
|   |   |-- schemas.py
|   |   |-- auth.py
|   |   |-- dependencies.py
|   |   |
|   |   |-- routers
|   |   |   |-- __init__.py
|   |   |   |-- health.py
|   |   |   |-- auth.py
|   |   |   |-- meta.py
|   |   |   |-- scenarios.py
|   |   |   |-- map.py
|   |   |   |-- shelters.py
|   |   |   |-- routes.py
|   |   |   |-- reports.py
|   |   |   |-- admin.py
|   |   |   |-- validation.py
|   |   |
|   |   |-- services
|   |   |   |-- __init__.py
|   |   |   |-- geo_service.py
|   |   |   |-- graph_service.py
|   |   |   |-- risk_service.py
|   |   |   |-- routing_service.py
|   |   |   |-- shelter_service.py
|   |   |   |-- scenario_service.py
|   |   |   |-- report_service.py
|   |   |   |-- explanation_service.py
|   |   |   |-- import_service.py
|   |   |
|   |   |-- ai
|   |   |   |-- __init__.py
|   |   |   |-- features.py
|   |   |   |-- train_model.py
|   |   |   |-- predict.py
|   |   |
|   |   |-- utils
|   |   |   |-- __init__.py
|   |   |   |-- errors.py
|   |   |   |-- rate_limit.py
|   |   |   |-- geo_math.py
|   |   |
|   |   |-- scripts
|   |       |-- __init__.py
|   |       |-- init_db.py
|   |       |-- import_data.py
|   |       |-- seed_users.py
|   |
|   |-- tests
|       |-- __init__.py
|       |-- conftest.py
|       |-- test_auth.py
|       |-- test_risk.py
|       |-- test_routes.py
|       |-- test_reports.py
|
|-- frontend
|   |-- package.json
|   |-- vite.config.ts
|   |-- tsconfig.json
|   |-- index.html
|   |-- src
|       |-- main.tsx
|       |-- App.tsx
|       |-- config.ts
|       |-- api
|       |   |-- client.ts
|       |   |-- types.ts
|       |
|       |-- store
|       |   |-- appStore.ts
|       |
|       |-- pages
|       |   |-- LoginPage.tsx
|       |   |-- DashboardPage.tsx
|       |
|       |-- components
|       |   |-- AppShell.tsx
|       |   |-- MapPanel.tsx
|       |   |-- LayerControl.tsx
|       |   |-- ScenarioSelect.tsx
|       |   |-- OriginPicker.tsx
|       |   |-- ShelterPanel.tsx
|       |   |-- RoutePanel.tsx
|       |   |-- ExplanationPanel.tsx
|       |   |-- ReportBlockageModal.tsx
|       |   |-- AlertsBar.tsx
|       |   |-- Legend.tsx
|       |   |-- LoginButton.tsx
|       |
|       |-- styles
|       |   |-- global.css
|       |   |-- map.css
|       |
|       |-- utils
|           |-- format.ts
|           |-- geo.ts
|
|-- data
|   |-- velachery
|       |-- roads.geojson
|       |-- shelters.json
|       |-- scenarios.json
|       |-- flood_labels.json
|       |-- overpass_query.txt
|
|-- models
|   |-- risk_model.joblib
|   |-- model_meta.json
|
|-- docs
    |-- demo_script.md
```

### 8.1 File Responsibilities

| File | Responsibility |
|---|---|
| `backend/app/main.py` | Creates FastAPI app, registers routers, mounts static frontend build in production. |
| `backend/app/config.py` | Loads environment variables and app settings. |
| `backend/app/database.py` | Creates SQLAlchemy engine and session factory. |
| `backend/app/models.py` | Defines ORM entities. |
| `backend/app/schemas.py` | Defines Pydantic request/response models. |
| `backend/app/auth.py` | JWT creation, password hashing, current user dependency. |
| `backend/app/routers/*` | HTTP endpoint definitions. |
| `backend/app/services/*` | Business logic. |
| `backend/app/ai/train_model.py` | Trains IsolationForest model. |
| `backend/app/ai/predict.py` | Loads model and predicts static flood propensity. |
| `backend/app/scripts/import_data.py` | Imports roads, shelters, scenarios into DB. |
| `frontend/src/store/appStore.ts` | Global UI state. |
| `frontend/src/api/client.ts` | API calls and error normalization. |
| `frontend/src/components/MapPanel.tsx` | Leaflet map rendering. |
| `data/velachery/roads.geojson` | OSM road network extract. |
| `data/velachery/shelters.json` | Curated shelter data from GCC relief centre list. |
| `data/velachery/scenarios.json` | Predefined rainfall scenarios. |

---

## 9. Database Design

Database: SQLite  
ORM: SQLAlchemy 2  
Naming convention: snake_case tables and columns.

### 9.1 users

| Field | Type | Constraint |
|---|---|---|
| id | INTEGER | Primary key, autoincrement |
| username | TEXT | Not null, unique, case-insensitive |
| password_hash | TEXT | Not null |
| role | TEXT | Not null, one of `viewer`, `responder`, `admin` |
| is_active | BOOLEAN | Not null, default true |
| created_at | TIMESTAMP | Not null, default current timestamp |
| updated_at | TIMESTAMP | Not null, default current timestamp |

Indexes:

```text
ix_users_username ON users(username)
```

### 9.2 nodes

| Field | Type | Constraint |
|---|---|---|
| id | INTEGER | Primary key, autoincrement |
| lat | REAL | Not null |
| lon | REAL | Not null |
| lon_lat_key | TEXT | Not null, unique |

`lon_lat_key` must be constructed as:

```text
f"{lon:.7f}_{lat:.7f}"
```

Indexes:

```text
ix_nodes_lon_lat_key ON nodes(lon_lat_key)
```

### 9.3 road_segments

| Field | Type | Constraint |
|---|---|---|
| id | INTEGER | Primary key, autoincrement |
| osm_way_id | TEXT | Nullable, indexed |
| name | TEXT | Nullable |
| road_type | TEXT | Not null, default `unclassified` |
| from_node_id | INTEGER | Not null, foreign key to nodes.id |
| to_node_id | INTEGER | Not null, foreign key to nodes.id |
| length_m | REAL | Not null, >= 0 |
| geometry_json | TEXT | Not null, GeoJSON LineString coordinate array |
| is_underpass | INTEGER | Not null, default 0 |
| low_lying_prior | REAL | Not null, default 0.35, between 0 and 1 |
| proximity_to_water | REAL | Not null, default 0.5, between 0 and 1 |
| drainage_proxy | REAL | Not null, default 0.5, between 0 and 1 |
| hazard_category | TEXT | Not null, one of `very_high`, `high`, `moderate`, `low`, `unknown` |
| historical_flood_count | INTEGER | Not null, default 0 |
| ml_static_propensity | REAL | Nullable, between 0 and 1 |
| risk_score | REAL | Not null, default 0, between 0 and 1 |
| risk_level | TEXT | Not null, default `low`, one of `low`, `moderate`, `high`, `critical` |
| blocked | INTEGER | Not null, default 0 |
| active_report_count | INTEGER | Not null, default 0 |
| updated_at | TIMESTAMP | Not null |

Indexes:

```text
ix_road_segments_from_node ON road_segments(from_node_id)
ix_road_segments_to_node ON road_segments(to_node_id)
ix_road_segments_risk_level ON road_segments(risk_level)
ix_road_segments_blocked ON road_segments(blocked)
ix_road_segments_osm_way_id ON road_segments(osm_way_id)
```

### 9.4 shelters

| Field | Type | Constraint |
|---|---|---|
| id | INTEGER | Primary key, autoincrement |
| external_id | TEXT | Nullable, unique |
| name | TEXT | Not null |
| type | TEXT | Not null, one of `school`, `community_center`, `college`, `religious_building`, `other` |
| lat | REAL | Not null |
| lon | REAL | Not null |
| nearest_node_id | INTEGER | Nullable, foreign key to nodes.id |
| capacity_assumed | INTEGER | Not null, default 100, >= 0 |
| occupancy_assumed | INTEGER | Not null, default 0, >= 0 |
| elevation_risk | TEXT | Not null, one of `low`, `moderate`, `high`, `critical`, `unknown` |
| accessible | INTEGER | Not null, default 0 |
| medical_support | INTEGER | Not null, default 0 |
| water_available | INTEGER | Not null, default 0 |
| status | TEXT | Not null, one of `open`, `full`, `closed` |
| source | TEXT | Not null, default `GCC relief centre list` |
| notes | TEXT | Nullable |
| created_at | TIMESTAMP | Not null |
| updated_at | TIMESTAMP | Not null |

Indexes:

```text
ix_shelters_status ON shelters(status)
ix_shelters_nearest_node ON shelters(nearest_node_id)
```

### 9.5 scenarios

| Field | Type | Constraint |
|---|---|---|
| id | INTEGER | Primary key, autoincrement |
| name | TEXT | Not null, unique |
| description | TEXT | Nullable |
| rainfall_mm_24h | REAL | Not null, >= 0 |
| rainfall_mm_1h | REAL | Not null, >= 0 |
| source | TEXT | Not null, default `manual` |
| is_active | INTEGER | Not null, default 0 |
| created_by_user_id | INTEGER | Nullable, foreign key to users.id |
| created_at | TIMESTAMP | Not null |

Indexes:

```text
ix_scenarios_is_active ON scenarios(is_active)
```

### 9.6 risk_snapshots

| Field | Type | Constraint |
|---|---|---|
| id | INTEGER | Primary key, autoincrement |
| scenario_id | INTEGER | Not null, foreign key to scenarios.id, cascade delete |
| segment_id | INTEGER | Not null, foreign key to road_segments.id, cascade delete |
| risk_score | REAL | Not null, between 0 and 1 |
| risk_level | TEXT | Not null |
| factors_json | TEXT | Not null |
| computed_at | TIMESTAMP | Not null |

Unique constraint:

```text
uq_risk_snapshots_scenario_segment ON (scenario_id, segment_id)
```

### 9.7 blocked_reports

| Field | Type | Constraint |
|---|---|---|
| id | INTEGER | Primary key, autoincrement |
| segment_id | INTEGER | Not null, foreign key to road_segments.id |
| user_id | INTEGER | Not null, foreign key to users.id |
| note | TEXT | Nullable, max 500 characters |
| source | TEXT | Not null, default `responder` |
| status | TEXT | Not null, one of `active`, `resolved`, `rejected` |
| confidence | REAL | Not null, default 0.9, between 0 and 1 |
| created_at | TIMESTAMP | Not null |
| resolved_at | TIMESTAMP | Nullable |

Indexes:

```text
ix_blocked_reports_segment_status ON blocked_reports(segment_id, status)
ix_blocked_reports_status ON blocked_reports(status)
```

### 9.8 route_requests

| Field | Type | Constraint |
|---|---|---|
| id | INTEGER | Primary key, autoincrement |
| scenario_id | INTEGER | Not null, foreign key to scenarios.id |
| origin_lat | REAL | Not null |
| origin_lon | REAL | Not null |
| origin_node_id | INTEGER | Not null, foreign key to nodes.id |
| destination_shelter_id | INTEGER | Nullable, foreign key to shelters.id |
| strategy | TEXT | Not null, one of `auto`, `safest`, `shortest` |
| status | TEXT | Not null, one of `completed`, `failed` |
| error_code | TEXT | Nullable |
| created_at | TIMESTAMP | Not null |

Indexes:

```text
ix_route_requests_created_at ON route_requests(created_at)
```

### 9.9 route_results

| Field | Type | Constraint |
|---|---|---|
| id | INTEGER | Primary key, autoincrement |
| request_id | INTEGER | Not null, foreign key to route_requests.id, cascade delete |
| route_type | TEXT | Not null, one of `safest`, `shortest`, `alternative` |
| shelter_id | INTEGER | Nullable, foreign key to shelters.id |
| node_sequence_json | TEXT | Not null |
| edge_sequence_json | TEXT | Not null |
| geometry_json | TEXT | Not null |
| distance_m | REAL | Not null, >= 0 |
| duration_min | REAL | Not null, >= 0 |
| cost_score | REAL | Not null, >= 0 |
| avg_risk_score | REAL | Not null, >= 0 |
| high_risk_segments_count | INTEGER | Not null, >= 0 |
| blocked_segments_encountered | INTEGER | Not null, >= 0 |
| created_at | TIMESTAMP | Not null |

Indexes:

```text
ix_route_results_request ON route_results(request_id)
```

### 9.10 audit_logs

| Field | Type | Constraint |
|---|---|---|
| id | INTEGER | Primary key, autoincrement |
| user_id | INTEGER | Nullable, foreign key to users.id |
| action | TEXT | Not null |
| entity_type | TEXT | Not null |
| entity_id | INTEGER | Nullable |
| payload_json | TEXT | Nullable |
| created_at | TIMESTAMP | Not null |

Indexes:

```text
ix_audit_logs_user_action ON audit_logs(user_id, action)
```

---

## 10. Complete API Specification

Base URL:

```text
/api
```

Content type:

```text
application/json
```

### 10.1 Common Error Schema

All errors must return:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {}
  }
}
```

Common HTTP codes:

| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Created |
| 400 | Bad request |
| 401 | Unauthenticated |
| 403 | Forbidden |
| 404 | Not found |
| 422 | Validation or business rule failure |
| 429 | Rate limited |
| 500 | Internal server error |

### 10.2 GET /api/health

Authentication: None

Response:

```json
{
  "status": "ok",
  "time": "2026-08-18T10:00:00Z",
  "version": "1.0.0",
  "model_loaded": true,
  "active_scenario_id": 3,
  "segment_count": 412,
  "shelter_count": 5
}
```

Errors:

| Code | Condition |
|---|---|
| INTERNAL | Database unavailable |

### 10.3 POST /api/auth/login

Authentication: None

Request:

```json
{
  "username": "responder",
  "password": "password123"
}
```

Validation:

| Field | Rule |
|---|---|
| username | string, 3–64 chars |
| password | string, 6–128 chars |

Business logic:

1. Find active user by username.
2. Verify password using bcrypt.
3. If invalid, increment in-memory failed-login counter for IP.
4. If more than 5 failed attempts in 60 seconds from same IP, return 429.
5. Create JWT with payload:

```json
{
  "sub": "user_id",
  "username": "responder",
  "role": "responder",
  "exp": 43200
}
```

Response:

```json
{
  "access_token": "jwt-token",
  "token_type": "Bearer",
  "expires_in": 43200,
  "user": {
    "id": 2,
    "username": "responder",
    "role": "responder"
  }
}
```

Errors:

| Code | HTTP | Condition |
|---|---:|---|
| VALIDATION_ERROR | 422 | Invalid body |
| INVALID_CREDENTIALS | 401 | Wrong username or password |
| RATE_LIMITED | 429 | Too many failed attempts |

### 10.4 GET /api/meta/area

Authentication: None

Response:

```json
{
  "name": "West Velachery, Chennai",
  "bbox": [12.965, 80.195, 12.995, 80.235],
  "default_center": [12.981, 80.213],
  "default_zoom": 15,
  "disclaimer": "Decision-support demo only. Not an official emergency service."
}
```

### 10.5 GET /api/scenarios

Authentication: None

Response:

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
  }
]
```

### 10.6 POST /api/scenarios

Authentication: Admin

Request:

```json
{
  "name": "Extreme Event",
  "description": "250 mm in 24 hours",
  "rainfall_mm_24h": 250,
  "rainfall_mm_1h": 50,
  "source": "manual"
}
```

Validation:

| Field | Rule |
|---|---|
| name | string, 3–80 chars, unique |
| description | optional string, max 300 chars |
| rainfall_mm_24h | number, 0–1000 |
| rainfall_mm_1h | number, 0–300 |
| source | optional string, max 120 chars |

Business logic:

1. Insert scenario.
2. Do not automatically activate.
3. Write audit log.

Response: 201 with scenario object.

Errors:

| Code | HTTP | Condition |
|---|---:|---|
| UNAUTHORIZED | 401 | Missing/invalid token |
| FORBIDDEN | 403 | Role not admin |
| VALIDATION_ERROR | 422 | Invalid payload |
| SCENARIO_EXISTS | 422 | Name already exists |

### 10.7 POST /api/scenarios/{scenario_id}/activate

Authentication: Responder or Admin

Path params:

| Param | Type |
|---|---|
| scenario_id | integer |

Business logic:

1. Load scenario. If missing, return 404.
2. Set all scenarios `is_active = 0`.
3. Set selected scenario `is_active = 1`.
4. Recompute risk for all road segments for this scenario.
5. Store or update `risk_snapshots` for this scenario.
6. Write audit log.

Response:

```json
{
  "scenario_id": 3,
  "active": true,
  "segments_updated": 412
}
```

Errors:

| Code | HTTP | Condition |
|---|---:|---|
| UNAUTHORIZED | 401 | Missing/invalid token |
| FORBIDDEN | 403 | Role not responder/admin |
| SCENARIO_NOT_FOUND | 404 | Invalid scenario_id |
| INTERNAL | 500 | Risk recomputation failure |

### 10.8 GET /api/map/geojson

Authentication: None

Query params:

| Param | Type | Default | Rule |
|---|---|---|---|
| scenario_id | integer | active scenario | Must exist if provided |
| include | string | `roads,shelters` | Comma-separated subset of `roads`, `shelters`, `reports` |

Business logic:

1. If `scenario_id` is absent, use active scenario.
2. If no active scenario exists, return 422 `NO_ACTIVE_SCENARIO`.
3. For roads, build FeatureCollection.
4. Road feature properties:

```json
{
  "segment_id": 12,
  "name": "AGS Colony Road",
  "road_type": "residential",
  "risk_score": 0.82,
  "risk_level": "critical",
  "blocked": true,
  "is_underpass": false
}
```

5. Shelter feature properties:

```json
{
  "shelter_id": 3,
  "name": "Community Hall",
  "status": "open",
  "capacity_assumed": 200,
  "occupancy_assumed": 40,
  "elevation_risk": "low",
  "suitability": 0.76
}
```

6. If `include=reports`, include active blocked reports as point features using segment midpoint.

Response:

```json
{
  "type": "FeatureCollection",
  "features": []
}
```

Errors:

| Code | HTTP | Condition |
|---|---:|---|
| VALIDATION_ERROR | 422 | Invalid include value |
| SCENARIO_NOT_FOUND | 404 | Invalid scenario_id |
| NO_ACTIVE_SCENARIO | 422 | No scenario active and no scenario_id provided |

### 10.9 GET /api/shelters

Authentication: None

Query params:

| Param | Type | Default |
|---|---|---|
| status | string | all |

Response item:

```json
{
  "id": 1,
  "name": "Corporation School",
  "type": "school",
  "lat": 12.981,
  "lon": 80.213,
  "status": "open",
  "capacity_assumed": 200,
  "occupancy_assumed": 20,
  "elevation_risk": "low",
  "accessible": true,
  "medical_support": false,
  "water_available": true,
  "suitability": 0.81,
  "routable": true
}
```

Business logic:

1. Compute suitability using formula in section 12.6.
2. `routable` is true if `nearest_node_id` is not null.

### 10.10 GET /api/shelters/{shelter_id}

Authentication: None

Response: single shelter object.

Errors:

| Code | HTTP | Condition |
|---|---:|---|
| SHELTER_NOT_FOUND | 404 | Invalid ID |

### 10.11 POST /api/routes

Authentication: None

Request:

```json
{
  "origin": {
    "lat": 12.9781,
    "lon": 80.2109
  },
  "destination_shelter_id": null,
  "scenario_id": 3,
  "strategy": "auto",
  "include_alternatives": true
}
```

Validation:

| Field | Rule |
|---|---|
| origin.lat | number, -90 to 90 |
| origin.lon | number, -180 to 180 |
| destination_shelter_id | optional integer |
| scenario_id | optional integer |
| strategy | one of `auto`, `safest`, `shortest`, default `auto` |
| include_alternatives | boolean, default true |

Business logic:

1. Load scenario. If `scenario_id` absent, use active scenario.
2. Snap origin to nearest node within `SNAP_RADIUS_METERS`.
3. If no node found, return 422 `ORIGIN_NOT_SNAPPABLE`.
4. If destination shelter provided:
   1. Load shelter.
   2. If shelter status is `closed`, return 422 `SHELTER_CLOSED`.
   3. If shelter `nearest_node_id` is null, return 422 `DESTINATION_NOT_ROUTABLE`.
5. If destination shelter absent:
   1. Load all shelters with status `open` and `nearest_node_id` not null.
   2. If none exist, return 422 `NO_ROUTABLE_SHELTERS`.
   3. For each shelter, compute safest route.
   4. Compute shelter suitability.
   5. Compute adjusted cost:

   ```text
   adjusted_cost = safest_route_cost + (1 - suitability) * 30
   ```

   6. Select shelter with lowest adjusted cost.
6. For selected shelter, compute:
   1. safest route
   2. shortest route
7. If no path exists without blocked edges, retry allowing blocked edges with penalty.
8. If still no path, return 422 `ROUTE_NOT_FOUND`.
9. Persist `route_requests` and `route_results`.
10. Build explanation.

Response:

```json
{
  "request_id": 18,
  "scenario_id": 3,
  "origin_node_id": 231,
  "chosen_shelter": {
    "id": 2,
    "name": "Community Hall",
    "status": "open",
    "suitability": 0.79
  },
  "routes": [
    {
      "route_id": 35,
      "route_type": "safest",
      "shelter_id": 2,
      "distance_m": 1820,
      "duration_min": 9.7,
      "cost_score": 21.4,
      "avg_risk_score": 0.18,
      "high_risk_segments_count": 0,
      "blocked_segments_encountered": 0,
      "geometry": {
        "type": "LineString",
        "coordinates": [[80.2109, 12.9781], [80.2115, 12.9789]]
      }
    },
    {
      "route_id": 36,
      "route_type": "shortest",
      "shelter_id": 2,
      "distance_m": 1450,
      "duration_min": 7.1,
      "cost_score": 7.1,
      "avg_risk_score": 0.63,
      "high_risk_segments_count": 4,
      "blocked_segments_encountered": 0,
      "geometry": {
        "type": "LineString",
        "coordinates": [[80.2109, 12.9781], [80.2101, 12.9775]]
      }
    }
  ],
  "explanation": {
    "additional_time_min": 2.6,
    "high_risk_segments_avoided": 4,
    "blocked_segments_avoided": 0,
    "shelter_reasons": [
      "Shelter has available assumed capacity",
      "Shelter elevation risk is low"
    ],
    "top_factors": [
      "Shortest route passes through high-risk AGS Colony roads",
      "Safest route avoids low-lying segments near Velachery lake side"
    ]
  },
  "warnings": []
}
```

Errors:

| Code | HTTP | Condition |
|---|---:|---|
| VALIDATION_ERROR | 422 | Invalid payload |
| NO_ACTIVE_SCENARIO | 422 | No scenario provided and none active |
| SCENARIO_NOT_FOUND | 404 | Invalid scenario |
| ORIGIN_NOT_SNAPPABLE | 422 | Origin too far from road graph |
| SHELTER_NOT_FOUND | 404 | Invalid shelter |
| SHELTER_CLOSED | 422 | Requested shelter closed |
| DESTINATION_NOT_ROUTABLE | 422 | Shelter not snapped to road graph |
| NO_ROUTABLE_SHELTERS | 422 | No open routable shelters |
| ROUTE_NOT_FOUND | 422 | No path exists |

### 10.12 GET /api/routes/{request_id}

Authentication: None

Response: stored route request and results.

Errors:

| Code | HTTP | Condition |
|---|---:|---|
| ROUTE_REQUEST_NOT_FOUND | 404 | Invalid ID |

### 10.13 POST /api/reports/blocked

Authentication: Responder or Admin

Request:

```json
{
  "segment_id": 214,
  "note": "Waterlogged near AGS Colony entrance"
}
```

Validation:

| Field | Rule |
|---|---|
| segment_id | integer, must exist |
| note | optional string, max 500 |

Business logic:

1. Load segment. If missing, return 404.
2. Check existing active report for same segment.
3. If active report exists, return existing report with HTTP 200.
4. Create blocked report with status `active`.
5. Increment `road_segments.active_report_count`.
6. Set `road_segments.blocked = 1`.
7. Set `road_segments.risk_score = 1.0`.
8. Set `road_segments.risk_level = "critical"`.
9. Recompute active scenario risk for that segment.
10. Write audit log.

Response:

```json
{
  "report_id": 8,
  "segment_id": 214,
  "status": "active",
  "segment": {
    "id": 214,
    "blocked": true,
    "risk_score": 1.0,
    "risk_level": "critical"
  }
}
```

Errors:

| Code | HTTP | Condition |
|---|---:|---|
| UNAUTHORIZED | 401 | Missing/invalid token |
| FORBIDDEN | 403 | Role not responder/admin |
| SEGMENT_NOT_FOUND | 404 | Invalid segment |
| VALIDATION_ERROR | 422 | Invalid body |

### 10.14 POST /api/reports/blocked/{report_id}/resolve

Authentication: Responder or Admin

Business logic:

1. Load report. If missing, return 404.
2. If already resolved, return 200 with report.
3. Set report status `resolved`.
4. Set `resolved_at` current timestamp.
5. Count remaining active reports for segment.
6. If count is zero:
   1. Set `road_segments.blocked = 0`.
   2. Set `active_report_count = 0`.
   3. Recompute segment risk for active scenario.
7. If count greater than zero:
   1. Decrement `active_report_count`.
   2. Keep `blocked = 1`.
8. Write audit log.

Response:

```json
{
  "report_id": 8,
  "status": "resolved",
  "segment": {
    "id": 214,
    "blocked": false,
    "risk_score": 0.46,
    "risk_level": "moderate"
  }
}
```

Errors:

| Code | HTTP | Condition |
|---|---:|---|
| UNAUTHORIZED | 401 | Missing/invalid token |
| FORBIDDEN | 403 | Role not responder/admin |
| REPORT_NOT_FOUND | 404 | Invalid report ID |

### 10.15 GET /api/reports/active

Authentication: None

Response:

```json
[
  {
    "id": 8,
    "segment_id": 214,
    "note": "Waterlogged near AGS Colony entrance",
    "status": "active",
    "created_at": "2026-08-19T09:12:00Z",
    "segment_name": "AGS Colony Road"
  }
]
```

### 10.16 POST /api/admin/recompute-risk

Authentication: Admin

Business logic:

1. Load active scenario.
2. Recompute all road segment risks.
3. Upsert risk snapshots.
4. Return count.

Response:

```json
{
  "scenario_id": 3,
  "segments_updated": 412
}
```

Errors:

| Code | HTTP | Condition |
|---|---:|---|
| UNAUTHORIZED | 401 | Missing/invalid token |
| FORBIDDEN | 403 | Role not admin |
| NO_ACTIVE_SCENARIO | 422 | No active scenario |

### 10.17 GET /api/validation/summary

Authentication: None

Response:

```json
{
  "model_loaded": true,
  "model_type": "IsolationForest",
  "segment_count": 412,
  "risk_distribution": {
    "low": 230,
    "moderate": 110,
    "high": 50,
    "critical": 22
  },
  "top_high_risk_segments": [
    {
      "segment_id": 214,
      "name": "AGS Colony Road",
      "risk_score": 0.92,
      "risk_level": "critical"
    }
  ],
  "documented_flood_pockets": [
    "AGS Colony",
    "Baby Nagar",
    "Dhandeeswaran Nagar",
    "Venkateshwara Nagar",
    "EB Colony",
    "Ayothi Colony",
    "Vijayanagar",
    "Ramnagar",
    "Murugan Nagar",
    "Kuberan Nagar"
  ]
}
```

---

## 11. Frontend Pages, Components, States, Interactions, and API Integration

### 11.1 Pages

| Route | Page | Purpose |
|---|---|---|
| `/` | DashboardPage | Main map and control panels. |
| `/login` | LoginPage | Login form for responders/admins. |

### 11.2 Global State

State manager: Zustand.

Store shape:

```ts
interface AppState {
  user: AuthUser | null;
  token: string | null;
  areaMeta: AreaMeta | null;
  scenarios: Scenario[];
  selectedScenarioId: number | null;
  geojson: GeoJSONFeatureCollection | null;
  origin: { lat: number; lon: number } | null;
  routeResponse: RouteResponse | null;
  activeReports: BlockedReport[];
  mapMode: "pan" | "origin" | "report";
  loading: boolean;
  error: string | null;
}
```

Actions:

```ts
setUser(token, user)
logout()
setAreaMeta(meta)
setScenarios(scenarios)
selectScenario(id)
setGeojson(data)
setOrigin(lat, lon)
setRouteResponse(response)
setMapMode(mode)
setError(message)
clearError()
```

### 11.3 API Client

`frontend/src/api/client.ts` must implement:

```ts
api.getHealth()
api.login(username, password)
api.getMeta()
api.getScenarios()
api.getMapGeoJSON(scenarioId, include)
api.getShelters()
api.createRoute(payload)
api.createBlockedReport(segmentId, note, token)
api.resolveBlockedReport(reportId, token)
api.getActiveReports()
api.getValidationSummary()
```

All API errors must be normalized to:

```ts
{
  code: string;
  message: string;
}
```

### 11.4 LoginPage

Purpose:

Authenticate responder/admin users.

UI behavior:

1. Show username and password fields.
2. Disable submit while loading.
3. On success, store token in Zustand and localStorage key `safetoute_token`.
4. Redirect to `/`.
5. On failure, display error message from API.

API calls:

```text
POST /api/auth/login
```

Error states:

| Error | UI |
|---|---|
| INVALID_CREDENTIALS | “Invalid username or password.” |
| RATE_LIMITED | “Too many attempts. Try again later.” |
| NETWORK | “Cannot reach server.” |

### 11.5 DashboardPage

Purpose:

Main emergency dashboard.

Layout:

```text
Header
  - Project title
  - Scenario selector
  - Login/logout button
  - Disclaimer badge

Main
  - MapPanel occupying 65% width on desktop

Side panel
  - LayerControl
  - OriginPicker
  - ShelterPanel
  - RoutePanel
  - ExplanationPanel
  - ActiveReports list

Footer
  - Legend
```

States:

| State | UI |
|---|---|
| initial loading | Spinner overlay |
| map loaded | Map visible |
| error | AlertsBar with retry button |
| route loading | RoutePanel spinner |
| route ready | Routes drawn and panel populated |

### 11.6 MapPanel

Purpose:

Render roads, shelters, routes, origin, and reports.

Dependencies:

- Leaflet
- `areaMeta`
- `geojson`
- `routeResponse`

Behavior:

1. Initialize map at `areaMeta.default_center` and `default_zoom`.
2. Add tile layer:

```text
https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
```

3. Render road GeoJSON as polylines.
4. Color roads by `risk_level`:

| risk_level | Color |
|---|---|
| low | `#22c55e` |
| moderate | `#facc15` |
| high | `#f97316` |
| critical | `#dc2626` |

5. Blocked segments must use dashed style and color `#7f1d1d`.
6. Render shelters as circle markers:

| status | Color |
|---|---|
| open | `#16a34a` |
| full | `#f59e0b` |
| closed | `#dc2626` |

7. Render safest route as solid blue line `#2563eb`.
8. Render shortest route as dashed gray line `#94a3b8`.
9. Render origin as purple marker `#7c3aed`.
10. If `mapMode === "origin"`, map click sets origin.
11. If `mapMode === "report"`, road click opens ReportBlockageModal.
12. Fit bounds to route after route response.

Edge cases:

| Case | Behavior |
|---|---|
| GeoJSON empty | Show alert “No map data available.” |
| Tile load failure | Map still renders with background and vector layers. |
| Route geometry empty | Show warning “No route geometry returned.” |

### 11.7 ScenarioSelect

Purpose:

Allow user to choose rainfall scenario.

UI:

Dropdown with scenario names.

Behavior:

1. On mount, call `GET /api/scenarios`.
2. Select active scenario by default.
3. On change:
   1. Set `selectedScenarioId`.
   2. Call `GET /api/map/geojson?scenario_id=...`.
   3. Clear existing route response.

Validation:

Scenario list must not be empty. If empty, show error.

### 11.8 OriginPicker

Purpose:

Set evacuation origin.

UI:

Buttons:

```text
Set Origin
Clear Origin
```

Behavior:

1. “Set Origin” sets `mapMode = "origin"`.
2. User clicks map.
3. Origin marker appears.
4. `mapMode` returns to `"pan"`.
5. “Clear Origin” removes origin and route response.

Error states:

| Case | UI |
|---|---|
| User clicks Plan Route without origin | “Please select an origin point.” |

### 11.9 ShelterPanel

Purpose:

Display shelters and allow manual destination selection.

API:

```text
GET /api/shelters
```

UI fields:

- Name
- Type
- Status badge
- Capacity assumed
- Occupancy assumed
- Suitability bar
- Routable badge

Interaction:

1. Click shelter selects `destination_shelter_id`.
2. Selected shelter highlighted.
3. “Use nearest suitable shelter” clears manual selection.

Edge cases:

| Case | UI |
|---|---|
| No shelters | “No shelters available.” |
| Shelter not routable | Disabled with tooltip “Not connected to road network.” |

### 11.10 RoutePanel

Purpose:

Trigger route planning and show route summaries.

Buttons:

```text
Plan Safest Route
Compare Shortest Route
Clear Route
```

Behavior:

1. Disable buttons if origin not set.
2. On click, call `POST /api/routes`.
3. Show loading spinner.
4. On success, display:

| Field | Safest | Shortest |
|---|---:|---:|
| Distance | meters | meters |
| Duration | minutes | minutes |
| Average risk | 0–1 | 0–1 |
| High-risk segments | count | count |
| Blocked segments encountered | count | count |

5. Highlight recommended route.

Error states:

| API Code | UI Message |
|---|---|
| ORIGIN_NOT_SNAPPABLE | “Selected origin is too far from a road. Click closer to a road.” |
| ROUTE_NOT_FOUND | “No route found to a shelter.” |
| NO_ROUTABLE_SHELTERS | “No open shelters are currently routable.” |
| NETWORK | “Cannot reach server.” |

### 11.11 ExplanationPanel

Purpose:

Explain AI and routing decision.

Data source:

`routeResponse.explanation`

UI:

Bullet list:

```text
- Safest route adds 2.6 minutes compared with shortest route.
- Avoids 4 high-risk segments.
- Avoids 0 blocked segments.
- Selected shelter has available assumed capacity.
- Shortest route passes through high-risk AGS Colony roads.
```

If warnings exist, show warning block.

### 11.12 ReportBlockageModal

Purpose:

Allow authenticated responder to mark road blocked.

Visibility:

Only when:

```text
user.role === "responder" || user.role === "admin"
```

and mapMode is `"report"` and a road segment was clicked.

Fields:

| Field | Type | Validation |
|---|---|---|
| Segment ID | read-only | required |
| Segment name | read-only | optional |
| Note | textarea | max 500 chars |

Buttons:

```text
Submit Report
Cancel
```

Behavior:

1. On submit, call `POST /api/reports/blocked`.
2. On success:
   1. Close modal.
   2. Refresh map GeoJSON.
   3. Refresh active reports.
   4. Clear route response.
3. On error, show inline error.

Error states:

| API Code | UI Message |
|---|---|
| UNAUTHORIZED | “Please login again.” |
| SEGMENT_NOT_FOUND | “Selected road segment no longer exists.” |
| VALIDATION_ERROR | “Note must be under 500 characters.” |

### 11.13 ActiveReports List

Purpose:

Show active blocked reports.

API:

```text
GET /api/reports/active
```

Poll every 30 seconds.

Item display:

```text
Segment: AGS Colony Road
Note: Waterlogged near entrance
Time: 09:12
Resolve button (responder/admin only)
```

Resolve behavior:

1. Call `POST /api/reports/blocked/{id}/resolve`.
2. Refresh map and reports.
3. Clear route response.

### 11.14 Polling Behavior

Frontend must poll:

```text
GET /api/map/geojson
GET /api/reports/active
```

every 30 seconds while DashboardPage is mounted.

Polling must pause when tab is hidden using `document.visibilityState`.

---

## 12. Backend Modules, Services, Middleware, and Business Logic

### 12.1 config.py

Must load environment variables using Pydantic Settings.

Settings:

```python
class Settings(BaseSettings):
    app_env: str
    secret_key: str
    database_url: str
    cors_origins: str
    default_lat: float
    default_lon: float
    area_name: str
    model_path: str
    snap_radius_meters: int
    blocked_penalty: float
    risk_ml_weight: float
    risk_rule_weight: float
    max_route_alternatives: int
    auth_admin_username: str | None
    auth_admin_password: str | None
    auth_responder_username: str | None
    auth_responder_password: str | None
    seed_placeholder_shelters: bool
```

Behavior:

1. In production, fail startup if `secret_key` is empty or equal to `change-me`.
2. Parse `cors_origins` as comma-separated list.
3. Provide singleton `get_settings()`.

### 12.2 database.py

Responsibilities:

1. Create SQLAlchemy engine.
2. Create session factory.
3. Provide `get_db()` dependency.
4. Use `check_same_thread=False` for SQLite.

### 12.3 auth.py

Responsibilities:

1. Hash passwords using bcrypt.
2. Verify passwords.
3. Create JWT.
4. Decode JWT.
5. Provide `get_current_user` dependency.
6. Provide `require_role(roles: list[str])` dependency.

JWT rules:

| Parameter | Value |
|---|---|
| Algorithm | HS256 |
| Expiry | 12 hours |
| Payload | `sub`, `username`, `role`, `exp` |

### 12.4 geo_service.py

Functions:

```python
haversine_m(lat1, lon1, lat2, lon2) -> float
line_length_m(coordinates: list[list[float]]) -> float
nearest_node(db, lat, lon, radius_m) -> Node | None
nearest_segment_midpoint(segment) -> tuple[float, float]
build_linestring(edge_sequence, edge_directions) -> list[list[float]]
```

Rules:

1. Coordinates are `[lon, lat]` in GeoJSON.
2. Node key uses 7 decimal places.
3. Snap radius is `settings.snap_radius_meters`.

### 12.5 graph_service.py

Responsibilities:

1. Build adjacency cache from database.
2. Invalidate cache when road_segments table changes.
3. Provide:

```python
get_adjacency() -> dict[int, list[tuple[int, int]]]
get_segment(segment_id) -> RoadSegment
```

Adjacency structure:

```python
{
  node_id: [(neighbor_node_id, segment_id), ...]
}
```

Graph assumptions:

1. All roads are bidirectional in MVP.
2. One-way restrictions are ignored.

### 12.6 shelter_service.py

Function:

```python
compute_suitability(shelter: Shelter) -> float
```

Formula:

```text
capacity_ratio = max(0, capacity_assumed - occupancy_assumed) / capacity_assumed
if capacity_assumed == 0:
    capacity_ratio = 0

safety_score = {
  "low": 1.0,
  "moderate": 0.6,
  "high": 0.2,
  "critical": 0.0,
  "unknown": 0.4
}[shelter.elevation_risk]

accessibility_score = 1.0 if shelter.accessible else 0.0
medical_score = 1.0 if shelter.medical_support else 0.0
water_score = 1.0 if shelter.water_available else 0.0

suitability = (
  0.35 * capacity_ratio +
  0.35 * safety_score +
  0.15 * accessibility_score +
  0.10 * medical_score +
  0.05 * water_score
)
```

Clamp result to `[0, 1]`.

### 12.7 risk_service.py

Responsibilities:

1. Compute risk for one segment.
2. Compute risk for all segments.
3. Provide risk cache per scenario.
4. Store risk snapshots.

Inputs:

```python
segment: RoadSegment
scenario: Scenario
```

Feature values:

```python
combined_rain = min(
  1.0,
  (0.7 * min(1.0, scenario.rainfall_mm_24h / 150.0)) +
  (0.3 * min(1.0, scenario.rainfall_mm_1h / 30.0))
)

static_propensity = (
  segment.ml_static_propensity
  if segment.ml_static_propensity is not None
  else segment.drainage_proxy
)

blocked_factor = 1.0 if segment.blocked or segment.active_report_count > 0 else 0.0
underpass_factor = 1.0 if segment.is_underpass else 0.0

base_risk = (
  0.45 * combined_rain +
  0.30 * static_propensity +
  0.10 * underpass_factor +
  0.10 * blocked_factor +
  0.05 * segment.low_lying_prior
)
```

Special rules:

```python
if combined_rain < 0.1 and blocked_factor == 0.0:
    risk = min(base_risk, 0.25)

if blocked_factor == 1.0:
    risk = max(base_risk, 0.9)

risk_score = clamp01(risk)
```

Risk levels:

| Score Range | Level |
|---|---|
| 0.00–0.24 | low |
| 0.25–0.49 | moderate |
| 0.50–0.74 | high |
| 0.75–1.00 | critical |

Output:

```python
RiskResult(
  segment_id=segment.id,
  risk_score=risk_score,
  risk_level=risk_level,
  factors={
    "combined_rain": combined_rain,
    "static_propensity": static_propensity,
    "underpass_factor": underpass_factor,
    "blocked_factor": blocked_factor,
    "low_lying_prior": segment.low_lying_prior
  }
)
```

### 12.8 routing_service.py

Responsibilities:

1. Run Dijkstra.
2. Compute edge costs dynamically.
3. Return path nodes, edges, distance, duration, risk metrics.

Speed map in meters per second:

```python
SPEED_MPS = {
  "motorway": 11.0,
  "trunk": 11.0,
  "primary": 11.0,
  "secondary": 8.3,
  "tertiary": 5.6,
  "residential": 5.6,
  "unclassified": 5.6,
  "service": 4.2,
  "track": 4.2,
  "footway": 1.4,
  "path": 1.4,
  "pedestrian": 1.4
}
DEFAULT_SPEED_MPS = 5.6
```

Edge cost formulas:

```python
travel_time_min = segment.length_m / speed_mps / 60.0

risk_penalty_min = (
  risk_score * risk_score * 0.015 * segment.length_m
)

blocked_penalty = settings.blocked_penalty if segment.blocked else 0.0

shortest_edge_cost = travel_time_min + blocked_penalty

safest_edge_cost = (
  travel_time_min +
  risk_penalty_min +
  blocked_penalty
)
```

Routing algorithm:

1. Use min-heap Dijkstra.
2. Maintain:

```python
dist[node_id] = cost
prev[node_id] = (previous_node_id, segment_id)
```

3. First attempt excludes blocked edges entirely.
4. If no path found, retry including blocked edges with penalty.
5. If still no path, return `None`.

Route metrics:

```python
distance_m = sum(segment.length_m)
duration_min = sum(travel_time_min)
avg_risk_score = sum(segment.risk_score * segment.length_m) / distance_m
high_risk_segments_count = count(segment.risk_level in ["high", "critical"])
blocked_segments_encountered = count(segment.blocked == 1)
```

### 12.9 explanation_service.py

Input:

```python
shortest_route: RouteResult
safest_route: RouteResult
chosen_shelter: Shelter
```

Logic:

```python
additional_time_min = max(0, safest_route.duration_min - shortest_route.duration_min)
high_risk_segments_avoided = max(
  0,
  shortest_route.high_risk_segments_count - safest_route.high_risk_segments_count
)
blocked_segments_avoided = max(
  0,
  shortest_route.blocked_segments_encountered - safest_route.blocked_segments_encountered
)
```

Shelter reasons:

1. If capacity available:

```text
"Shelter has available assumed capacity"
```

2. If elevation risk low:

```text
"Shelter elevation risk is low"
```

3. If accessible:

```text
"Shelter is marked accessible"
```

Top factors:

1. If shortest route has high-risk segments:

```text
"Shortest route passes through {count} high-risk segments"
```

2. If shortest route has blocked segments:

```text
"Shortest route encounters {count} blocked segments"
```

3. If safest route has zero high-risk segments:

```text
"Safest route avoids high-risk flood pockets"
```

### 12.10 report_service.py

Responsibilities:

1. Create blocked report.
2. Resolve blocked report.
3. Update segment blocked state.
4. Trigger risk recomputation for affected segment.

Rules:

1. Only one active report per segment is returned as active; duplicate submissions return existing report.
2. Resolving one report does not unblock segment if other active reports exist.
3. Every report mutation writes audit log.

### 12.11 scenario_service.py

Responsibilities:

1. List scenarios.
2. Create scenarios.
3. Activate scenarios.
4. Get active scenario.

Rules:

1. Exactly one scenario may be active.
2. Activating scenario must recompute risk synchronously.
3. Scenario names must be unique.

### 12.12 import_service.py

Responsibilities:

1. Read `roads.geojson`.
2. Create nodes and road segments.
3. Read `shelters.json`.
4. Snap shelters to nearest nodes.
5. Read `scenarios.json`.
6. Upsert scenarios.
7. Seed users.

Road import rules:

1. For each GeoJSON Feature:
   1. Accept geometry type `LineString` or `MultiLineString`.
   2. For each coordinate sequence, create edges between consecutive coordinates.
   3. Create node keys using 7-decimal rounding.
   4. Calculate segment length using haversine.
2. Copy properties:

```text
osm_way_id = properties.osm_id or properties.id
name = properties.name
road_type = properties.highway or "unclassified"
```

3. Set `is_underpass = 1` if:

```text
properties.underpass == true
or properties.name contains "subway"
or properties.name contains "underpass"
```

4. Map hazard category if present:

```text
very_high -> low_lying_prior=1.0, drainage_proxy=1.0
high -> low_lying_prior=0.8, drainage_proxy=0.8
moderate -> low_lying_prior=0.5, drainage_proxy=0.5
low -> low_lying_prior=0.2, drainage_proxy=0.2
unknown -> low_lying_prior=0.35, drainage_proxy=0.35
```

Shelter import rules:

1. Validate lat/lon.
2. Snap to nearest node within `settings.snap_radius_meters`.
3. If no node found, set `nearest_node_id = null` and log warning.
4. If `seed_placeholder_shelters` is true and no shelter file exists, create four dev-only placeholders named:

```text
Dev Placeholder Shelter A
Dev Placeholder Shelter B
Dev Placeholder Shelter C
Dev Placeholder Shelter D
```

Placeholder shelters must not be used in final demo.

---

## 13. AI Architecture

### 13.1 AI Objective

The AI model estimates static flood-prone propensity for each road segment. This propensity is combined with dynamic rainfall scenario factors and blocked-road reports to compute final road risk.

The MVP does not use an LLM.

### 13.2 Model Type

Primary model:

```text
sklearn.ensemble.IsolationForest
```

Purpose:

Detect road segments with anomalous flood-prone characteristics based on static infrastructure and geography features.

### 13.3 Model Inputs

Features per road segment:

| Feature | Type | Source |
|---|---|---|
| length_m | float | road_segments.length_m |
| road_type_encoded | int | encoded road_type |
| is_underpass | int | road_segments.is_underpass |
| proximity_to_water | float | road_segments.proximity_to_water |
| drainage_proxy | float | road_segments.drainage_proxy |
| historical_flood_count | int | road_segments.historical_flood_count |

Road type encoding:

```python
ROAD_TYPE_ENCODE = {
  "footway": 0,
  "path": 0,
  "pedestrian": 0,
  "service": 1,
  "track": 1,
  "residential": 2,
  "unclassified": 2,
  "tertiary": 3,
  "secondary": 4,
  "primary": 5,
  "trunk": 6,
  "motorway": 6
}
```

Default encoding: `2`.

### 13.4 Model Training Rules

Training script:

```bash
python -m app.ai.train_model
```

Rules:

1. Load all road segments from DB.
2. If fewer than 30 segments, do not train.
3. Use `StandardScaler` on features.
4. Train:

```python
IsolationForest(
  n_estimators=200,
  contamination=0.15,
  random_state=42
)
```

5. Use `model.score_samples(X_scaled)`.
6. Convert scores to flood propensity:

```python
raw = model.score_samples(X_scaled)
min_raw = min(raw)
max_raw = max(raw)

if max_raw == min_raw:
    propensity = 0.5 for all segments
else:
    propensity = 1.0 - ((raw - min_raw) / (max_raw - min_raw))
```

Higher propensity means more flood-prone.

7. Save model artifact to `models/risk_model.joblib` as:

```python
{
  "model": model,
  "scaler": scaler,
  "feature_names": [...],
  "trained_at": timestamp,
  "segment_count": count
}
```

8. Save `models/model_meta.json` with:

```json
{
  "trained_at": "...",
  "segment_count": 412,
  "model_type": "IsolationForest",
  "top_propensity_segments": []
}
```

9. Update `road_segments.ml_static_propensity` for all segments.

### 13.5 AI Inference

Inference function:

```python
predict_static_propensity(segment) -> float
```

Rules:

1. If model file missing, return `segment.drainage_proxy`.
2. If model file corrupt, log error and return `segment.drainage_proxy`.
3. Output must be clamped to `[0, 1]`.

### 13.6 Final Risk Composition

```text
final_risk =
  0.45 * combined_rain +
  0.30 * static_propensity +
  0.10 * underpass_factor +
  0.10 * blocked_factor +
  0.05 * low_lying_prior
```

This formula is deterministic and explainable.

### 13.7 AI Validation

Validation approach:

1. Model must output propensity in `[0, 1]`.
2. Top 10 propensity segments must be printed for manual review.
3. Manual review should compare top segments against documented flood pockets:
   - AGS Colony
   - Baby Nagar
   - Dhandeeswaran Nagar
   - Venkateshwara Nagar
   - EB Colony
   - Ayothi Colony
   - Vijayanagar
   - Ramnagar
   - Murugan Nagar
   - Kuberan Nagar
4. For demo acceptance, at least 5 of the top 20 propensity segments should intersect or be adjacent to documented flood pockets, based on manual inspection.

### 13.8 AI Fallbacks

| Failure | Fallback |
|---|---|
| Model missing | Use `drainage_proxy` as static propensity. |
| Model load error | Use `drainage_proxy`. |
| Scenario missing | Return 422, do not guess. |
| Risk computation error for one segment | Set risk_score=0.5 and log error. |
| Risk computation fails globally | Return 500 and use last stored active risk if available. |

### 13.9 LLM and RAG

No LLM is used in MVP.

No RAG is used in MVP.

No prompts are required.

---

## 14. Authentication, Authorization, and Security Requirements

### 14.1 Authentication

1. Use username/password login.
2. Passwords hashed with bcrypt.
3. Successful login returns JWT.
4. Token expires after 12 hours.
5. Token sent as:

```text
Authorization: Bearer <token>
```

### 14.2 Authorization

1. Public endpoints require no token.
2. Mutating emergency endpoints require responder or admin role.
3. Admin endpoints require admin role.
4. Role is embedded in JWT and re-checked by backend dependency.

### 14.3 Password Seeding

Development:

1. If `AUTH_ADMIN_USERNAME` and `AUTH_ADMIN_PASSWORD` are missing, create:

```text
username: admin
password: admin123
role: admin
```

2. If `AUTH_RESPONDER_USERNAME` and `AUTH_RESPONDER_PASSWORD` are missing, create:

```text
username: responder
password: responder123
role: responder
```

Production:

1. Startup must fail if admin credentials are missing.
2. Default passwords must not be accepted in production.

### 14.4 Security Controls

| Control | Requirement |
|---|---|
| CORS | Only origins in `CORS_ORIGINS` allowed. |
| Rate limiting | Login limited to 5 failed attempts per IP per 60 seconds. |
| SQL injection | Prevented by SQLAlchemy ORM and parameterized queries. |
| Input validation | All requests validated by Pydantic. |
| Secret handling | `SECRET_KEY` never sent to frontend. |
| Token storage | Frontend stores token in localStorage for demo; production recommendation is httpOnly cookie. |
| Audit logging | All mutating actions logged in `audit_logs`. |
| File uploads | Not supported. |
| External calls | Only OpenStreetMap tiles and optional Open-Meteo if enabled. |

---

## 15. Error Handling and Edge Cases

### 15.1 Global Error Handling

Backend must catch:

1. Pydantic validation errors and return 422.
2. HTTPException and return its status/code.
3. Unexpected exceptions and return 500.

Unexpected exception response:

```json
{
  "error": {
    "code": "INTERNAL",
    "message": "An unexpected error occurred.",
    "details": {}
  }
}
```

Logs must include stack trace server-side.

### 15.2 Edge Cases

| Case | Required Behavior |
|---|---|
| No active scenario | Endpoints requiring scenario return 422 `NO_ACTIVE_SCENARIO`. |
| Origin outside graph | Return 422 `ORIGIN_NOT_SNAPPABLE`. |
| Shelter not snapped | Mark `routable=false`; exclude from auto selection. |
| All shelters closed | Return 422 `NO_ROUTABLE_SHELTERS`. |
| All roads blocked | Attempt penalized path; if none, return 422 `ROUTE_NOT_FOUND`. |
| Duplicate blocked report | Return existing active report, HTTP 200. |
| Resolve already resolved report | Return HTTP 200 with resolved status. |
| Scenario rainfall zero | Risk remains low unless blocked. |
| Model missing | Use fallback propensity. |
| Map GeoJSON too large | Frontend renders only roads, shelters, reports; no historical snapshots. |
| Token expired | Frontend clears token and shows login prompt. |

---

## 16. Real-Time/Background Processing Requirements

### 16.1 MVP Real-Time Strategy

No WebSockets.

Frontend polls:

```text
GET /api/map/geojson
GET /api/reports/active
```

every 30 seconds.

### 16.2 Synchronous Processing

Risk recomputation is synchronous for MVP.

Trigger points:

1. Scenario activation.
2. Blocked report creation.
3. Blocked report resolution.
4. Admin forced recompute.

### 16.3 Background Jobs

No background worker is required for MVP.

Optional production design:

1. Use APScheduler or Celery.
2. Refresh live rainfall every 10 minutes.
3. Recompute risk snapshots asynchronously.

---

## 17. Environment Variables and Configuration

### 17.1 `.env.example`

```env
APP_ENV=development
SECRET_KEY=change-me
DATABASE_URL=sqlite:///./safedata.db
CORS_ORIGINS=http://localhost:5173

DEFAULT_LAT=12.981
DEFAULT_LON=80.213
AREA_NAME=West Velachery, Chennai

MODEL_PATH=models/risk_model.joblib
SNAP_RADIUS_METERS=250
BLOCKED_PENALTY=1000000
RISK_ML_WEIGHT=0.45
RISK_RULE_WEIGHT=0.55
MAX_ROUTE_ALTERNATIVES=3

AUTH_ADMIN_USERNAME=
AUTH_ADMIN_PASSWORD=
AUTH_RESPONDER_USERNAME=
AUTH_RESPONDER_PASSWORD=

SEED_PLACEHOLDER_SHELTERS=false
OPEN_METEO_ENABLED=false
OPEN_METEO_LAT=12.981
OPEN_METEO_LON=80.213
```

### 17.2 Required in Production

```env
APP_ENV=production
SECRET_KEY=<strong-random-value>
CORS_ORIGINS=<production-origin>
AUTH_ADMIN_USERNAME=<non-default>
AUTH_ADMIN_PASSWORD=<strong-password>
```

---

## 18. Complete Setup, Development, and Deployment Instructions

### 18.1 Prerequisites

| Tool | Version |
|---|---|
| Python | 3.11+ |
| Node.js | 20+ |
| npm | 10+ |
| Git | latest |

### 18.2 Repository Setup

```bash
git clone <repo-url>
cd safetoute-velachery
```

### 18.3 Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create environment file from repository root:

```bash
cp .env.example .env
```

### 18.4 Data Preparation

1. Open Overpass Turbo.
2. Use bbox:

```text
south=12.965
west=80.195
north=12.995
east=80.235
```

3. Run query:

```overpassql
[out:json][timeout:180];
(
  way["highway"](12.965,80.195,12.995,80.235);
);
out geom;
```

4. Export result as GeoJSON.
5. Save as:

```text
data/velachery/roads.geojson
```

6. Create `data/velachery/shelters.json` using GCC relief centre data.

Shelter JSON schema:

```json
[
  {
    "external_id": "GCC-RC-001",
    "name": "Real shelter name",
    "type": "school",
    "lat": 12.981,
    "lon": 80.213,
    "capacity_assumed": 200,
    "occupancy_assumed": 0,
    "elevation_risk": "low",
    "accessible": true,
    "medical_support": false,
    "water_available": true,
    "status": "open",
    "source": "OpenCity GCC Relief Centres",
    "notes": ""
  }
]
```

7. Create `data/velachery/scenarios.json`:

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
    "description": "80 mm in 24 hours",
    "rainfall_mm_24h": 80,
    "rainfall_mm_1h": 15,
    "source": "manual",
    "is_active": false
  },
  {
    "name": "Michaung Replay",
    "description": "Approximately 150 mm in 24 hours",
    "rainfall_mm_24h": 150,
    "rainfall_mm_1h": 30,
    "source": "Michaung 2023 benchmark",
    "is_active": false
  },
  {
    "name": "Extreme Event",
    "description": "250 mm in 24 hours",
    "rainfall_mm_24h": 250,
    "rainfall_mm_1h": 50,
    "source": "manual",
    "is_active": false
  }
]
```

### 18.5 Database Initialization

From `backend` directory:

```bash
python -m app.scripts.init_db
python -m app.scripts.seed_users
python -m app.scripts.import_data \
  --roads ../data/velachery/roads.geojson \
  --shelters ../data/velachery/shelters.json \
  --scenarios ../data/velachery/scenarios.json
```

### 18.6 Train AI Model

From `backend` directory:

```bash
python -m app.ai.train_model
```

Expected output:

```text
Model saved to models/risk_model.joblib
Meta saved to models/model_meta.json
Updated ml_static_propensity for N segments
```

### 18.7 Run Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Backend available at:

```text
http://localhost:8000
```

### 18.8 Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend available at:

```text
http://localhost:5173
```

### 18.9 Production Build

Build frontend:

```bash
cd frontend
npm run build
```

FastAPI must serve `frontend/dist` if it exists.

Run backend:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 18.10 Deployment Recommendation

Use one service for MVP:

1. Build frontend.
2. Deploy FastAPI app.
3. FastAPI serves static frontend.
4. Use managed persistent disk or repo-included SQLite for demo.

Production deployment target is an OPEN DECISION.

---

## 19. Testing Strategy and Acceptance Criteria

### 19.1 Backend Unit Tests

Run:

```bash
cd backend
pytest -q
```

Required tests:

| Test | Acceptance Criteria |
|---|---|
| test_health | Returns status ok and counts. |
| test_login_success | Valid credentials return JWT. |
| test_login_failure | Invalid credentials return 401. |
| test_risk_range | All computed risk scores are between 0 and 1. |
| test_risk_level_mapping | Risk level matches thresholds. |
| test_blocked_report_sets_critical | Active blocked report sets risk_score 1.0. |
| test_route_origin_snap | Origin within radius snaps to node. |
| test_route_origin_fail | Origin outside radius returns `ORIGIN_NOT_SNAPPABLE`. |
| test_route_safest_and_shortest | Route response includes both route types. |
| test_blocked_segment_avoided | If alternate path exists, safest route avoids blocked segment. |
| test_no_route | Disconnected graph returns `ROUTE_NOT_FOUND`. |
| test_shelter_suitability | Suitability is between 0 and 1. |

### 19.2 API Integration Tests

Use FastAPI TestClient.

Required scenarios:

1. Public user can fetch map GeoJSON.
2. Public user can create route request.
3. Public user cannot create blocked report.
4. Responder can create blocked report.
5. Admin can activate scenario.
6. Responder cannot create scenario.

### 19.3 Frontend Manual Tests

| Test | Pass Condition |
|---|---|
| Load dashboard | Map renders within 4 seconds. |
| Change scenario | Road colors update. |
| Set origin | Origin marker appears. |
| Plan route | Safest and shortest routes render. |
| Login | Responder sees report controls. |
| Block road | Segment turns dark red dashed. |
| Replan route | Route avoids blocked segment if possible. |
| Resolve report | Segment risk returns to computed value. |
| Network failure | UI shows retryable error. |

### 19.4 Feature Acceptance Criteria

#### F1 Authentication

Pass if:

1. Login with valid credentials returns token.
2. Invalid credentials return 401.
3. Protected endpoint without token returns 401.
4. Responder cannot access admin endpoint.

#### F2 Map Dashboard

Pass if:

1. Roads render from GeoJSON.
2. Shelters render.
3. Risk colors match risk_level.
4. Blocked segments use dashed dark red.
5. Map polling updates data every 30 seconds.

#### F3 Scenario Management

Pass if:

1. Four scenarios are seeded.
2. Public can list scenarios.
3. Responder can activate scenario.
4. Activation recomputes risk.
5. Map reflects selected scenario.

#### F4 AI Road Risk Engine

Pass if:

1. Risk scores are between 0 and 1.
2. Risk levels match thresholds.
3. Blocked segments have risk_score 1.0.
4. Model fallback works when model file missing.
5. Validation summary returns risk distribution.

#### F5 Shelter Directory

Pass if:

1. Shelters load from JSON.
2. Suitability is between 0 and 1.
3. Closed shelters excluded from auto destination.
4. Non-routable shelters are marked `routable=false`.

#### F6 Route Planning

Pass if:

1. Origin snaps to nearest node.
2. Safest and shortest routes returned.
3. Auto destination selects open shelter.
4. Route persists in database.
5. Route geometry renders on map.

#### F7 Route Explanation

Pass if:

1. Additional time computed correctly.
2. High-risk avoided count computed correctly.
3. Shelter reasons include capacity and elevation risk.
4. Warnings shown if route uses blocked segments.

#### F8 Blocked Road Reporting

Pass if:

1. Responder can create report.
2. Public cannot create report.
3. Segment becomes blocked.
4. Duplicate active report returns existing report.
5. Audit log written.

#### F9 Dynamic Re-routing

Pass if:

1. After blocked report, new route avoids blocked segment when alternate exists.
2. If no alternate exists, response includes warning and blocked_segments_encountered > 0.
3. Resolving report allows route to use segment again.

#### F10 Data Import

Pass if:

1. Roads GeoJSON imports without error.
2. Nodes and segments are created.
3. Shelters snap to nodes.
4. Scenarios upsert by name.
5. Users seeded according to environment.

#### F11 Health and Validation

Pass if:

1. Health endpoint returns model and DB status.
2. Validation summary returns risk distribution.
3. Top high-risk segments list is non-empty when scenario has rainfall.

---

## 20. Implementation Order with Dependencies

### Phase 1: Scaffold

1. Create repository.
2. Create backend and frontend folders.
3. Add `.env.example`.
4. Add requirements and package files.

Dependencies: none.

### Phase 2: Backend Core

1. Implement `config.py`.
2. Implement `database.py`.
3. Implement `models.py`.
4. Implement `schemas.py`.
5. Implement health endpoint.

Dependencies: Phase 1.

### Phase 3: Authentication

1. Implement password hashing.
2. Implement JWT.
3. Implement login endpoint.
4. Implement role dependencies.
5. Seed users.

Dependencies: Phase 2.

### Phase 4: Data Import

1. Implement geo math utilities.
2. Implement import service.
3. Implement init_db and import_data scripts.
4. Import roads, shelters, scenarios.

Dependencies: Phase 2.

### Phase 5: AI Risk Engine

1. Implement feature builder.
2. Implement training script.
3. Implement prediction fallback.
4. Implement risk service.
5. Implement risk snapshots.

Dependencies: Phase 4.

### Phase 6: Map API

1. Implement `GET /api/meta/area`.
2. Implement `GET /api/scenarios`.
3. Implement `GET /api/map/geojson`.
4. Implement scenario activation.

Dependencies: Phase 5.

### Phase 7: Routing

1. Implement graph service.
2. Implement Dijkstra.
3. Implement shelter scoring.
4. Implement route endpoint.
5. Implement explanation service.

Dependencies: Phase 5.

### Phase 8: Reports

1. Implement blocked report endpoint.
2. Implement resolve endpoint.
3. Implement active reports endpoint.
4. Connect reports to risk updates.

Dependencies: Phase 5.

### Phase 9: Frontend Core

1. Setup Vite React TypeScript.
2. Implement API client.
3. Implement Zustand store.
4. Implement DashboardPage.
5. Implement MapPanel.

Dependencies: Phase 6.

### Phase 10: Frontend Routing UI

1. Implement OriginPicker.
2. ShelterPanel.
3. RoutePanel.
4. ExplanationPanel.

Dependencies: Phase 7.

### Phase 11: Frontend Reports UI

1. Implement LoginButton.
2. LoginPage.
3. ReportBlockageModal.
4. ActiveReports list.

Dependencies: Phase 8.

### Phase 12: Testing and Demo Polish

1. Backend tests.
2. Manual frontend tests.
3. Demo data freeze.
4. Demo script rehearsal.

Dependencies: Phases 9–11.

---

## 21. MVP vs Optional Features

### MVP

Must be complete before presentation:

| Feature | Status |
|---|---|
| West Velachery road network | Required |
| Four rainfall scenarios | Required |
| Road risk coloring | Required |
| Shelter list and scoring | Required |
| Safest route planning | Required |
| Shortest route comparison | Required |
| Blocked-road reporting | Required |
| Dynamic rerouting | Required |
| Explanation panel | Required |
| Login for responder/admin | Required |
| Demo fallback data | Required |

### Optional

Only after MVP passes:

| Feature | Condition |
|---|---|
| Historical backtest panel | Only if routing and risk are stable. |
| Live Open-Meteo refresh | Only if demo internet is reliable. |
| SMS/WhatsApp mock | Only if UI is polished. |
| Multi-responder dashboard | Only if time remains. |
| Tamil/English toggle | Only if demo script is stable. |

---

## 22. Demo Workflow and Hackathon-Critical Features

### 22.1 Demo Preconditions

1. Backend running.
2. Frontend built or dev server running.
3. Database seeded.
4. Model trained or fallback active.
5. Demo scenario `Michaung Replay` available.
6. Backup JSON snapshot available if API fails.

### 22.2 Two-Minute Demo Script

1. Open dashboard.

   Say:

   > “This is an AI evacuation decision-support system for West Velachery, Chennai.”

2. Show normal scenario.

   Say:

   > “Under normal rainfall, most roads are low risk.”

3. Switch to Michaung Replay.

   Say:

   > “We simulate approximately 150 mm rainfall in 24 hours.”

4. Point to red segments.

   Say:

   > “The AI flags low-lying flood-prone roads, especially around AGS Colony, Baby Nagar, and Vijayanagar.”

5. Click origin in a red zone.

6. Click Plan Safest Route.

7. Show two routes.

   Say:

   > “The shortest route passes through high-risk segments. The safest route avoids them and reaches a shelter.”

8. Show explanation panel.

   Say:

   > “The safest route adds a few minutes but avoids high-risk flood segments.”

9. Login as responder.

10. Mark one road blocked.

11. Replan route.

   Say:

   > “When a field report marks this road blocked, the system immediately reroutes.”

12. Close:

   > “This converts raw rainfall and road data into safer evacuation decisions.”

### 22.3 Hackathon-Critical Features

These must never fail during demo:

1. Map load.
2. Scenario switch.
3. Route request.
4. Blocked-road simulation.
5. Explanation panel.
6. Fallback data if network fails.

---

## 23. Performance, Scalability, and Production Considerations

### 23.1 MVP Performance Requirements

| Operation | Target |
|---|---|
| Map GeoJSON active scenario | < 800 ms |
| Route calculation with <= 1000 segments | < 2 seconds |
| Shelter list | < 300 ms |
| Login | < 500 ms |
| Frontend initial render | < 4 seconds |

### 23.2 Optimization Rules

1. Build graph adjacency once at startup and cache it.
2. Cache risk results for active scenario in memory.
3. Use SQLite indices on nodes and edges.
4. Limit GeoJSON response to current scenario only.
5. Simplify road geometries if total segments exceed 1500.
6. Poll only every 30 seconds.

### 23.3 Production Scaling

If moving beyond MVP:

1. Replace SQLite with PostgreSQL + PostGIS.
2. Store road geometry as PostGIS geometry.
3. Use OSRM or Valhalla for large-scale routing.
4. Use Redis for risk cache and rate limiting.
5. Use Celery or Cloud Tasks for background risk recomputation.
6. Use official shelter feeds and live field reporting.
7. Add OAuth2 or government SSO.
8. Add HTTPS, monitoring, alerting, and audit retention.
9. Add map tile server or vector tiles.
10. Add automated data validation for OSM updates.

---

## 24. Known Assumptions, Constraints, and Risks

### 24.1 Assumptions

| ID | Assumption |
|---|---|
| A1 | All roads are treated as bidirectional in MVP. |
| A2 | OSM road network is sufficiently accurate for demo. |
| A3 | Shelter capacities are assumed values unless sourced from GCC. |
| A4 | Blocked-road reports are simulated or responder-entered, not live official feeds. |
| A5 | Rainfall scenarios are sufficient for demo without live weather. |
| A6 | The system is decision support, not an official life-safety navigation system. |
| A7 | Elevation risk is proxied by GCC hazard categories, low_lying_prior, and drainage_proxy. |
| A8 | One neighborhood scope is sufficient to demonstrate real-world relevance. |

### 24.2 Constraints

| ID | Constraint |
|---|---|
| C1 | Hackathon duration is 30 hours. |
| C2 | Team is strong in web development but new to AI. |
| C3 | No guaranteed live government data feed. |
| C4 | No guaranteed field validation during hackathon. |
| C5 | Demo internet may be unreliable. |

### 24.3 Risks

| Risk | Severity | Mitigation |
|---|---|---|
| OSM export too large | High | Restrict bbox and simplify geometry. |
| Shelter data unavailable | High | Use GCC relief centre dataset placeholders and label assumptions. |
| Routing too slow | Medium | Limit graph size and cache adjacency. |
| Risk model appears too simple | Medium | Explain hybrid AI scoring and measurable route risk reduction. |
| Map tiles fail | Medium | Vector layers still render; use backup screenshot/video. |
| API fails live | High | Record backup demo video and keep frozen JSON snapshot. |
| Judges ask for live data | Medium | Clearly state MVP uses documented historical scenarios and simulated reports. |

---

## OPEN DECISIONS

The following items are not yet finalized and must be resolved before final demo data freeze:

| ID | Decision | Owner | Deadline |
|---|---|---|---|
| OD-1 | Final list of real GCC shelters inside West Velachery. | Data lead | Before data import freeze |
| OD-2 | Final assumed capacity and occupancy values for each shelter. | Team lead | Before demo freeze |
| OD-3 | Final OSM bbox and road simplification level. | Backend lead | Phase 4 |
| OD-4 | Whether to include one-way road constraints. | Team lead | Post-MVP only |
| OD-5 | Whether live Open-Meteo rainfall is used in demo. | Team lead | Phase 12 |
| OD-6 | Final deployment target. | Team lead | Phase 12 |
| OD-7 | Whether to replace hazard proxy with DEM elevation data. | AI lead | Post-MVP only |
| OD-8 | Whether UI needs Tamil labels for demo. | Pitch lead | Post-MVP only |
| OD-9 | Whether official emergency-response disclaimer is required on every screen. | Team lead | Phase 12 |