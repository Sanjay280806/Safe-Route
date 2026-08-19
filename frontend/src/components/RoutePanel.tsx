import type { Destination, LatLng, RouteMode, RouteResponse } from "../types";

interface RoutePanelProps {
  origin: LatLng | null;
  destination: Destination | null;
  routeMode: RouteMode;
  routeResponse: RouteResponse | null;
  loading: boolean;
  mapMode: "pan" | "set_origin" | "set_destination" | "report_road";
  onRouteModeChange: (mode: RouteMode) => void;
  onMapModeChange: (mode: "set_origin" | "set_destination") => void;
  onRequestRoute: () => void;
  onClear: () => void;
}

function pointLabel(point: LatLng | null, fallback: string): string {
  return point ? `${point.lat.toFixed(4)}, ${point.lon.toFixed(4)}` : fallback;
}

function destinationLabel(destination: Destination | null): string {
  if (!destination) return "Choose a place or map point";
  return destination.type === "poi" ? destination.poi.name : `${destination.location.lat.toFixed(4)}, ${destination.location.lon.toFixed(4)}`;
}

export function RoutePanel({
  origin,
  destination,
  routeMode,
  routeResponse,
  loading,
  mapMode,
  onRouteModeChange,
  onMapModeChange,
  onRequestRoute,
  onClear,
}: RoutePanelProps) {
  const visibleRoutes = routeResponse?.routes.filter((route) => routeMode === "compare" || route.route_type === routeMode) ?? [];

  return (
    <section className="panel route-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Flood-aware routing</p>
          <h2>Plan a route</h2>
        </div>
        {routeResponse ? <span className="live-pill">Route ready</span> : null}
      </div>

      <div className="route-points">
        <div className="route-point">
          <span className="route-dot origin" />
          <div><small>From</small><strong>{pointLabel(origin, "Set an origin")}</strong></div>
          <button type="button" onClick={() => onMapModeChange("set_origin")}>Set on map</button>
        </div>
        <div className="route-connector" />
        <div className="route-point">
          <span className="route-dot destination" />
          <div><small>To</small><strong>{destinationLabel(destination)}</strong></div>
          <button type="button" onClick={() => onMapModeChange("set_destination")}>Set on map</button>
        </div>
      </div>

      {mapMode === "set_origin" || mapMode === "set_destination" ? (
        <p className="map-mode-hint">Click the map to set your {mapMode === "set_origin" ? "origin" : "destination"}.</p>
      ) : null}

      <fieldset className="route-mode-selector">
        <legend>Route preference</legend>
        {(["safe", "short", "compare"] as RouteMode[]).map((mode) => (
          <button
            type="button"
            key={mode}
            className={routeMode === mode ? "active" : ""}
            onClick={() => onRouteModeChange(mode)}
          >
            {mode === "safe" ? "Safest" : mode === "short" ? "Shortest" : "Compare"}
          </button>
        ))}
      </fieldset>

      <div className="route-actions">
        <button type="button" className="primary-button" disabled={!origin || !destination || loading} onClick={onRequestRoute}>
          {loading ? "Finding route…" : "Get route"}
        </button>
        <button type="button" className="secondary-button" onClick={onClear}>Clear</button>
      </div>

      {visibleRoutes.length > 0 ? (
        <div className="route-summaries">
          {visibleRoutes.map((route) => (
            <article className={`route-summary ${route.route_type}`} key={route.route_type}>
              <span className="route-line-swatch" />
              <div>
                <strong>{route.route_type === "safe" ? "Safe route" : "Short route"}</strong>
                <p>{(route.distance_m / 1000).toFixed(2)} km · {route.duration_min.toFixed(1)} min</p>
              </div>
              <span className={`risk-score ${route.avg_risk_score >= 0.5 ? "high" : "low"}`}>{Math.round(route.avg_risk_score * 100)}% risk</span>
            </article>
          ))}
        </div>
      ) : null}
    </section>
  );
}
