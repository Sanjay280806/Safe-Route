import type { Health, RiskLevel, User, ValidationSummary } from "../types";

interface AiRiskPanelProps {
  health: Health | null;
  summary: ValidationSummary | null;
  user: User | null;
  recomputing: boolean;
  onRecompute: () => void;
}

const levels: RiskLevel[] = ["low", "moderate", "high", "critical"];

export function AiRiskPanel({ health, summary, user, recomputing, onRecompute }: AiRiskPanelProps) {
  const modelLoaded = summary?.model_loaded ?? health?.model_loaded ?? false;
  const distribution = summary?.risk_distribution;

  return (
    <section className="panel ai-risk-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Risk scoring</p>
          <h2>Road risk model</h2>
        </div>
        <span className={`live-pill ${modelLoaded ? "" : "fallback"}`}>
          {modelLoaded ? "Model loaded" : "Seeded fallback"}
        </span>
      </div>

      <p className="ai-risk-copy">
        {modelLoaded
          ? `${summary?.model_type ?? "Risk model"} scores the current local scenario.`
          : "Local placeholder road-risk values are used until a trained model is available."}
      </p>

      <div className="ai-risk-distribution" aria-label="Road risk distribution">
        {levels.map((level) => (
          <span className={`ai-risk-chip ${level}`} key={level}>
            <strong>{distribution?.[level] ?? 0}</strong>
            <small>{level}</small>
          </span>
        ))}
      </div>

      {summary?.top_high_risk_segments.length ? (
        <ul className="ai-top-segments" aria-label="Highest risk roads">
          {summary.top_high_risk_segments.slice(0, 3).map((segment) => (
            <li key={segment.segment_id}>
              <strong>{segment.name}</strong>
              <small>{Math.round(segment.risk_score * 100)}% risk</small>
            </li>
          ))}
        </ul>
      ) : (
        <p className="panel-empty">Risk summary is unavailable.</p>
      )}

      {user?.role === "admin" ? (
        <button className="primary-button ai-recompute" type="button" disabled={recomputing} onClick={onRecompute}>
          {recomputing ? "Recomputing…" : "Recompute road risk"}
        </button>
      ) : null}
    </section>
  );
}
