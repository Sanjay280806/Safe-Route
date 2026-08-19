import L, { type LeafletMouseEvent } from "leaflet";
import { useEffect } from "react";
import { CircleMarker, MapContainer, Marker, Polyline, Popup, TileLayer, Tooltip, useMap, useMapEvents } from "react-leaflet";
import { categoryIcon, categoryLabel } from "./CategoryChips";
import type { BlockedReport, Destination, LatLng, MapGeoJson, MapMode, Poi, RoadFeature, Route, User } from "../types";

const RISK_COLORS = {
  low: "#22c55e",
  moderate: "#eab308",
  high: "#f97316",
  critical: "#dc2626",
};

function roadFeatures(mapData: MapGeoJson | null): RoadFeature[] {
  if (!mapData) return [];
  return mapData.features.filter((feature): feature is RoadFeature => feature.geometry.type === "LineString" && feature.properties.layer_type === "road");
}

function poiMarkerIcon(poi: Poi): L.DivIcon {
  return L.divIcon({
    className: "leaflet-poi-icon-wrapper",
    html: `<span class="leaflet-poi-icon ${poi.category}" aria-label="${poi.category}">${categoryIcon(poi.category)}</span>`,
    iconSize: [34, 34],
    iconAnchor: [17, 17],
  });
}

function originIcon(): L.DivIcon {
  return L.divIcon({ className: "leaflet-origin-wrapper", html: '<span class="leaflet-origin-marker"></span>', iconSize: [24, 24], iconAnchor: [12, 12] });
}

function currentLocationIcon(): L.DivIcon {
  return L.divIcon({ className: "leaflet-current-wrapper", html: '<span class="leaflet-current-marker"></span>', iconSize: [28, 28], iconAnchor: [14, 14] });
}

function MapClickHandler({ mode, onMapClick }: { mode: MapMode; onMapClick: (point: LatLng) => void }) {
  useMapEvents({
    click(event) {
      if (mode === "set_origin" || mode === "set_destination") {
        onMapClick({ lat: event.latlng.lat, lon: event.latlng.lng });
      }
    },
  });
  return null;
}

function MapFocus({ point }: { point: LatLng | null }) {
  const map = useMap();
  useEffect(() => {
    if (point) map.flyTo([point.lat, point.lon], Math.max(map.getZoom(), 16), { duration: 0.45 });
  }, [map, point]);
  return null;
}

interface RoadLayerProps {
  roads: RoadFeature[];
  reports: BlockedReport[];
  user: User | null;
  onRoadSelect: (road: RoadFeature) => void;
}

function RoadLayer({ roads, reports, user, onRoadSelect }: RoadLayerProps) {
  const reportBySegment = new Map(reports.filter((report) => report.verification_status !== "rejected").map((report) => [report.segment_id, report]));

  return (
    <>
      {roads.map((road) => {
        const report = reportBySegment.get(road.properties.segment_id);
        const confirmedBlocked = road.properties.blocked || report?.verification_status === "confirmed";
        const pending = report?.verification_status === "pending";
        const color = confirmedBlocked ? "#7f1d1d" : pending ? "#f59e0b" : RISK_COLORS[road.properties.current_risk_level];
        const positions = road.geometry.coordinates.map(([lon, lat]) => [lat, lon] as [number, number]);

        return (
          <Polyline
            key={road.properties.segment_id}
            positions={positions}
            pathOptions={{ color, weight: confirmedBlocked ? 7 : 6, opacity: 0.92, dashArray: confirmedBlocked || pending ? "8 8" : undefined, lineCap: "round" }}
            eventHandlers={{ click: () => onRoadSelect(road) }}
          >
            <Tooltip sticky direction="top">
              <strong>{road.properties.name}</strong><br />
              {confirmedBlocked ? "Confirmed blocked" : pending ? "Pending report" : `${road.properties.current_risk_level} risk`}
              {road.properties.predicted_time_to_high_risk_min !== null ? <><br />High risk in ~{road.properties.predicted_time_to_high_risk_min} min</> : null}
              {user && (user.role === "reporter" || user.role === "admin") ? <><br /><em>Click to report this road</em></> : null}
            </Tooltip>
          </Polyline>
        );
      })}
    </>
  );
}

