import type { Health, User, ValidationSummary } from "../types";

interface AiRiskPanelProps {
  health: Health | null;
  summary: ValidationSummary | null;
  user: User | null;
  recomputing: boolean;
  onRecompute: () => void;
}

export function AiRiskPanel({ health, summary, user, recomputing, onRecompute }: AiRiskPanelProps) {
  const modelLoaded = summary?.model_loaded ?? health?.model_loaded ?? false;
  const distribution = summary?.risk_distribution;
  const topSegments = summary?.top_high_risk_segments ?? [];

  return (
    <section className="panel ai-risk-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">AI flood risk engine</p>
          <h2>{modelLoaded ? "IsolationForest active" : "Heuristic fallback"}</h2>
        </div>
        <span className={`live-pill ${modelLoaded ? "" : "fallback"}`}>
          {modelLoaded ? "Model loaded" : "No trained model"}
        </span>
      </div>
      <p className="ai-risk-copy">
        {modelLoaded
          ? "Road flood propensity is scored from the trained IsolationForest model, then combined with the active rainfall scenario for routing."
          : "Fewer than 30 road segments are available, so static propensity uses stored segment features instead of IsolationForest. Rainfall and blocked-road penalties still drive safest-route scoring."}
      </p>
      {distribution ? (
        <div className="ai-risk-distribution">
          {(["low", "moderate", "high", "critical"] as const).map((level) => (
            <span key={level} className={`ai-risk-chip ${level}`}>
              <strong>{distribution[level] ?? 0}</strong>
              <small>{level}</small>
            </span>
          ))}
        </div>
      ) : null}
      {topSegments.length > 0 ? (
        <ul className="ai-top-segments">
          {topSegments.slice(0, 3).map((segment) => (
            <li key={segment.segment_id}>
              <strong>{segment.name}</strong>
              <small>{Math.round(segment.risk_score * 100)}% · {segment.risk_level}</small>
            </li>
          ))}
        </ul>
      ) : null}
      {user?.role === "admin" ? (
        <button type="button" className="secondary-button ai-recompute" disabled={recomputing} onClick={onRecompute}>
          {recomputing ? "Recomputing…" : "Recompute risk"}
        </button>
      ) : null}
    </section>
  );
}
