import {
  AdvancedMarker,
  APILoadingStatus,
  InfoWindow,
  Map as GoogleMap,
  Polyline,
  useApiLoadingStatus,
  useMap,
  type MapMouseEvent,
} from "@vis.gl/react-google-maps";
import { useEffect, useMemo, useState } from "react";
import {
  bboxToBoundsLiteral,
  expandBbox,
  getGoogleMapsApiKey,
  getGoogleMapsMapId,
  type Bbox,
} from "../config/googleMaps";
import { useGoogleMapsConfigured } from "./GoogleMapsProvider";
import type { BlockedReport, Destination, LatLng, MapGeoJson, MapMode, Poi, RoadFeature, Route } from "../types";
import { categoryIcon, categoryLabel } from "./CategoryChips";

const RISK_COLORS = {
  low: "#22c55e",
  moderate: "#eab308",
  high: "#f97316",
  critical: "#dc2626",
} as const;

function roadFeatures(mapData: MapGeoJson | null): RoadFeature[] {
  if (!mapData) return [];
  return mapData.features.filter(
    (feature): feature is RoadFeature =>
      feature.geometry.type === "LineString" && feature.properties.layer_type === "road",
  );
}

function toGooglePath(coordinates: [number, number][]): google.maps.LatLngLiteral[] {
  return coordinates.map(([lon, lat]) => ({ lat, lng: lon }));
}

function MapFocus({ point }: { point: LatLng | null }) {
  const map = useMap();

  useEffect(() => {
    if (!map || !point) return;
    map.panTo({ lat: point.lat, lng: point.lon });
    if ((map.getZoom() ?? 0) < 16) {
      map.setZoom(16);
    }
  }, [map, point]);

  return null;
}

interface RoadLayerProps {
  roads: RoadFeature[];
  reports: BlockedReport[];
  onRoadSelect: (road: RoadFeature) => void;
}

function RoadLayer({ roads, reports, onRoadSelect }: RoadLayerProps) {
  const reportBySegment = useMemo(
    () => new globalThis.Map<number, BlockedReport>(
      reports.filter((report) => report.verification_status !== "rejected").map((report) => [report.segment_id, report]),
    ),
    [reports],
  );

  return (
    <>
      {roads.map((road) => {
        const report = reportBySegment.get(road.properties.segment_id);
        const confirmedBlocked = road.properties.blocked || report?.verification_status === "confirmed";
        const pending = report?.verification_status === "pending";
        const color = confirmedBlocked ? "#7f1d1d" : pending ? "#f59e0b" : RISK_COLORS[road.properties.current_risk_level];
        const path = toGooglePath(road.geometry.coordinates);

        return (
          <Polyline
            key={road.properties.segment_id}
            path={path}
            strokeColor={color}
            strokeWeight={confirmedBlocked ? 7 : 6}
            strokeOpacity={0.92}
            clickable
            icons={
              confirmedBlocked || pending
                ? [{ icon: { path: "M 0,-1 0,1", strokeOpacity: 1, scale: 3 }, offset: "0", repeat: "16px" }]
                : undefined
            }
            onClick={(event) => {
              event.domEvent.stopPropagation();
              onRoadSelect(road);
            }}
          />
        );
      })}
    </>
  );
}

interface MapPanelProps {
  center: [number, number];
  zoom: number;
  bounds: Bbox;
  mapData: MapGeoJson | null;
  pois: Poi[];
  reports: BlockedReport[];
  routes: Route[];
  oldRoute: Route | null;
  origin: LatLng | null;
  destination: Destination | null;
  currentLocation: LatLng | null;
  mapMode: MapMode;
  focusPoint: LatLng | null;
  onMapClick: (point: LatLng) => void;
  onPoiSelect: (poi: Poi) => void;
  onRoadSelect: (road: RoadFeature) => void;
}

function MapStatusOverlay() {
  const status = useApiLoadingStatus();

  if (status === APILoadingStatus.LOADED) return null;

  if (status === APILoadingStatus.AUTH_FAILURE) {
    return (
      <div className="map-inline-error" role="alert">
        Invalid Google Maps API key. Update <code>VITE_GOOGLE_MAPS_API_KEY</code>.
      </div>
    );
  }

  if (status === APILoadingStatus.FAILED) {
    return (
      <div className="map-inline-error" role="alert">
        Google Maps could not be loaded. Check your network and API settings.
      </div>
    );
  }

  return <div className="map-loading-overlay" role="status">Loading Google Maps…</div>;
}

