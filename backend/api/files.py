from __future__ import annotations

import asyncio
import traceback

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse

from database.repository import DuckDBRepository
from backend.deps import get_repo
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


@router.put("/{filename}")
async def replace_file(filename: str, file: UploadFile = File(...), repo: DuckDBRepository = Depends(get_repo)):
    try:
        service = ETLService(repo)
        contents = await file.read()
        saved_path = await asyncio.to_thread(service.save_upload, contents, filename)
        result = await asyncio.to_thread(service.run, str(saved_path))
        return {
            "filename": filename,
            "replaced": True,
            "rows_loaded": result.get("rows_loaded", 0),
            "warehouse_built": result.get("warehouse_built", False),
            "total_rows": result.get("total_rows", 0),
            "status": result.get("status", "success"),
        }
    except Exception:
        log.error("Failed to replace file %s\n%s", filename, traceback.format_exc())
        return JSONResponse(status_code=500, content={"detail": "Failed to replace file"})


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
