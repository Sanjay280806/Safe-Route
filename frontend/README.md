# SafeRoute frontend

React + Vite dashboard for the SafeRoute Velachery benchmark layer. It uses the **Google Maps JavaScript API** (`@vis.gl/react-google-maps`) and the frozen API field names from `docs/API_CONTRACT.md`.

## Run locally

```powershell
cd frontend
npm install
npm run dev
```

The app starts in mock mode by default. Its local response fixtures live in `src/mocks/` and are intentionally marked as placeholder data.

## Environment variables

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCKS=false
VITE_GOOGLE_MAPS_API_KEY=your_google_maps_api_key
VITE_GOOGLE_MAPS_MAP_ID=DEMO_MAP_ID
```

Never commit your real API key. Copy from `.env.example` and fill in values locally.

### Google Cloud APIs to enable

Enable these for your Google Cloud project and restrict the key to your dev/production origins:

1. **Maps JavaScript API** — interactive map tiles and controls
2. **Places API** — origin/destination Places Autocomplete in the route panel
3. **Geocoding API** (recommended) — address resolution for autocomplete selections
4. **Directions API** (optional) — SafeRoute routing still uses the backend; Google Directions is not required for safe-route calculation

For production markers, create a [Map ID](https://developers.google.com/maps/documentation/javascript/map-ids) in Google Cloud Console and set `VITE_GOOGLE_MAPS_MAP_ID`. `DEMO_MAP_ID` works for local development.

## Production check

```powershell
npm run build
```

## Manual demo checklist

- [ ] Load `/`: Google Maps renders the Velachery area with coloured road-risk overlays and POI markers.
- [ ] Pan and zoom within the Velachery bounds; the map should not drift far outside the service area.
- [ ] Use origin/destination Places Autocomplete or **Set on map** to pick endpoints.
- [ ] Use the search and category chips: the local POI result list and map markers filter together.
- [ ] Select a POI, choose `Safest`, `Shortest`, or `Compare`, then click **Get route**: backend route lines, summaries, warnings, and explanation panel render.
- [ ] Change the rainfall scenario: the mocked road-risk layer changes colour and route output is cleared.
- [ ] Open `/login` and use `reporter/password`: clicking a road opens the report modal and submitting it updates its map status and active-reports panel.
- [ ] Log in as `admin/password`: pending field reports expose confirm/reject controls.
- [ ] Report **Low-Lying Shortcut**, request the shortest route, then click **Start navigation**: the position marker advances, detects the confirmed report, and switches to a new safe route while retaining the old route in grey.

This frontend intentionally excludes chatbot, live weather, satellite/CCTV, voice navigation, multi-city support, production authentication, and backend/AI changes.
