import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { createRoute, createShelter, getActiveReports, getArea, getHealth, getMapGeoJson, getMessages, getPois, getRainfall, getScenarios, getShelters, getValidationSummary, recomputeRisk, reroute, sendMessage, submitBlockedReport, updateMessageStatus, updateRainfall, updateShelterOccupancy, useMocks, verifyReport } from "../api/client";
import { AiRiskPanel } from "../components/AiRiskPanel";
import { CategoryChips } from "../components/CategoryChips";
import { ExplanationPanel } from "../components/ExplanationPanel";
import { GoogleMapsProvider } from "../components/GoogleMapsProvider";
import { MapPanel } from "../components/MapPanel";
import { NavigationSimulator } from "../components/NavigationSimulator";
import { PlaceResultsPanel } from "../components/PlaceResultsPanel";
import { ReportModal } from "../components/ReportModal";
import { ReportStatusPanel } from "../components/ReportStatusPanel";
import { RoutePanel } from "../components/RoutePanel";
import { ShelterPanel } from "../components/ShelterPanel";
import { RainfallPanel } from "../components/RainfallPanel";
import { MessagePanel } from "../components/MessagePanel";
import { RiskTablePanel } from "../components/RiskTablePanel";
import { SearchBar } from "../components/SearchBar";
import { WarningsPanel } from "../components/WarningsPanel";
import type { AreaMeta, BlockedReport, Destination, FieldMessage, Health, LatLng, MapGeoJson, MapMode, Poi, PoiCategory, RainfallStatus, RoadFeature, Route, RouteResponse, Shelter, User, ValidationSummary } from "../types";
import { expandBbox, type Bbox } from "../config/googleMaps";

const fallbackArea: AreaMeta = {
  name: "West Velachery, Chennai",
  bbox: [12.965, 80.195, 12.995, 80.235],
  default_center: [12.98, 80.2125],
  default_zoom: 15,
  disclaimer: "Demo decision-support tool. Not an official emergency service.",
};

function distanceMeters(a: LatLng, b: LatLng): number {
  const latitudeScale = 111_320;
  const longitudeScale = latitudeScale * Math.cos((a.lat * Math.PI) / 180);
  return Math.hypot((a.lat - b.lat) * latitudeScale, (a.lon - b.lon) * longitudeScale);
}

interface DashboardPageProps {
  user: User | null;
  token: string | null;
  onLogout: () => void;
}

