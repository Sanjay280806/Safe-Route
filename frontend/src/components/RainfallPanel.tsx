import { useEffect, useState } from "react";
import type { RainfallStatus, User } from "../types";

export function RainfallPanel({ rainfall, user, busy, onUpdate }: {
  rainfall: RainfallStatus | null;
  user: User | null;
  busy: boolean;
  onUpdate: (rainfall24: number, rainfall1: number) => void;
}) {
  const [rainfall24, setRainfall24] = useState("");
  const [rainfall1, setRainfall1] = useState("");

  useEffect(() => {
    if (!rainfall) return;
    setRainfall24(String(rainfall.rainfall_mm_24h));
    setRainfall1(String(rainfall.rainfall_mm_1h));
  }, [rainfall]);

  return (
    <section className="scenario-card rainfall-panel">
      <p className="eyebrow">Rainfall and risk input</p>
      <h2>{rainfall?.scenario_name ?? "Loading local rainfall…"}</h2>
      <p>{rainfall ? `${rainfall.updated_from}. Road-risk predictions update from this local scenario.` : "Loading rainfall data."}</p>
      <div><span><strong>{rainfall?.rainfall_mm_24h ?? "–"}</strong> mm / 24h</span><span><strong>{rainfall?.rainfall_mm_1h ?? "–"}</strong> mm / hour</span></div>
      {user?.role === "admin" ? (
        <form className="rainfall-editor" onSubmit={(event) => { event.preventDefault(); onUpdate(Number(rainfall24), Number(rainfall1)); }}>
          <label>24h<input min="0" required type="number" value={rainfall24} onChange={(event) => setRainfall24(event.target.value)} /></label>
          <label>1h<input min="0" required type="number" value={rainfall1} onChange={(event) => setRainfall1(event.target.value)} /></label>
          <button type="submit" disabled={busy}>Update rainfall</button>
        </form>
      ) : null}
    </section>
  );
}
