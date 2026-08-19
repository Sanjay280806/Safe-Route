import type { RouteWarning } from "../types";

export function WarningsPanel({ warnings }: { warnings: RouteWarning[] }) {
  return (
    <section className="panel warnings-panel">
      <div className="panel-heading">
        <div><p className="eyebrow">AI time-to-risk</p><h2>Route warnings</h2></div>
        <span className={`warning-count ${warnings.length ? "has-warnings" : ""}`}>{warnings.length}</span>
      </div>
      {warnings.length === 0 ? <p className="safe-message">No time-to-risk warnings on the selected route.</p> : null}
      {warnings.map((warning, index) => (
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
