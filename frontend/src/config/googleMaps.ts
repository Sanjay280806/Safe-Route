/** Geographic bounding box as [south, west, north, east]. */
export type Bbox = [number, number, number, number];

/** Velachery and surrounding connecting roads — slightly wider than backend demo bbox. */
export const VELACHERY_FALLBACK_BBOX: Bbox = [12.955, 80.185, 13.005, 80.245];

export function getGoogleMapsApiKey(): string {
  return import.meta.env.VITE_GOOGLE_MAPS_API_KEY?.trim() ?? "";
}

export function getGoogleMapsMapId(): string {
  return import.meta.env.VITE_GOOGLE_MAPS_MAP_ID?.trim() || "DEMO_MAP_ID";
}

export function bboxToBoundsLiteral(bbox: Bbox): google.maps.LatLngBoundsLiteral {
  return { south: bbox[0], west: bbox[1], north: bbox[2], east: bbox[3] };
}

/** Expand backend bbox so connecting roads around Velachery stay reachable. */
export function expandBbox(bbox: Bbox, padding = 0.01): Bbox {
  return [bbox[0] - padding, bbox[1] - padding, bbox[2] + padding, bbox[3] + padding];
}

export function bboxCenter(bbox: Bbox): google.maps.LatLngLiteral {
  return {
    lat: (bbox[0] + bbox[2]) / 2,
    lng: (bbox[1] + bbox[3]) / 2,
  };
}

export const GOOGLE_MAPS_LIBRARIES = ["places", "geometry"] as const;

export const GOOGLE_MAPS_SETUP_DOCS = [
  "Maps JavaScript API",
  "Places API (Autocomplete)",
  "Geocoding API (optional, for address lookup)",
  "Directions API (optional — SafeRoute routing uses the backend)",
] as const;
