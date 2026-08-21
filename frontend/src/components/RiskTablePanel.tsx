import type { RainfallStatus, RoadFeature } from "../types";

export function RiskTablePanel({ roads, rainfall }: { roads: RoadFeature[]; rainfall: RainfallStatus | null }) {
  return (
    <section className="panel risk-table-panel">
      <div className="panel-heading"><div><p className="eyebrow">Local AI prediction</p><h2>Road risk table</h2></div><span className="live-pill">{rainfall?.rainfall_mm_24h ?? "–"} mm / 24h</span></div>
      <div className="risk-table-wrap"><table><thead><tr><th>Road</th><th>Rain</th><th>Block risk</th><th>Status</th></tr></thead><tbody>{roads.map((road) => <tr key={road.properties.segment_id}><td>{road.properties.name}</td><td>{rainfall?.rainfall_mm_1h ?? "–"} mm/h</td><td><span className={`road-risk-value ${road.properties.current_risk_level}`}>{Math.round(road.properties.current_risk_score * 100)}%</span></td><td>{road.properties.blocked ? "Blocked" : "Clear"}</td></tr>)}</tbody></table></div>
    </section>
  );
}
