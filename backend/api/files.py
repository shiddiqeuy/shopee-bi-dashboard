from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse

from database.repository import DuckDBRepository
from backend.deps import get_repo
from streamlit_app.services.etl_service import ETLService
from utils.logger import get_logger, log_error_context

log = get_logger(__name__)

router = APIRouter()

PUBLIC_FILE_ERROR = "Upload atau proses ETL gagal. Cek backend log untuk detail teknis."


@router.get("/")
def list_files():
    try:
        return {"files": ETLService.list_files()}
    except Exception as exc:
        log_error_context(log, "Failed to list files", exc=exc, stage="files")
        return JSONResponse(status_code=500, content={"detail": "Failed to list files"})


@router.put("/{filename}")
async def replace_file(filename: str, file: UploadFile = File(...), repo: DuckDBRepository = Depends(get_repo)):
    contents: bytes | None = None
    stage = "upload"
    try:
        service = ETLService(repo)
        contents = await file.read()
        saved_path = await asyncio.to_thread(service.save_upload, contents, filename)
        stage = "etl"
        result = await asyncio.to_thread(service.run, str(saved_path))
        return {
            "filename": filename,
            "replaced": True,
            "rows_loaded": result.get("rows_loaded", 0),
            "warehouse_built": result.get("warehouse_built", False),
            "total_rows": result.get("total_rows", 0),
            "status": result.get("status", "success"),
        }
    except Exception as exc:
        log_error_context(
            log,
            "Failed to replace file",
            exc=exc,
            stage=stage,
            filename=filename,
            uploaded_filename=file.filename,
            content_type=file.content_type,
            size_bytes=len(contents) if contents is not None else None,
        )
        return JSONResponse(status_code=500, content={"detail": PUBLIC_FILE_ERROR})


@router.delete("/{filename}")
def delete_file(filename: str):
    try:
        deleted = ETLService.delete_file(filename)
        return {"deleted": deleted}
    except Exception as exc:
        log_error_context(log, "Failed to delete file", exc=exc, stage="files", filename=filename)
        return JSONResponse(status_code=500, content={"detail": "Failed to delete file"})


@router.post("/clear")
def clear_all():
    try:
        count = ETLService.clear_all()
        return {"deleted_count": count}
    except Exception as exc:
        log_error_context(log, "Failed to clear files", exc=exc, stage="files")
        return JSONResponse(status_code=500, content={"detail": "Failed to clear files"})
