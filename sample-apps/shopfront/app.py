import os
import time

from fastapi import FastAPI, HTTPException, Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)

app = FastAPI(title="shopfront")

VALID_MODES = {"normal", "slow", "leak", "crash"}
state = {"mode": "normal"}
leaked_memory = []  # grows in "leak" mode

REQUESTS = Counter(
    "shop_http_requests_total",
    "Total HTTP requests",
    ["path", "status"],
)
LATENCY = Histogram(
    "shop_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["path"],
)


@app.middleware("http")
async def track_metrics(request: Request, call_next):
    start = time.perf_counter()
    status = "500"
    try:
        response = await call_next(request)
        status = str(response.status_code)
        return response
    finally:
        route = request.scope.get("route")
        path = route.path if route else "unmatched"
        REQUESTS.labels(path=path, status=status).inc()
        LATENCY.labels(path=path).observe(time.perf_counter() - start)


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
def health():
    return {"status": "ok", "mode": state["mode"]}


@app.get("/checkout")
def checkout():
    mode = state["mode"]
    if mode == "slow":
        time.sleep(3)  # simulate a slow dependency
    elif mode == "leak":
        leaked_memory.append(bytearray(10 * 1024 * 1024))  # +10 MB per request
    elif mode == "crash":
        os._exit(1)  # hard crash, like a real bug
    return {"order": "confirmed", "mode": mode}


@app.post("/admin/mode/{mode}")
def set_mode(mode: str):
    if mode not in VALID_MODES:
        raise HTTPException(
            status_code=400,
            detail=f"mode must be one of {sorted(VALID_MODES)}",
        )
    state["mode"] = mode
    return {"mode": mode}
