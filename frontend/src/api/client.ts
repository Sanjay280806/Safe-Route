import activeReportsMock from "../mocks/activeReports.json";
import blockedReportMock from "../mocks/blockedReportResponse.json";
import healthMock from "../mocks/health.json";
import loginMock from "../mocks/login.json";
import mapGeoJsonMock from "../mocks/mapGeoJSON.json";
import metaMock from "../mocks/meta.json";
import poisMock from "../mocks/pois.json";
import routeResponseMock from "../mocks/routeResponse.json";
import scenariosMock from "../mocks/scenarios.json";
import type {
  AreaMeta,
  BlockedReport,
  BlockedReportResponse,
  Health,
  LoginResponse,
  MapGeoJson,
  Poi,
  RoadProperties,
  RouteRequest,
  RouteResponse,
  RerouteRequest,
  Scenario,
} from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
export const useMocks = import.meta.env.VITE_USE_MOCKS !== "false";

function copy<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.error?.message ?? `Request failed (${response.status}).`);
  }

  return response.json() as Promise<T>;
}

function toRiskLevel(score: number): "low" | "moderate" | "high" | "critical" {
  if (score >= 0.75) return "critical";
  if (score >= 0.5) return "high";
  if (score >= 0.25) return "moderate";
  return "low";
}

function scenarioAdjustedMap(scenarioId: number): MapGeoJson {
  const map = copy(mapGeoJsonMock) as unknown as MapGeoJson;
  const adjustmentByScenario: Record<number, number> = { 1: -0.45, 2: -0.18, 3: 0, 4: 0.18 };
  const adjustment = adjustmentByScenario[scenarioId] ?? 0;

  map.features.forEach((feature) => {
    if (feature.geometry.type !== "LineString" || feature.properties.layer_type !== "road") return;
    const road = feature.properties as RoadProperties;
    const score = Math.max(0.04, Math.min(1, road.current_risk_score + adjustment));
    road.current_risk_score = Number(score.toFixed(2));
    road.current_risk_level = road.blocked ? "critical" : toRiskLevel(score);
    if (!road.blocked && score < 0.5) road.flood_status = "safe";
  });

  return map;
}

export async function getHealth(): Promise<Health> {
  return useMocks ? copy(healthMock) : request<Health>("/api/health");
}

export async function getArea(): Promise<AreaMeta> {
  return useMocks ? copy(metaMock) as AreaMeta : request<AreaMeta>("/api/meta/area");
}

export async function getScenarios(): Promise<Scenario[]> {
  return useMocks ? copy(scenariosMock) as Scenario[] : request<Scenario[]>("/api/scenarios");
}

export async function getPois(): Promise<Poi[]> {
  return useMocks ? copy(poisMock) as Poi[] : request<Poi[]>("/api/pois");
}

export async function getMapGeoJson(scenarioId: number): Promise<MapGeoJson> {
  return useMocks
    ? scenarioAdjustedMap(scenarioId)
    : request<MapGeoJson>(`/api/map/geojson?scenario_id=${scenarioId}&include=roads,pois,reports`);
}

export async function getActiveReports(): Promise<BlockedReport[]> {
  return useMocks ? copy(activeReportsMock) as BlockedReport[] : request<BlockedReport[]>("/api/reports/active");
}

function mockRouteForDestination(payload: RouteRequest | RerouteRequest): RouteResponse {
  const route = copy(routeResponseMock) as RouteResponse;
  const destination = payload.destination;
  let destinationPoint: [number, number] | null = null;
  if ("poi_id" in destination) {
    const poi = (poisMock as unknown as Poi[]).find((candidate) => candidate.id === destination.poi_id);
    if (poi) {
      route.destination = { type: "poi", poi_id: poi.id, name: poi.name, category: poi.category };
      destinationPoint = [poi.lon, poi.lat];
    }
  } else {
    route.destination = { type: "custom" };
    destinationPoint = [destination.lon, destination.lat];
  }

  const origin = "current_location" in payload ? payload.current_location : payload.origin;
  if (destinationPoint) {
    route.routes.forEach((candidate) => {
      const coordinates = candidate.geometry.coordinates;
      candidate.geometry.coordinates = coordinates.map((point, index) => {
        if (index === 0) return [origin.lon, origin.lat];
        if (index === coordinates.length - 1) return destinationPoint as [number, number];
        return point;
      });
    });
  }
  return route;
}

export async function createRoute(payload: RouteRequest): Promise<RouteResponse> {
  return useMocks
    ? mockRouteForDestination(payload)
    : request<RouteResponse>("/api/routes", { method: "POST", body: JSON.stringify(payload) });
}

export async function reroute(payload: RerouteRequest): Promise<RouteResponse> {
  return useMocks
    ? mockRouteForDestination(payload)
    : request<RouteResponse>("/api/routes/re-route", { method: "POST", body: JSON.stringify(payload) });
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  if (useMocks) {
    if (password !== "password" || !["reporter", "admin"].includes(username.toLowerCase())) {
      throw new Error("Use reporter/password or admin/password in mock mode.");
    }
    const response = copy(loginMock) as LoginResponse;
    response.user = {
      id: username.toLowerCase() === "admin" ? 1 : 2,
      username: username.toLowerCase(),
      role: username.toLowerCase() === "admin" ? "admin" : "reporter",
    };
    return response;
  }
  return request<LoginResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export async function submitBlockedReport(
  payload: { segment_id: number; source: string; note: string; flood_status: string },
  token: string,
): Promise<BlockedReportResponse> {
  if (useMocks) {
    const response = copy(blockedReportMock) as BlockedReportResponse;
    return { ...response, segment_id: payload.segment_id, report_id: Date.now() };
  }
  return request<BlockedReportResponse>("/api/reports/blocked", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
}

export async function verifyReport(
  reportId: number,
  decision: "confirm" | "reject",
  token: string,
): Promise<void> {
  if (useMocks) return;
  await request<unknown>(`/api/reports/${reportId}/verify`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ decision }),
  });
}
