from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse

from config.config import DASHBOARD_OUTPUT
from streamlit_app.services.analytics_service import AnalyticsService
from streamlit_app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/download")
def download_dashboard(request: Request):
    repo = request.app.state.repo

    analytics_service = AnalyticsService(repo)
    results = analytics_service.compute_all()

    dashboard_service = DashboardService(repo)
    path = dashboard_service.generate(results)

    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=DASHBOARD_OUTPUT.name,
    )
