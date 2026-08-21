import { useState } from "react";
import type { FieldMessage, RoadFeature, User } from "../types";

interface MessagePanelProps {
  user: User | null;
  messages: FieldMessage[];
  roads: RoadFeature[];
  busy: boolean;
  onSend: (payload: { sender_name: string; category: string; message: string; segment_id?: number }) => void;
  onStatus: (message: FieldMessage, status: FieldMessage["status"]) => void;
  onManageRoad: (segmentId: number) => void;
}

export function MessagePanel({ user, messages, roads, busy, onSend, onStatus, onManageRoad }: MessagePanelProps) {
  const [name, setName] = useState("");
  const [category, setCategory] = useState("road_blockage");
  const [message, setMessage] = useState("");
  const [segmentId, setSegmentId] = useState("");
  const isOperator = user?.role === "reporter" || user?.role === "admin";

  if (isOperator) {
    return (
      <section className="panel message-panel">
        <div className="panel-heading"><div><p className="eyebrow">Resident messages</p><h2>Control room inbox</h2></div><span className="count-pill danger">{messages.filter((item) => item.status !== "resolved").length}</span></div>
        {messages.length === 0 ? <p className="safe-message">No resident messages awaiting action.</p> : null}
        <div className="message-list">
          {messages.map((item) => (
            <article className="message-row" key={item.id}>
              <div><strong>{item.category.replace(/_/g, " ")}</strong><small>{item.sender_name} · {item.sender_role}</small><p>{item.message}</p>{item.road_name ? <small>{item.road_name}</small> : null}</div>
              <div className="message-actions">
                <select aria-label="Message status" value={item.status} disabled={busy} onChange={(event) => onStatus(item, event.target.value as FieldMessage["status"])}><option value="open">Open</option><option value="in_review">In review</option><option value="resolved">Resolved</option></select>
                {item.segment_id && user.role === "admin" ? <button type="button" onClick={() => onManageRoad(item.segment_id!)}>Manage road</button> : null}
              </div>
            </article>
          ))}
        </div>
      </section>
    );
  }

  return (
    <section className="panel message-panel">
      <div className="panel-heading"><div><p className="eyebrow">Need help?</p><h2>Message the control room</h2></div></div>
      <p className="ai-risk-copy">Send a local blockage, shelter, or safety concern to reporters.</p>
      <form className="compact-form" onSubmit={(event) => { event.preventDefault(); onSend({ sender_name: name.trim() || "Resident", category, message: message.trim(), ...(segmentId ? { segment_id: Number(segmentId) } : {}) }); setMessage(""); }}>
        <input placeholder="Your name (optional)" value={name} onChange={(event) => setName(event.target.value)} />
        <select value={category} onChange={(event) => setCategory(event.target.value)}><option value="road_blockage">Road blockage</option><option value="shelter_help">Shelter help</option><option value="safety">Safety concern</option><option value="other">Other</option></select>
        <select value={segmentId} onChange={(event) => setSegmentId(event.target.value)}><option value="">Related road (optional)</option>{roads.map((road) => <option key={road.properties.segment_id} value={road.properties.segment_id}>{road.properties.name}</option>)}</select>
        <textarea required rows={3} placeholder="Describe what you need or observed" value={message} onChange={(event) => setMessage(event.target.value)} />
        <button className="primary-button" disabled={busy || !message.trim()} type="submit">Send message</button>
      </form>
    </section>
  );
}
