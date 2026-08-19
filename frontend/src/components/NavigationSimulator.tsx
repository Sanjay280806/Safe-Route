import { useEffect, useMemo, useRef, useState } from "react";
import type { BlockedReport, LatLng, RoadFeature, Route } from "../types";

function pointsClose(a: [number, number], b: [number, number]): boolean {
  return Math.abs(a[0] - b[0]) < 0.00015 && Math.abs(a[1] - b[1]) < 0.00015;
}

function routeContainsRoad(route: Route, road: RoadFeature): boolean {
  const [roadStart, roadEnd] = road.geometry.coordinates;
  const points = route.geometry.coordinates;
  return points.some((point) => pointsClose(point, roadStart)) && points.some((point) => pointsClose(point, roadEnd));
}

interface NavigationSimulatorProps {
  route: Route | null;
  reports: BlockedReport[];
  roads: RoadFeature[];
  onLocationChange: (location: LatLng | null) => void;
  onReroute: (report: BlockedReport) => Promise<void>;
}

export function NavigationSimulator({ route, reports, roads, onLocationChange, onReroute }: NavigationSimulatorProps) {
  const [running, setRunning] = useState(false);
  const [waypoint, setWaypoint] = useState(0);
  const [status, setStatus] = useState<"ready" | "moving" | "rerouting" | "arrived">("ready");
  const rerouteInFlight = useRef(false);
  const coordinates = useMemo(() => route?.geometry.coordinates ?? [], [route]);

  useEffect(() => {
    setRunning(false);
    setWaypoint(0);
    setStatus("ready");
    onLocationChange(null);
  }, [route, onLocationChange]);

  useEffect(() => {
    if (!running || !route || coordinates.length === 0) return;

    const timer = window.setInterval(() => {
      setWaypoint((current) => {
        const next = Math.min(current + 1, coordinates.length - 1);
        const [lon, lat] = coordinates[next];
        onLocationChange({ lat, lon });

        const blockedReport = reports.find((report) => {
          if (report.verification_status !== "confirmed") return false;
          const road = roads.find((candidate) => candidate.properties.segment_id === report.segment_id);
          return road ? routeContainsRoad(route, road) : false;
        });

        if (next > 0 && blockedReport && !rerouteInFlight.current) {
          rerouteInFlight.current = true;
          setRunning(false);
          setStatus("rerouting");
          void onReroute(blockedReport).finally(() => {
            rerouteInFlight.current = false;
          });
          return current;
        }

        if (next === coordinates.length - 1) {
          setRunning(false);
          setStatus("arrived");
        }
        return next;
      });
    }, 1250);
    return () => window.clearInterval(timer);
  }, [coordinates, onLocationChange, onReroute, reports, roads, route, running]);

  if (!route) {
    return (
      <section className="panel navigation-panel disabled">
        <p className="eyebrow">Demo movement</p><h2>Navigation simulation</h2>
        <p>Request a route to simulate movement and automatic rerouting.</p>
      </section>
    );
  }

  const progress = coordinates.length > 1 ? Math.round((waypoint / (coordinates.length - 1)) * 100) : 0;
  const blockedOnRoute = reports.some((report) => {
    const road = roads.find((candidate) => candidate.properties.segment_id === report.segment_id);
    return report.verification_status === "confirmed" && road && routeContainsRoad(route, road);
  });

  return (
    <section className="panel navigation-panel">
      <div className="panel-heading"><div><p className="eyebrow">Demo movement</p><h2>Navigation simulation</h2></div><span className={`nav-status ${status}`}>{status}</span></div>
      <p className="navigation-description">
        {blockedOnRoute ? "A confirmed block is on this route. Start simulation to demonstrate automatic rerouting." : "The location marker will move along the selected route."}
      </p>
      <div className="progress-track" aria-label={`Navigation progress ${progress}%`}><span style={{ width: `${progress}%` }} /></div>
      <div className="navigation-controls">
        <button type="button" className="primary-button" disabled={running || status === "rerouting" || status === "arrived"} onClick={() => { setStatus("moving"); setRunning(true); }}>
          {status === "rerouting" ? "Rerouting…" : status === "arrived" ? "Arrived" : running ? "Navigating…" : "Start navigation"}
        </button>
        <button type="button" className="secondary-button" disabled={!running && waypoint === 0} onClick={() => { setRunning(false); setWaypoint(0); setStatus("ready"); onLocationChange(null); }}>Reset</button>
      </div>
    </section>
  );
}
