from fastapi import FastAPI

from app.routers.routes import router as routes_router


app = FastAPI(title="SafeRoute Benchmark Routing API", version="1.0")
app.include_router(routes_router, prefix="/api")


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "benchmark_layer": "ai_risk_and_routing",
        "model_loaded": False,
    }

