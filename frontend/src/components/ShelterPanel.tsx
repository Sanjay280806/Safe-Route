import { useEffect, useState } from "react";
import type { Shelter, User } from "../types";

interface ShelterPanelProps {
  shelters: Shelter[];
  user: User | null;
  busy: boolean;
  onOccupancyUpdate: (shelter: Shelter, occupancy: number, status: string) => void;
  onCreate: (payload: {
    name: string;
    lat: number;
    lon: number;
    address: string;
    capacity_assumed: number;
    occupancy_assumed: number;
    accessible: boolean;
    medical_support: boolean;
    water_available: boolean;
  }) => void;
}

export function ShelterPanel({ shelters, user, busy, onOccupancyUpdate, onCreate }: ShelterPanelProps) {
  const [adding, setAdding] = useState(false);
  const canUpdate = user?.role === "reporter" || user?.role === "admin";
  const canCreate = user?.role === "admin";

  return (
    <section className="panel shelter-panel">
      <div className="panel-heading">
        <div><p className="eyebrow">Evacuation support</p><h2>Shelter availability</h2></div>
        <span className="count-pill">{shelters.length}</span>
      </div>
      {shelters.length === 0 ? <p className="panel-empty">No local shelters are available yet.</p> : null}
      <div className="shelter-list">
        {shelters.map((shelter) => (
          <ShelterRow
            key={shelter.poi_id}
            shelter={shelter}
            editable={canUpdate}
            busy={busy}
            onSave={(occupancy, status) => onOccupancyUpdate(shelter, occupancy, status)}
          />
        ))}
      </div>
      {canCreate ? (
        <>
          <button className="secondary-button shelter-add-toggle" type="button" onClick={() => setAdding((value) => !value)}>
            {adding ? "Cancel" : "Add shelter"}
          </button>
          {adding ? <ShelterForm busy={busy} onSubmit={(payload) => { onCreate(payload); setAdding(false); }} /> : null}
        </>
      ) : null}
    </section>
  );
}

function ShelterRow({
  shelter,
  editable,
  busy,
  onSave,
}: {
  shelter: Shelter;
  editable: boolean;
  busy: boolean;
  onSave: (occupancy: number, status: string) => void;
}) {
  const [occupancy, setOccupancy] = useState(String(shelter.occupancy_assumed));
  const [status, setStatus] = useState<Shelter["status"]>(shelter.status);
  const capacityPercent = Math.min(100, Math.round((shelter.occupancy_assumed / Math.max(shelter.capacity_assumed, 1)) * 100));

  useEffect(() => {
    setOccupancy(String(shelter.occupancy_assumed));
    setStatus(shelter.status);
  }, [shelter.occupancy_assumed, shelter.status]);

  return (
    <article className="shelter-row">
      <div className="shelter-row-main">
        <strong>{shelter.name}</strong>
        <small>{shelter.address || "Local placeholder location"}</small>
        <span className="shelter-capacity">{shelter.available_capacity} spaces available of {shelter.capacity_assumed}</span>
        <span className="shelter-progress"><i style={{ width: `${capacityPercent}%` }} /></span>
        <small>{[shelter.accessible && "accessible", shelter.medical_support && "medical", shelter.water_available && "water"].filter(Boolean).join(" · ") || "basic support details pending"}</small>
      </div>
      {editable ? (
        <div className="shelter-editor">
          <label>Occupied<input aria-label={`${shelter.name} occupancy`} min="0" type="number" value={occupancy} onChange={(event) => setOccupancy(event.target.value)} /></label>
          <select aria-label={`${shelter.name} status`} value={status} onChange={(event) => setStatus(event.target.value as Shelter["status"])}>
            <option value="open">Open</option><option value="closed">Closed</option><option value="unknown">Unknown</option>
          </select>
          <button type="button" disabled={busy} onClick={() => onSave(Math.max(0, Number(occupancy) || 0), status)}>Save</button>
        </div>
      ) : <span className={`shelter-status ${shelter.status}`}>{shelter.status}</span>}
    </article>
  );
}

function ShelterForm({
  busy,
  onSubmit,
}: {
  busy: boolean;
  onSubmit: (payload: {
    name: string; lat: number; lon: number; address: string; capacity_assumed: number; occupancy_assumed: number;
    accessible: boolean; medical_support: boolean; water_available: boolean;
  }) => void;
}) {
  const [name, setName] = useState("");
  const [lat, setLat] = useState("12.981");
  const [lon, setLon] = useState("80.213");
  const [address, setAddress] = useState("");
  const [capacity, setCapacity] = useState("100");
  const [occupancy, setOccupancy] = useState("0");
  const [accessible, setAccessible] = useState(false);
  const [medical, setMedical] = useState(false);
  const [water, setWater] = useState(false);

  return (
    <form className="compact-form shelter-form" onSubmit={(event) => {
      event.preventDefault();
      onSubmit({ name, lat: Number(lat), lon: Number(lon), address, capacity_assumed: Number(capacity), occupancy_assumed: Number(occupancy), accessible, medical_support: medical, water_available: water });
    }}>
      <input required placeholder="Shelter name" value={name} onChange={(event) => setName(event.target.value)} />
      <input placeholder="Address / landmark" value={address} onChange={(event) => setAddress(event.target.value)} />
      <div><input required aria-label="Latitude" type="number" step="any" value={lat} onChange={(event) => setLat(event.target.value)} /><input required aria-label="Longitude" type="number" step="any" value={lon} onChange={(event) => setLon(event.target.value)} /></div>
      <div><input required aria-label="Capacity" min="1" type="number" value={capacity} onChange={(event) => setCapacity(event.target.value)} /><input required aria-label="Occupancy" min="0" type="number" value={occupancy} onChange={(event) => setOccupancy(event.target.value)} /></div>
      <label><input checked={accessible} type="checkbox" onChange={(event) => setAccessible(event.target.checked)} /> Accessible</label>
      <label><input checked={medical} type="checkbox" onChange={(event) => setMedical(event.target.checked)} /> Medical support</label>
      <label><input checked={water} type="checkbox" onChange={(event) => setWater(event.target.checked)} /> Water available</label>
      <button className="primary-button" disabled={busy} type="submit">Add local shelter</button>
    </form>
  );
}
