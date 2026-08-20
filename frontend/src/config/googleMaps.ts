export type Bbox = [number, number, number, number];

export function getGoogleMapsApiKey(): string {
  return import.meta.env.VITE_GOOGLE_MAPS_API_KEY?.trim() ?? "";
}

export function getGoogleMapsMapId(): string | undefined {
  const mapId = import.meta.env.VITE_GOOGLE_MAPS_MAP_ID?.trim();
  return mapId || undefined;
}

export function expandBbox(
  [south, west, north, east]: Bbox,
  padding = 0.0015,
): Bbox {
  return [south - padding, west - padding, north + padding, east + padding];
}

export function bboxToBoundsLiteral([south, west, north, east]: Bbox): google.maps.LatLngBoundsLiteral {
  return { south, west, north, east };
}
