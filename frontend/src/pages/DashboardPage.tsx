import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { createRoute, getActiveReports, getArea, getHealth, getMapGeoJson, getPois, getScenarios, getValidationSummary, recomputeRisk, reroute, submitBlockedReport, useMocks, verifyReport } from "../api/client";
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
import { SearchBar } from "../components/SearchBar";
import { WarningsPanel } from "../components/WarningsPanel";
import type { AreaMeta, BlockedReport, Destination, Health, LatLng, MapGeoJson, MapMode, Poi, PoiCategory, RoadFeature, Route, RouteMode, RouteResponse, Scenario, User, ValidationSummary } from "../types";
import { expandBbox, type Bbox } from "../config/googleMaps";

const fallbackArea: AreaMeta = {
  name: "West Velachery, Chennai",
  bbox: [12.965, 80.195, 12.995, 80.235],
  default_center: [12.98, 80.2125],
  default_zoom: 15,
  disclaimer: "Demo decision-support tool. Not an official emergency service.",
};

interface DashboardPageProps {
  user: User | null;
  token: string | null;
  onLogout: () => void;
}

export function DashboardPage({ user, token, onLogout }: DashboardPageProps) {
  const [area, setArea] = useState<AreaMeta>(fallbackArea);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
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
  const [routeMode, setRouteMode] = useState<RouteMode>("compare");
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
        const [nextArea, nextScenarios, nextPois, nextReports] = await Promise.all([getArea(), getScenarios(), getPois(), getActiveReports()]);
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
        setScenarios(nextScenarios);
        setPois(nextPois);
        setReports(nextReports);
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

  const filteredPois = useMemo(() => {
    const search = query.trim().toLowerCase();
    return pois.filter((poi) => {
      const matchesCategory = !category || poi.category === category;
      const searchable = `${poi.name} ${poi.category} ${poi.address ?? ""}`.toLowerCase();
      return matchesCategory && (!search || searchable.includes(search));
    });
  }, [category, pois, query]);

  const roads = useMemo(() => (mapData?.features.filter((feature): feature is RoadFeature => feature.geometry.type === "LineString" && feature.properties.layer_type === "road") ?? []), [mapData]);
  const displayedRoutes = useMemo(() => {
    if (!routeResponse) return [];
    return routeResponse.routes.filter((route) => routeMode === "compare" || route.route_type === routeMode);
  }, [routeMode, routeResponse]);
  const navigationRoute = useMemo(() => {
    if (!routeResponse) return null;
    return routeResponse.routes.find((route) => route.route_type === (routeMode === "short" ? "short" : "safe")) ?? routeResponse.routes[0] ?? null;
  }, [routeMode, routeResponse]);

  const selectPoi = useCallback((poi: Poi) => {
    setSelectedPoi(poi);
    setDestination({ type: "poi", poi });
    setDestinationLabel(poi.name);
    setFocusPoint({ lat: poi.lat, lon: poi.lon });
    setMapMode("pan");
    setNotification(`${poi.name} selected as destination.`);
  }, []);

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
    setNotification("Destination updated.");
  }, []);

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
      setNotification("Custom destination selected.");
    }
  }, [mapMode]);

  const changeScenario = async (nextScenarioId: number) => {
    setScenarioId(nextScenarioId);
    setRouteResponse(null);
    setOldRoute(null);
    setCurrentLocation(null);
    setNotification("Scenario changed. Road risk layer updated.");
    try {
      await loadMap(nextScenarioId);
      const nextValidation = await getValidationSummary();
      setValidation(nextValidation);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to update road risk layer.");
    }
  };

  const requestRoute = async () => {
    if (!origin || !destination) return;
    setRouteLoading(true);
    setError("");
    try {
      const destinationPayload = destination.type === "poi" ? { poi_id: destination.poi.id } : destination.location;
      const response = await createRoute({ origin, destination: destinationPayload, route_mode: routeMode === "short" ? "short" : "safe", scenario_id: scenarioId, include_alternatives: true });
      setRouteResponse(response);
      setOldRoute(null);
      setCurrentLocation(null);
      setNotification("Safe and shortest route options are ready.");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to find a route.");
    } finally {
      setRouteLoading(false);
    }
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
        include_alternatives: true,
      });
      const activeRouteType = routeMode === "short" ? "short" : "safe";
      const previousRoute = routeResponse?.routes.find((route) => route.route_type === activeRouteType) ?? routeResponse?.routes[0] ?? null;
      setOldRoute(previousRoute);
      setRouteResponse(response);
      setRouteMode("safe");
      setNotification(`Rerouted around ${report.road_name}. The previous path is shown in grey.`);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to reroute around the blocked road.");
    }
  }, [currentLocation, destination, routeMode, routeResponse]);

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
      setNotification(`AI risk recomputed for ${result.segments_updated} road segments.`);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to recompute flood risk.");
    } finally {
      setRecomputing(false);
    }
  };

  const mapCenter: [number, number] = area.default_center;
  const mapBounds: Bbox = expandBbox(area.bbox as Bbox);
  const activeScenario = scenarios.find((scenario) => scenario.id === scenarioId);

  return (
    <GoogleMapsProvider>
    <main className="dashboard-page">
      <header className="app-header">
        <div className="header-main-row">
          <Link className="brand" to="/"><span className="brand-mark">⌁</span><span>SafeRoute<small>Velachery</small></span></Link>
          <SearchBar value={query} onChange={setQuery} onClear={() => setQuery("")} />
          <div className="header-tools">
            <label className="scenario-select"><span>Scenario</span><select value={scenarioId} onChange={(event) => void changeScenario(Number(event.target.value))}>{scenarios.map((scenario) => <option key={scenario.id} value={scenario.id}>{scenario.name}</option>)}</select></label>
            {user ? <div className="user-menu"><span className="user-avatar">{user.username.slice(0, 1).toUpperCase()}</span><span><strong>{user.username}</strong><small>{user.role}</small></span><button type="button" onClick={onLogout}>Sign out</button></div> : <Link className="login-button" to="/login">Reporter login</Link>}
          </div>
        </div>
        <CategoryChips selected={category} onSelect={setCategory} />
      </header>

      {notification ? <div className="dashboard-notice" role="status"><span>✓</span>{notification}<button type="button" aria-label="Dismiss notification" onClick={() => setNotification("")}>×</button></div> : null}
      {error ? <div className="dashboard-error" role="alert"><span>!</span>{error}<button type="button" aria-label="Dismiss error" onClick={() => setError("")}>×</button></div> : null}

      <div className="dashboard-layout">
        <aside className="left-sidebar">
          <PlaceResultsPanel places={filteredPois} selectedPoi={selectedPoi} loading={loading} onSelect={selectPoi} />
          <RoutePanel
            origin={origin}
            originLabel={originLabel}
            destination={destination}
            destinationLabel={destinationLabel}
            routeMode={routeMode}
            routeResponse={routeResponse}
            loading={routeLoading}
            mapMode={mapMode}
            mapBounds={mapBounds}
            onOriginLabelChange={setOriginLabel}
            onDestinationLabelChange={setDestinationLabel}
            onOriginSelect={handleOriginSelect}
            onDestinationSelect={handleDestinationSelect}
            onRouteModeChange={setRouteMode}
            onMapModeChange={setMapMode}
            onRequestRoute={() => void requestRoute()}
            onClear={clearRoute}
            onPlacesError={setError}
          />
        </aside>

        <MapPanel center={mapCenter} zoom={area.default_zoom} bounds={mapBounds} mapData={mapData} pois={filteredPois} reports={reports} routes={displayedRoutes} oldRoute={oldRoute} origin={origin} destination={destination} currentLocation={currentLocation} mapMode={mapMode} focusPoint={focusPoint} onMapClick={handleMapClick} onPoiSelect={selectPoi} onRoadSelect={selectRoad} />

        <aside className="right-sidebar">
          <section className="scenario-card"><p className="eyebrow">Current model input</p><h2>{activeScenario?.name ?? "Loading scenario…"}</h2><p>{activeScenario?.description ?? "Local rainfall scenario"}</p><div><span><strong>{activeScenario?.rainfall_mm_24h ?? "–"}</strong> mm / 24h</span><span><strong>{activeScenario?.rainfall_mm_1h ?? "–"}</strong> mm / 1h</span></div></section>
          <AiRiskPanel health={health} summary={validation} user={user} recomputing={recomputing} onRecompute={() => void handleRecomputeRisk()} />
          <WarningsPanel warnings={routeResponse?.warnings ?? []} />
          <ExplanationPanel routeResponse={routeResponse} modelLoaded={validation?.model_loaded ?? health?.model_loaded ?? false} />
          <NavigationSimulator route={navigationRoute} reports={reports} roads={roads} onLocationChange={setCurrentLocation} onReroute={handleReroute} />
          <ReportStatusPanel reports={reports} user={user} onVerify={(report, decision) => void handleVerify(report, decision)} />
        </aside>
      </div>
      <footer className="app-footer"><span><i className="status-dot" /> {useMocks ? "Mock API mode" : "Connected to API"}</span><span>AI: {validation?.model_loaded || health?.model_loaded ? "IsolationForest loaded" : "heuristic flood propensity"}</span><span>{area.disclaimer ?? "Demo decision-support tool. Not an official emergency service."}</span></footer>

      <ReportModal road={reportOpen ? selectedRoad : null} submitting={reportSubmitting} onClose={() => { setReportOpen(false); setMapMode("pan"); }} onSubmit={(payload) => void submitReport(payload)} />
    </main>
    </GoogleMapsProvider>
  );
}