export function MapPanel({
  center,
  zoom,
  bounds,
  mapData,
  pois,
  reports,
  routes,
  oldRoute,
  origin,
  destination,
  currentLocation,
  mapMode,
  focusPoint,
  onMapClick,
  onPoiSelect,
  onRoadSelect,
}: MapPanelProps) {
  const configured = useGoogleMapsConfigured();
  const roads = roadFeatures(mapData);
  const mapBounds = useMemo(() => bboxToBoundsLiteral(expandBbox(bounds)), [bounds]);
  const [activePoi, setActivePoi] = useState<Poi | null>(null);

  const modeMessage: Record<MapMode, string> = {
    pan: "Pan or zoom the map",
    set_origin: "Click map to set origin",
    set_destination: "Click map to set destination",
    report_road: "Select a road to report",
  };

  const handleMapClick = (event: MapMouseEvent) => {
    if (mapMode !== "set_origin" && mapMode !== "set_destination") return;
    const latLng = event.detail.latLng;
    if (!latLng) return;
    onMapClick({ lat: latLng.lat, lon: latLng.lng });
  };

  const destinationPoint =
    destination?.type === "poi"
      ? { lat: destination.poi.lat, lon: destination.poi.lon }
      : destination?.type === "custom"
        ? destination.location
        : null;

  if (!configured || !getGoogleMapsApiKey()) {
    return (
      <section className="map-panel" aria-label="Flood-aware map">
        <div className="map-load-error map-load-error-panel" role="alert">
          <strong>Google Maps is not configured</strong>
          <p>
            Add <code>VITE_GOOGLE_MAPS_API_KEY</code> to <code>frontend/.env</code> and enable the
            Maps JavaScript API and Places API in Google Cloud Console.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="map-panel" aria-label="Flood-aware map">
      <div className="map-top-status">
        <span className={`map-mode-badge ${mapMode !== "pan" ? "active" : ""}`}>{modeMessage[mapMode]}</span>
        <span className="map-count">{roads.length} monitored roads</span>
      </div>

      <MapStatusOverlay />

      <GoogleMap
        mapId={getGoogleMapsMapId()}
        className="map-canvas"
        defaultCenter={{ lat: center[0], lng: center[1] }}
        defaultZoom={zoom}
        gestureHandling="greedy"
        restriction={{ latLngBounds: mapBounds, strictBounds: false }}
        mapTypeControl
        fullscreenControl
        zoomControl
        streetViewControl={false}
        clickableIcons={false}
        onClick={handleMapClick}
      >
        <MapFocus point={focusPoint} />
        <RoadLayer roads={roads} reports={reports} onRoadSelect={onRoadSelect} />

        {oldRoute ? (
          <Polyline
            path={toGooglePath(oldRoute.geometry.coordinates)}
            strokeColor="#cbd5e1"
            strokeWeight={7}
            strokeOpacity={0.7}
            clickable={false}
          />
        ) : null}

        {routes.map((route) => (
          <Polyline
            key={route.route_type}
            path={toGooglePath(route.geometry.coordinates)}
            strokeColor={route.route_type === "safe" ? "#2563eb" : "#94a3b8"}
            strokeWeight={route.route_type === "safe" ? 7 : 5}
            strokeOpacity={0.95}
            icons={
              route.route_type === "short"
                ? [{ icon: { path: "M 0,-1 0,1", strokeOpacity: 1, scale: 3 }, offset: "0", repeat: "18px" }]
                : undefined
            }
            clickable={false}
          />
        ))}

        {pois.map((poi) => (
          <AdvancedMarker
            key={poi.id}
            position={{ lat: poi.lat, lng: poi.lon }}
            title={poi.name}
            onClick={() => setActivePoi(poi)}
          >
            <span className={`map-poi-icon ${poi.category}`} aria-label={poi.category}>
              {categoryIcon(poi.category)}
            </span>
          </AdvancedMarker>
        ))}

        {origin ? (
          <AdvancedMarker position={{ lat: origin.lat, lng: origin.lon }} title="Origin">
            <span className="map-origin-marker" aria-hidden="true" />
          </AdvancedMarker>
        ) : null}

        {destinationPoint ? (
          <AdvancedMarker position={{ lat: destinationPoint.lat, lng: destinationPoint.lon }} title="Destination">
            <span className="map-destination-marker" aria-hidden="true" />
          </AdvancedMarker>
        ) : null}

        {currentLocation ? (
          <AdvancedMarker position={{ lat: currentLocation.lat, lng: currentLocation.lon }} title="Navigating">
            <span className="map-current-marker" aria-hidden="true" />
          </AdvancedMarker>
        ) : null}

        {activePoi ? (
          <InfoWindow
            position={{ lat: activePoi.lat, lng: activePoi.lon }}
            onCloseClick={() => setActivePoi(null)}
          >
            <div className="map-info-window">
              <strong>{activePoi.name}</strong>
              <p>{categoryLabel(activePoi.category)} · {activePoi.status}</p>
              <button type="button" className="popup-action" onClick={() => { onPoiSelect(activePoi); setActivePoi(null); }}>
                Choose destination
              </button>
            </div>
          </InfoWindow>
        ) : null}
      </GoogleMap>

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
