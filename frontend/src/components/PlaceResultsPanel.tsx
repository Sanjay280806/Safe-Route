import { categoryIcon, categoryLabel } from "./CategoryChips";
import type { Poi } from "../types";

interface PlaceResultsPanelProps {
  places: Poi[];
  selectedPoi: Poi | null;
  loading: boolean;
  onSelect: (poi: Poi) => void;
}

export function PlaceResultsPanel({ places, selectedPoi, loading, onSelect }: PlaceResultsPanelProps) {
  return (
    <section className="panel place-results">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Important places</p>
          <h2>Explore nearby</h2>
        </div>
        <span className="count-pill">{places.length}</span>
      </div>

      {loading ? <p className="muted panel-empty">Loading places…</p> : null}
      {!loading && places.length === 0 ? <p className="muted panel-empty">No matching places in the local dataset.</p> : null}

      <div className="place-list">
        {places.map((poi) => (
          <button
            type="button"
            key={poi.id}
            className={`place-row ${selectedPoi?.id === poi.id ? "selected" : ""}`}
            onClick={() => onSelect(poi)}
          >
            <span className={`place-icon ${poi.category}`} aria-hidden="true">{categoryIcon(poi.category)}</span>
            <span className="place-copy">
              <strong>{poi.name}</strong>
              <span>{categoryLabel(poi.category)} · {poi.status}</span>
              {poi.address ? <small>{poi.address}</small> : null}
            </span>
            <span className="chevron" aria-hidden="true">›</span>
          </button>
        ))}
      </div>
    </section>
  );
}
