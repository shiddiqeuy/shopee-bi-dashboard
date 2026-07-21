from __future__ import annotations

from fastapi import APIRouter

from streamlit_app.services.etl_service import ETLService

router = APIRouter()


@router.get("/")
def list_files():
    return {"files": ETLService.list_files()}


@router.delete("/{filename}")
def delete_file(filename: str):
    deleted = ETLService.delete_file(filename)
    return {"deleted": deleted}


@router.post("/clear")
def clear_all():
    count = ETLService.clear_all()
    return {"deleted_count": count}