export function DashboardPage({ user, token, onLogout }: DashboardPageProps) {
  const [area, setArea] = useState<AreaMeta>(fallbackArea);
  const [scenarioId, setScenarioId] = useState<number>(3);
  const [pois, setPois] = useState<Poi[]>([]);
  const [mapData, setMapData] = useState<MapGeoJson | null>(null);
  const [reports, setReports] = useState<BlockedReport[]>([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<PoiCategory | null>(null);
  const [selectedPoi, setSelectedPoi] = useState<Poi | null>(null);
  const [origin, setOrigin] = useState<LatLng | null>({ lat: 12.98, lon: 80.21 });
  const [originLabel, setOriginLabel] = useState("");
  const [destination, setDestination] = useState<Destination | null>(null);
  const [destinationLabel, setDestinationLabel] = useState("");
  const [mapMode, setMapMode] = useState<MapMode>("pan");
  const [routeResponse, setRouteResponse] = useState<RouteResponse | null>(null);
  const [oldRoute, setOldRoute] = useState<Route | null>(null);
  const [currentLocation, setCurrentLocation] = useState<LatLng | null>(null);
  const [focusPoint, setFocusPoint] = useState<LatLng | null>(null);
  const [selectedRoad, setSelectedRoad] = useState<RoadFeature | null>(null);
  const [reportOpen, setReportOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [routeLoading, setRouteLoading] = useState(false);
  const [reportSubmitting, setReportSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [notification, setNotification] = useState("");
  const [health, setHealth] = useState<Health | null>(null);
  const [validation, setValidation] = useState<ValidationSummary | null>(null);
  const [recomputing, setRecomputing] = useState(false);
  const [shelters, setShelters] = useState<Shelter[]>([]);
  const [rainfall, setRainfall] = useState<RainfallStatus | null>(null);
  const [messages, setMessages] = useState<FieldMessage[]>([]);
  const [operationsBusy, setOperationsBusy] = useState(false);

  const loadMap = useCallback(async (nextScenarioId: number) => {
    const data = await getMapGeoJson(nextScenarioId);
    setMapData(data);
  }, []);

  useEffect(() => {
    let active = true;
    const load = async () => {
      setLoading(true);
      setError("");
      try {
        const [nextArea, nextScenarios, nextPois, nextReports, nextShelters, nextRainfall] = await Promise.all([getArea(), getScenarios(), getPois(), getActiveReports(), getShelters(), getRainfall()]);
        const activeScenario = nextScenarios.find((scenario) => scenario.is_active)?.id ?? nextScenarios[0]?.id ?? 3;
        const nextMap = await getMapGeoJson(activeScenario);
        let nextHealth: Health | null = null;
        let nextValidation: ValidationSummary | null = null;
        try {
          [nextHealth, nextValidation] = await Promise.all([getHealth(), getValidationSummary()]);
        } catch {
          nextHealth = null;
          nextValidation = null;
        }
        if (!active) return;
        setArea(nextArea);
        setPois(nextPois);
        setReports(nextReports);
        setShelters(nextShelters);
        setRainfall(nextRainfall);
        setHealth(nextHealth);
        setValidation(nextValidation);
        setScenarioId(activeScenario);
        setMapData(nextMap);
        setOrigin({ lat: nextArea.default_center[0], lon: nextArea.default_center[1] - 0.0025 });
      } catch (caughtError) {
        if (active) setError(caughtError instanceof Error ? caughtError.message : "Unable to load the local map data.");
      } finally {
        if (active) setLoading(false);
      }
    };
    void load();
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!token || (user?.role !== "reporter" && user?.role !== "admin")) {
      setMessages([]);
      return;
    }
    void getMessages(token)
      .then(setMessages)
      .catch((caughtError) => setError(caughtError instanceof Error ? caughtError.message : "Unable to load resident messages."));
  }, [token, user?.role]);

  const filteredPois = useMemo(() => {
    const search = query.trim().toLowerCase();
    const matching = pois.filter((poi) => {
      const matchesCategory = !category || poi.category === category;
      const searchable = `${poi.name} ${poi.category} ${poi.address ?? ""}`.toLowerCase();
      return matchesCategory && (!search || searchable.includes(search));
    });
    if (!origin || destination) return matching;
    return matching
      .map((poi) => ({ ...poi, distance_m: Math.round(distanceMeters(origin, { lat: poi.lat, lon: poi.lon })) }))
      .sort((a, b) => (a.distance_m ?? 0) - (b.distance_m ?? 0));
  }, [category, destination, origin, pois, query]);

  const roads = useMemo(() => (mapData?.features.filter((feature): feature is RoadFeature => feature.geometry.type === "LineString" && feature.properties.layer_type === "road") ?? []), [mapData]);
  const displayedRoutes = useMemo(() => {
    if (!routeResponse) return [];
    return routeResponse.routes.filter((route) => route.route_type === "safe").slice(0, 1);
  }, [routeResponse]);
  const navigationRoute = useMemo(() => {
    if (!routeResponse) return null;
    return routeResponse.routes.find((route) => route.route_type === "safe") ?? routeResponse.routes[0] ?? null;
  }, [routeResponse]);

  const requestRouteFor = useCallback(async (nextDestination: Destination) => {
    if (!origin) return;
    setRouteLoading(true);
    setError("");
    try {
      const destinationPayload = nextDestination.type === "poi" ? { poi_id: nextDestination.poi.id } : nextDestination.location;
      const response = await createRoute({
        origin,
        destination: destinationPayload,
        route_mode: "safe",
        scenario_id: scenarioId,
        include_alternatives: false,
      });
      setRouteResponse(response);
      setOldRoute(null);
      setCurrentLocation(null);
      setNotification("The optimal flood-aware route is ready.");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to find a safe route.");
    } finally {
      setRouteLoading(false);
    }
  }, [origin, scenarioId]);

  const selectPoi = useCallback((poi: Poi) => {
    setSelectedPoi(poi);
    setDestination({ type: "poi", poi });
    setDestinationLabel(poi.name);
    setFocusPoint({ lat: poi.lat, lon: poi.lon });
    setMapMode("pan");
    void requestRouteFor({ type: "poi", poi });
  }, [requestRouteFor]);

  const handleOriginSelect = useCallback((point: LatLng, label: string) => {
    setOrigin(point);
    setOriginLabel(label);
    setFocusPoint(point);
    setMapMode("pan");
    setNotification("Origin updated.");
  }, []);

  const handleDestinationSelect = useCallback((nextDestination: Destination, label: string) => {
    setSelectedPoi(nextDestination.type === "poi" ? nextDestination.poi : null);
    setDestination(nextDestination);
    setDestinationLabel(label);
    const focus = nextDestination.type === "poi"
      ? { lat: nextDestination.poi.lat, lon: nextDestination.poi.lon }
      : nextDestination.location;
    setFocusPoint(focus);
    setMapMode("pan");
    void requestRouteFor(nextDestination);
  }, [requestRouteFor]);

  const handleMapClick = useCallback((point: LatLng) => {
    if (mapMode === "set_origin") {
      setOrigin(point);
      setOriginLabel(`${point.lat.toFixed(4)}, ${point.lon.toFixed(4)}`);
      setFocusPoint(point);
      setMapMode("pan");
      setNotification("Origin updated from the map.");
      return;
    }
    if (mapMode === "set_destination") {
      setSelectedPoi(null);
      setDestination({ type: "custom", location: point });
      setDestinationLabel(`${point.lat.toFixed(4)}, ${point.lon.toFixed(4)}`);
      setFocusPoint(point);
      setMapMode("pan");
      const nextDestination: Destination = { type: "custom", location: point };
      void requestRouteFor(nextDestination);
    }
  }, [mapMode, requestRouteFor]);

  const requestRoute = () => {
    if (destination) void requestRouteFor(destination);
  };

  const clearRoute = () => {
    setRouteResponse(null);
    setOldRoute(null);
    setDestination(null);
    setDestinationLabel("");
    setSelectedPoi(null);
    setCurrentLocation(null);
    setMapMode("pan");
    setNotification("Route cleared.");
  };

  const selectRoad = useCallback((road: RoadFeature) => {
    setSelectedRoad(road);
    if (user?.role === "reporter" || user?.role === "admin") {
      setReportOpen(true);
      setMapMode("report_road");
    } else {
      setNotification(`${road.properties.name}: ${road.properties.current_risk_level} risk. Sign in as a reporter to submit a road report.`);
    }
  }, [user]);

  const submitReport = async (payload: { source: string; note: string; flood_status: string }) => {
    if (!selectedRoad || !token) return;
    setReportSubmitting(true);
    try {
      const response = await submitBlockedReport({ segment_id: selectedRoad.properties.segment_id, ...payload }, token);
      const report: BlockedReport = {
        id: response.report_id,
        segment_id: response.segment_id,
        road_name: selectedRoad.properties.name,
        source: payload.source,
        verification_status: response.verification_status,
        note: payload.note,
        created_at: new Date().toISOString(),
      };
      setReports((current) => [...current.filter((item) => item.segment_id !== report.segment_id), report]);
      setReportOpen(false);
      setMapMode("pan");
      setNotification(`${selectedRoad.properties.name} marked ${response.verification_status}. Credibility score: ${Math.round(response.credibility_score * 100)}%.`);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Could not submit the report.");
    } finally {
      setReportSubmitting(false);
    }
  };

  const handleVerify = async (report: BlockedReport, decision: "confirm" | "reject") => {
    if (!token) return;
    try {
      await verifyReport(report.id, decision, token);
      setReports((current) => current.map((item) => item.id === report.id ? { ...item, verification_status: decision === "confirm" ? "confirmed" : "rejected" } : item));
      setNotification(`Report ${decision === "confirm" ? "confirmed" : "rejected"} by control room.`);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Could not update this report.");
    }
  };

  const handleReroute = useCallback(async (report: BlockedReport) => {
    if (!currentLocation || !destination) return;
    try {
      setNotification(`Road ahead is blocked on ${report.road_name}. Rerouting…`);
      const destinationPayload = destination.type === "poi" ? { poi_id: destination.poi.id } : destination.location;
      const response = await reroute({
        current_location: currentLocation,
        destination: destinationPayload,
        reason: "blocked_ahead",
        route_mode: "safe",
        scenario_id: scenarioId,
        include_alternatives: false,
      });
      const previousRoute = routeResponse?.routes.find((route) => route.route_type === "safe") ?? routeResponse?.routes[0] ?? null;
      setOldRoute(previousRoute);
      setRouteResponse(response);
      setNotification(`Rerouted around ${report.road_name}. The previous path is shown in grey.`);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to reroute around the blocked road.");
    }
  }, [currentLocation, destination, routeResponse, scenarioId]);

  const handleRecomputeRisk = async () => {
    if (!token) return;
    setRecomputing(true);
    setError("");
    try {
      const result = await recomputeRisk(token);
      await loadMap(scenarioId);
      const [nextHealth, nextValidation] = await Promise.all([getHealth(), getValidationSummary()]);
      setHealth(nextHealth);
      setValidation(nextValidation);
      setRainfall(await getRainfall());
      setNotification(`AI risk recomputed for ${result.segments_updated} road segments.`);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to recompute flood risk.");
    } finally {
      setRecomputing(false);
    }
  };

  const handleShelterOccupancyUpdate = async (shelter: Shelter, occupancy: number, status: string) => {
    if (!token) return;
    setOperationsBusy(true);
    try {
      const updated = await updateShelterOccupancy(shelter.poi_id, { occupancy_assumed: occupancy, status }, token);
      setShelters((current) => current.map((item) => item.poi_id === updated.poi_id ? updated : item));
      setNotification(`${updated.name} availability updated.`);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to update shelter occupancy.");
    } finally {
      setOperationsBusy(false);
    }
  };

  const handleCreateShelter = async (payload: {
    name: string; lat: number; lon: number; address: string; capacity_assumed: number; occupancy_assumed: number;
    accessible: boolean; medical_support: boolean; water_available: boolean;
  }) => {
    if (!token) return;
    setOperationsBusy(true);
    try {
      const created = await createShelter(payload, token);
      setShelters((current) => [...current, created]);
      const [nextPois, nextMap] = await Promise.all([getPois(), getMapGeoJson(scenarioId)]);
      setPois(nextPois);
      setMapData(nextMap);
      setNotification(`${created.name} added as a user-supplied shelter pending verification.`);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to add the shelter.");
    } finally {
      setOperationsBusy(false);
    }
  };

  const handleRainfallUpdate = async (rainfall24: number, rainfall1: number) => {
    if (!token) return;
    setOperationsBusy(true);
    try {
      const updated = await updateRainfall({ rainfall_mm_24h: rainfall24, rainfall_mm_1h: rainfall1 }, token);
      const [nextMap, nextHealth, nextValidation] = await Promise.all([getMapGeoJson(scenarioId), getHealth(), getValidationSummary()]);
      setRainfall(updated);
      setMapData(nextMap);
      setHealth(nextHealth);
      setValidation(nextValidation);
      setNotification("Rainfall input saved and local road-risk predictions recomputed.");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to update rainfall.");
    } finally {
      setOperationsBusy(false);
    }
  };

  const handleSendMessage = async (payload: { sender_name: string; category: string; message: string; segment_id?: number }) => {
    setOperationsBusy(true);
    try {
      await sendMessage(payload, token);
      setNotification("Message sent to the control room.");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to send the message.");
    } finally {
      setOperationsBusy(false);
    }
  };

  const handleMessageStatus = async (message: FieldMessage, status: FieldMessage["status"]) => {
    if (!token) return;
    setOperationsBusy(true);
    try {
      const updated = await updateMessageStatus(message.id, status, token);
      setMessages((current) => current.map((item) => item.id === updated.id ? updated : item));
      setNotification("Resident message status updated.");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to update the message.");
    } finally {
      setOperationsBusy(false);
    }
  };

  const handleManageRoad = (segmentId: number) => {
    const road = roads.find((item) => item.properties.segment_id === segmentId);
    if (!road) return;
    setSelectedRoad(road);
    setReportOpen(true);
    setMapMode("report_road");
  };

  const mapCenter: [number, number] = area.default_center;
  const mapBounds: Bbox = expandBbox(area.bbox as Bbox);
  return (
    <GoogleMapsProvider>
    <main className="dashboard-page">
      <header className="app-header">
        <div className="header-main-row">
          <Link className="brand" to="/"><span className="brand-mark">⌁</span><span>SafeRoute<small>Velachery</small></span></Link>
          <SearchBar value={query} onChange={setQuery} onClear={() => setQuery("")} />
          <div className="header-tools">
            {user ? <div className="user-menu"><span className="user-avatar">{user.username.slice(0, 1).toUpperCase()}</span><span><strong>{user.username}</strong><small>{user.role}</small></span><button type="button" onClick={onLogout}>Sign out</button></div> : <Link className="login-button" to="/login">Reporter login</Link>}
          </div>
        </div>
        <CategoryChips selected={category} onSelect={setCategory} />
      </header>

      {notification ? <div className="dashboard-notice" role="status"><span>✓</span>{notification}<button type="button" aria-label="Dismiss notification" onClick={() => setNotification("")}>×</button></div> : null}
      {error ? <div className="dashboard-error" role="alert"><span>!</span>{error}<button type="button" aria-label="Dismiss error" onClick={() => setError("")}>×</button></div> : null}

      <div className={`dashboard-layout ${user ? "operator-layout" : "resident-layout"}`}>
        {!user ? (
        <aside className="left-sidebar">
          <PlaceResultsPanel places={filteredPois} selectedPoi={selectedPoi} loading={loading} onSelect={selectPoi} />
          <RoutePanel
            origin={origin}
            originLabel={originLabel}
            destination={destination}
            destinationLabel={destinationLabel}
            routeResponse={routeResponse}
            loading={routeLoading}
            mapMode={mapMode}
            mapBounds={mapBounds}
            onOriginLabelChange={setOriginLabel}
            onDestinationLabelChange={setDestinationLabel}
            onOriginSelect={handleOriginSelect}
            onDestinationSelect={handleDestinationSelect}
            onMapModeChange={setMapMode}
            onRequestRoute={() => void requestRoute()}
            onClear={clearRoute}
            onPlacesError={setError}
          />
        </aside>
        ) : null}

        <MapPanel key={`map-${user?.role ?? "resident"}`} center={mapCenter} zoom={area.default_zoom} bounds={mapBounds} mapData={mapData} pois={filteredPois} reports={reports} routes={displayedRoutes} oldRoute={oldRoute} origin={origin} destination={destination} currentLocation={currentLocation} mapMode={mapMode} focusPoint={focusPoint} onMapClick={handleMapClick} onPoiSelect={selectPoi} onRoadSelect={selectRoad} />

        <aside className={`right-sidebar ${user ? "operator-sidebar" : "resident-sidebar"}`}>
          <RainfallPanel rainfall={rainfall} user={user} busy={operationsBusy} onUpdate={(rainfall24, rainfall1) => void handleRainfallUpdate(rainfall24, rainfall1)} />
          <AiRiskPanel health={health} summary={validation} user={user} recomputing={recomputing} onRecompute={() => void handleRecomputeRisk()} />
          {user?.role === "admin" ? <RiskTablePanel roads={roads} rainfall={rainfall} /> : null}
          <ShelterPanel shelters={shelters} user={user} busy={operationsBusy} onOccupancyUpdate={(shelter, occupancy, status) => void handleShelterOccupancyUpdate(shelter, occupancy, status)} onCreate={(payload) => void handleCreateShelter(payload)} />
          <MessagePanel user={user} messages={messages} roads={roads} busy={operationsBusy} onSend={(payload) => void handleSendMessage(payload)} onStatus={(message, status) => void handleMessageStatus(message, status)} onManageRoad={handleManageRoad} />
          {!user ? <WarningsPanel route={navigationRoute} warnings={routeResponse?.warnings ?? []} loading={routeLoading} /> : null}
          {!user ? <ExplanationPanel routeResponse={routeResponse} route={navigationRoute} modelLoaded={validation?.model_loaded ?? health?.model_loaded ?? false} /> : null}
          {!user ? <NavigationSimulator route={navigationRoute} reports={reports} roads={roads} onLocationChange={setCurrentLocation} onReroute={handleReroute} /> : null}
          <ReportStatusPanel reports={reports} user={user} onVerify={(report, decision) => void handleVerify(report, decision)} />
        </aside>
      </div>
      <footer className="app-footer"><span><i className="status-dot" /> {useMocks ? "Mock API mode" : "Connected to API"}</span><span>AI: {validation?.model_loaded || health?.model_loaded ? "IsolationForest loaded" : "heuristic flood propensity"}</span><span>{area.disclaimer ?? "Demo decision-support tool. Not an official emergency service."}</span></footer>

      <ReportModal road={reportOpen ? selectedRoad : null} submitting={reportSubmitting} source={user?.role === "admin" ? "control_room" : "field_official"} onClose={() => { setReportOpen(false); setMapMode("pan"); }} onSubmit={(payload) => void submitReport(payload)} />
    </main>
    </GoogleMapsProvider>
  );
}
