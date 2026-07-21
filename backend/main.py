from __future__ import annotations

import sys
import traceback
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database.connection import close_pool, init_pool
from utils.logger import get_logger

from backend.api import etl, analytics, dashboard, files

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_pool()
    yield
    close_pool()


app = FastAPI(title="Shopee BI Dashboard API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(etl.router, prefix="/api/etl", tags=["ETL"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(files.router, prefix="/api/files", tags=["Files"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    log.error("Unhandled exception on %s %s\n%s", request.method, request.url.path, traceback.format_exc())
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/api/health")
def health():
    return {"status": "ok"}
