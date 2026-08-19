# AI Routing Implementation Notes

Implemented only the benchmark AI risk and routing layer.

## Added

- Risk model training script: `backend/app/ai/train_model.py`
- Risk scoring service: `backend/app/services/risk_service.py`
- Time-to-risk service: `backend/app/services/time_risk_service.py`
- Graph service: `backend/app/services/graph_service.py`
- Routing service: `backend/app/services/routing_service.py`
- Warning service: `backend/app/services/warning_service.py`
- Explanation service: `backend/app/services/explanation_service.py`
- Route APIs:
  - `POST /api/routes`
  - `POST /api/routes/re-route`

## Required Existing Database Fields

No model or migration files were modified. The services expect these fields when real SQLite tables exist:

- `nodes`: `id`, `lat`, `lon`
- `road_segments`: `id`, `from_node_id`, `to_node_id`, `length_m`, `geometry_json`, `name`, `road_type`, `is_underpass`, `low_lying_prior`, `proximity_to_water`, `drainage_proxy`, `historical_flood_count`, `ml_static_propensity`, `blocked`, `flood_status`
- `scenarios`: `id`, `name`, `rainfall_mm_24h`, `rainfall_mm_1h`, `is_active`
- `pois`: `id`, `name`, `category`, `lat`, `lon`, `nearest_node_id`, `status`

`route_requests` is optional for this benchmark slice. If present, it should allow a default insert or the repository can be adapted to the final route request schema.

## Placeholder Data

`data/mock/*` is placeholder-only demo fallback data and is not official civic, hospital, shelter, or road data.

