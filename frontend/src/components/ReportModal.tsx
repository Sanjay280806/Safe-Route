import { useState } from "react";
import type { RoadFeature } from "../types";

interface ReportModalProps {
  road: RoadFeature | null;
  submitting: boolean;
  source?: string;
  onClose: () => void;
  onSubmit: (payload: { source: string; note: string; flood_status: string }) => void;
}

export function ReportModal({ road, submitting, source = "field_official", onClose, onSubmit }: ReportModalProps) {
  const [floodStatus, setFloodStatus] = useState("confirmed_flooded");
  const [note, setNote] = useState("");

  if (!road) return null;

  const submit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit({ source, note: note.trim() || "Field observation submitted from dashboard", flood_status: floodStatus });
  };

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <section className="modal-card" role="dialog" aria-modal="true" aria-labelledby="report-title" onMouseDown={(event) => event.stopPropagation()}>
        <div className="modal-heading">
          <div><p className="eyebrow">Field reporter</p><h2 id="report-title">Report road condition</h2></div>
          <button type="button" className="icon-button" aria-label="Close report modal" onClick={onClose}>×</button>
        </div>
        <div className="report-road-summary">
          <span className="road-strip" />
          <div><strong>{road.properties.name}</strong><small>Segment #{road.properties.segment_id} · current model risk: {road.properties.current_risk_level}</small></div>
        </div>
        <form onSubmit={submit}>
          <label className="field-label" htmlFor="flood-status">Observed condition</label>
          <select id="flood-status" value={floodStatus} onChange={(event) => setFloodStatus(event.target.value)}>
            <option value="confirmed_flooded">Confirmed flooded / impassable</option>
            <option value="blocked">Blocked road</option>
            <option value="likely_flooded">Flooding likely</option>
          </select>
          <label className="field-label" htmlFor="report-note">Field note</label>
          <textarea id="report-note" rows={4} value={note} onChange={(event) => setNote(event.target.value)} placeholder="Describe the waterlogging or obstruction…" />
          <p className="form-help">Reports are scored for credibility. Confirmed field-official reports immediately affect routing.</p>
          <div className="modal-actions">
            <button type="button" className="secondary-button" onClick={onClose}>Cancel</button>
            <button type="submit" className="primary-button" disabled={submitting}>{submitting ? "Submitting…" : "Submit report"}</button>
          </div>
        </form>
      </section>
    </div>
  );
}
