export type Role = "reporter" | "admin";

export interface User {
  id: number;
  username: string;
  role: Role;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in?: number;
  user: User;
}

export interface Health {
  status: string;
  model_loaded: boolean;
  active_scenario_id: number;
  road_count: number;
  poi_count: number;
}

export interface AreaMeta {
  name: string;
  bbox: [number, number, number, number];
  default_center: [number, number];
  default_zoom: number;
  disclaimer?: string;
}

export interface Scenario {
  id: number;
  name: string;
  description?: string;
  rainfall_mm_24h: number;
  rainfall_mm_1h: number;
  source?: string;
  is_active: boolean;
}

export type PoiCategory =
  | "shelter"
  | "hospital"
  | "clinic"
  | "police_station"
  | "petrol_bunk"
  | "fire_station"
  | "pharmacy"
  | "school"
  | "community_center";

export interface Poi {
  id: number;
  external_id?: string;
  name: string;
  category: PoiCategory;
  lat: number;
  lon: number;
  address?: string;
  phone?: string;
  status: "open" | "closed" | "unknown";
  nearest_node_id?: number;
  source?: string;
  notes?: string;
  distance_m?: number | null;
}

export interface LatLng {
  lat: number;
  lon: number;
}

export type Destination =
  | { type: "poi"; poi: Poi }
  | { type: "custom"; location: LatLng };

export type MapMode = "pan" | "set_origin" | "set_destination" | "report_road";
export type RouteMode = "safe" | "short" | "compare";
export type RiskLevel = "low" | "moderate" | "high" | "critical";

export interface RoadProperties {
  layer_type: "road";
  segment_id: number;
  name: string;
  road_type?: string;
  current_risk_score: number;
  current_risk_level: RiskLevel;
  predicted_time_to_high_risk_min: number | null;
  blocked: boolean;
  flood_status: string;
}

export interface RoadFeature {
  type: "Feature";
  geometry: { type: "LineString"; coordinates: [number, number][] };
  properties: RoadProperties;
}

export interface MapGeoJson {
  type: "FeatureCollection";
  features: Array<RoadFeature | { type: "Feature"; geometry: { type: "Point" }; properties: Record<string, unknown> }>;
}

export interface RouteGeometry {
  type: "LineString";
  coordinates: [number, number][];
}

export interface Route {
  route_type: "safe" | "short";
  distance_m: number;
  duration_min: number;
  cost_score?: number;
  avg_risk_score: number;
  high_risk_segments_count: number;
  blocked_segments_encountered: number;
  predicted_risk_warnings_count: number;
  geometry: RouteGeometry;
}

export interface RouteWarning {
  warning_type: "predicted_flood_before_arrival" | "blocked_ahead" | "high_risk_area";
  segment_id?: number;
  road_name: string;
  eta_to_segment_min?: number;
  predicted_time_to_high_risk_min?: number;
  message: string;
  created_at?: string;
}

export interface RouteResponse {
  request_id: number;
  destination: {
    type: "poi" | "custom";
    poi_id?: number;
    name?: string;
    category?: PoiCategory;
  };
  routes: Route[];
  warnings: RouteWarning[];
  explanation: {
    safe_route_adds_min: number;
    high_risk_segments_avoided: number;
    blocked_segments_avoided: number;
    summary: string;
  };
}

export interface BlockedReport {
  id: number;
  segment_id: number;
  road_name: string;
  source: string;
  verification_status: "confirmed" | "pending" | "rejected";
  note: string;
  created_at: string;
}

export interface BlockedReportResponse {
  report_id: number;
  segment_id: number;
  verification_status: "confirmed" | "pending" | "rejected";
  credibility_score: number;
  road_status: {
    blocked: boolean;
    flood_status: string;
    current_risk_level: RiskLevel;
  };
}

export interface RouteRequest {
  origin: LatLng;
  destination: { poi_id: number } | LatLng;
  route_mode: "safe" | "short";
  scenario_id: number;
  include_alternatives: boolean;
}

export interface RerouteRequest {
  current_location: LatLng;
  destination: { poi_id: number } | LatLng;
  reason: "blocked_ahead" | "predicted_risk";
  route_mode: "safe" | "short";
}
