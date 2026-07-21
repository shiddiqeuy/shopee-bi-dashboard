from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from config.config import DASHBOARD_OUTPUT
from database.repository import DuckDBRepository
from backend.deps import get_repo
from streamlit_app.services.analytics_service import AnalyticsService
from streamlit_app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/download")
async def download_dashboard(repo: DuckDBRepository = Depends(get_repo)):
    analytics_service = AnalyticsService(repo)
    results = await asyncio.to_thread(analytics_service.compute_all)

    dashboard_service = DashboardService(repo)
    path = await asyncio.to_thread(dashboard_service.generate, results)

    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=DASHBOARD_OUTPUT.name,
    )
