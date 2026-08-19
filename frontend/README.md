# SafeRoute frontend

React + Vite dashboard for the SafeRoute Velachery benchmark layer. It uses Leaflet and the frozen API field names from `docs/API_CONTRACT.md`.

## Run locally

```powershell
cd frontend
npm install
npm run dev
```

The app starts in mock mode by default. Its local response fixtures live in `src/mocks/` and are intentionally marked as placeholder data.

To connect to the frozen backend contract later, set the following in `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCKS=false
```

## Production check

```powershell
npm run build
```

## Manual demo checklist

- [ ] Load `/`: West Velachery map renders with coloured road-risk lines and placeholder POI markers.
- [ ] Use the search and category chips: the local POI result list and map markers filter together.
- [ ] Select a POI, choose `Safest`, `Shortest`, or `Compare`, then click **Get route**: route lines, route summaries, warnings, and the explanation panel render.
- [ ] Change the rainfall scenario: the mocked road-risk layer changes colour and route output is cleared.
- [ ] Click **Set on map** beside either route endpoint, then click the map: the chosen origin or custom destination updates.
- [ ] Open `/login` and use `reporter/password`: clicking a road opens the report modal and submitting it updates its map status and active-reports panel.
- [ ] Log in as `admin/password`: pending field reports expose confirm/reject controls.
- [ ] Report **Low-Lying Shortcut**, request the shortest route, then click **Start navigation**: the position marker advances, detects the confirmed report, and switches to a new safe route while retaining the old route in grey.

This frontend intentionally excludes chatbot, live weather, satellite/CCTV, voice navigation, multi-city support, production authentication, and backend/AI changes.