interface MapPanelProps {
  center: [number, number];
  zoom: number;
  mapData: MapGeoJson | null;
  pois: Poi[];
  reports: BlockedReport[];
  routes: Route[];
  oldRoute: Route | null;
  origin: LatLng | null;
  destination: Destination | null;
  currentLocation: LatLng | null;
  mapMode: MapMode;
  user: User | null;
  focusPoint: LatLng | null;
  onMapClick: (point: LatLng) => void;
  onPoiSelect: (poi: Poi) => void;
  onRoadSelect: (road: RoadFeature) => void;
}

export function MapPanel({
  center,
  zoom,
  mapData,
  pois,
  reports,
  routes,
  oldRoute,
  origin,
  destination,
  currentLocation,
  mapMode,
  user,
  focusPoint,
  onMapClick,
  onPoiSelect,
  onRoadSelect,
}: MapPanelProps) {
  const roads = roadFeatures(mapData);
  const modeMessage: Record<MapMode, string> = {
    pan: "Pan or zoom the map",
    set_origin: "Click map to set origin",
    set_destination: "Click map to set destination",
    report_road: "Select a road to report",
  };

  return (
    <section className="map-panel" aria-label="Flood-aware map">
      <div className="map-top-status">
        <span className={`map-mode-badge ${mapMode !== "pan" ? "active" : ""}`}>{modeMessage[mapMode]}</span>
        <span className="map-count">{roads.length} monitored roads</span>
      </div>
      <MapContainer center={center} zoom={zoom} scrollWheelZoom className="map-canvas" preferCanvas>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapClickHandler mode={mapMode} onMapClick={onMapClick} />
        <MapFocus point={focusPoint} />
        <RoadLayer roads={roads} reports={reports} user={user} onRoadSelect={onRoadSelect} />

        {oldRoute ? <Polyline positions={oldRoute.geometry.coordinates.map(([lon, lat]) => [lat, lon] as [number, number])} pathOptions={{ color: "#cbd5e1", weight: 7, opacity: 0.7 }} /> : null}
        {routes.map((route) => (
          <Polyline
            key={route.route_type}
            positions={route.geometry.coordinates.map(([lon, lat]) => [lat, lon] as [number, number])}
            pathOptions={{ color: route.route_type === "safe" ? "#2563eb" : "#94a3b8", weight: route.route_type === "safe" ? 7 : 5, opacity: 0.95, dashArray: route.route_type === "short" ? "10 9" : undefined, lineCap: "round" }}
          >
            <Tooltip sticky>{route.route_type === "safe" ? "Safe route" : "Shortest route"} · {route.duration_min.toFixed(1)} min</Tooltip>
          </Polyline>
        ))}

        {pois.map((poi) => (
          <Marker key={poi.id} position={[poi.lat, poi.lon]} icon={poiMarkerIcon(poi)} eventHandlers={{ click: () => onPoiSelect(poi) }}>
            <Popup>
              <strong>{poi.name}</strong><br />
              {categoryLabel(poi.category)} · {poi.status}<br />
              <button type="button" className="popup-action" onClick={() => onPoiSelect(poi)}>Choose destination</button>
            </Popup>
          </Marker>
        ))}

        {origin ? <Marker position={[origin.lat, origin.lon]} icon={originIcon()}><Tooltip permanent direction="top" offset={[0, -12]}>Origin</Tooltip></Marker> : null}
        {destination?.type === "custom" ? <CircleMarker center={[destination.location.lat, destination.location.lon]} radius={9} pathOptions={{ color: "#7c3aed", fillColor: "#8b5cf6", fillOpacity: 1 }}><Tooltip permanent direction="top">Destination</Tooltip></CircleMarker> : null}
        {currentLocation ? <Marker position={[currentLocation.lat, currentLocation.lon]} icon={currentLocationIcon()}><Tooltip permanent direction="top">Navigating</Tooltip></Marker> : null}
      </MapContainer>
      <MapLegend />
    </section>
  );
}

function MapLegend() {
  return (
    <aside className="map-legend" aria-label="Road risk legend">
      <strong>Road risk</strong>
      <span><i className="risk-low" /> Low</span>
      <span><i className="risk-moderate" /> Moderate</span>
      <span><i className="risk-high" /> High</span>
      <span><i className="risk-critical" /> Critical</span>
      <span><i className="risk-blocked" /> Blocked</span>
    </aside>
  );
}
