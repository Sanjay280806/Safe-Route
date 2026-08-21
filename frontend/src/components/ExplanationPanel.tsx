import type { Route, RouteResponse } from "../types";

export function ExplanationPanel({ routeResponse, route, modelLoaded = false }: { routeResponse: RouteResponse | null; route: Route | null; modelLoaded?: boolean }) {
  if (!routeResponse || !route) {
    return (
      <section className="panel explanation-panel empty-explanation">
        <p className="eyebrow">Why this route?</p>
        <h2>Risk-aware guidance</h2>
        <p>Choose a destination and request a route to see the routing explanation.</p>
      </section>
    );
  }

  const { explanation } = routeResponse;
  return (
    <section className="panel explanation-panel">
      <p className="eyebrow">Why the safe route?</p>
      <h2>Flood exposure reduced</h2>
      <p className="explanation-copy">{explanation.summary}</p>
      <p className="explanation-ai-source">
        {modelLoaded
          ? "Scored with IsolationForest flood propensity plus rainfall and blocked-road penalties."
          : "Scored with stored segment flood propensity plus rainfall and blocked-road penalties."}
      </p>
      <p className="route-analysis-detail">Selected route: {(route.distance_m / 1000).toFixed(2)} km · {route.duration_min.toFixed(1)} min · {Math.round(route.avg_risk_score * 100)}% average flood risk</p>
      <div className="explanation-metrics">
        <span><strong>+{explanation.safe_route_adds_min.toFixed(1)} min</strong><small>travel time</small></span>
        <span><strong>{explanation.high_risk_segments_avoided}</strong><small>high-risk roads avoided</small></span>
        <span><strong>{explanation.blocked_segments_avoided}</strong><small>blocked roads avoided</small></span>
      </div>
    </section>
  );
}
