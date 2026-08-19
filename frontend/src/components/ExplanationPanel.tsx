import type { RouteResponse } from "../types";

export function ExplanationPanel({ routeResponse }: { routeResponse: RouteResponse | null }) {
  if (!routeResponse) {
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
      <div className="explanation-metrics">
        <span><strong>+{explanation.safe_route_adds_min.toFixed(1)} min</strong><small>travel time</small></span>
        <span><strong>{explanation.high_risk_segments_avoided}</strong><small>high-risk roads avoided</small></span>
        <span><strong>{explanation.blocked_segments_avoided}</strong><small>blocked roads avoided</small></span>
      </div>
    </section>
  );
}
