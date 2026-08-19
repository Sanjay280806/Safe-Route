# Agent Rules

Implement ONLY the benchmark layer.

Do NOT implement:
- chatbot
- live weather unless explicitly enabled
- satellite imagery
- CCTV vision
- voice navigation
- multi-city support
- production auth
- complex microservices

Use:
- FastAPI backend
- SQLite database
- React + Vite frontend
- Leaflet map
- seeded local data
- mock fallback data

If data is missing:
- create placeholder data in /data/mock
- clearly mark it as placeholder
- do not invent real shelter/hospital names as official data

Every feature must be testable using:
- backend health endpoint
- API endpoints
- frontend build
- manual demo checklist