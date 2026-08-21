import type { Route, RouteWarning } from "../types";

interface WarningsPanelProps {
  route: Route | null;
  warnings: RouteWarning[];
  loading?: boolean;
}

export function WarningsPanel({ route, warnings, loading = false }: WarningsPanelProps) {
  const hasRoute = Boolean(route);
  const warningCount = hasRoute ? warnings.length : 0;

  return (
    <section className="panel warnings-panel">
      <div className="panel-heading">
        <div><p className="eyebrow">AI time-to-risk</p><h2>Route warnings</h2></div>
        <span className={`warning-count ${warningCount ? "has-warnings" : ""}`}>{hasRoute ? warningCount : "–"}</span>
      </div>
      {!hasRoute && !loading ? <p className="panel-empty">Select a destination and get a route to assess time-to-risk.</p> : null}
      {loading ? <p className="panel-empty">Assessing time-to-risk on the selected route…</p> : null}
      {route && !loading ? <p className="route-analysis-detail">{(route.distance_m / 1000).toFixed(2)} km · {route.duration_min.toFixed(1)} min · {Math.round(route.avg_risk_score * 100)}% average flood risk</p> : null}
      {hasRoute && warnings.length === 0 && !loading ? <p className="safe-message">No time-to-risk warnings on this optimal route.</p> : null}
      {hasRoute && warnings.map((warning, index) => (
        <article className="warning-card" key={`${warning.segment_id ?? index}-${warning.road_name}`}>
          <span className="warning-symbol" aria-hidden="true">!</span>
          <div>
            <strong>{warning.road_name}</strong>
            <p>{warning.message}</p>
            {warning.eta_to_segment_min !== undefined && warning.predicted_time_to_high_risk_min !== undefined ? (
              <small>ETA {warning.eta_to_segment_min} min · risk predicted in {warning.predicted_time_to_high_risk_min} min</small>
            ) : null}
          </div>
        </article>
      ))}
    </section>
  );
}
