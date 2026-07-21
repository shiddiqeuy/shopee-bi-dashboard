from __future__ import annotations

import traceback

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from streamlit_app.services.etl_service import ETLService
from utils.logger import get_logger

log = get_logger(__name__)

router = APIRouter()


@router.get("/")
def list_files():
    try:
        return {"files": ETLService.list_files()}
    except Exception:
        log.error("Failed to list files\n%s", traceback.format_exc())
        return JSONResponse(status_code=500, content={"detail": "Failed to list files"})


@router.delete("/{filename}")
def delete_file(filename: str):
    try:
        deleted = ETLService.delete_file(filename)
        return {"deleted": deleted}
    except Exception:
        log.error("Failed to delete file %s\n%s", filename, traceback.format_exc())
        return JSONResponse(status_code=500, content={"detail": "Failed to delete file"})


@router.post("/clear")
def clear_all():
    try:
        count = ETLService.clear_all()
        return {"deleted_count": count}
    except Exception:
        log.error("Failed to clear files\n%s", traceback.format_exc())
        return JSONResponse(status_code=500, content={"detail": "Failed to clear files"})
