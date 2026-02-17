"""
Brand Files Router
Handles file upload, listing, and deletion with Supabase Storage.
GET    /brand-files/?client_id={id}  - List files
POST   /brand-files/upload/          - Upload file
DELETE /brand-files/{file_id}/       - Delete file
"""
from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Query
from typing import Optional
import logging
import uuid
from datetime import datetime, timezone

from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.supabase_service import get_supabase_service
from .models import BrandFileProfile, BrandFileResponse, BrandFileListResponse

logger = logging.getLogger(__name__)
router = APIRouter()

# Plan limits for brand files
PLAN_LIMITS = {
    "basic": {"max_files": 3, "max_size_mb": 10, "total_mb": 25},
    "pro": {"max_files": 10, "max_size_mb": 25, "total_mb": 100},
    "enterprise": {"max_files": 30, "max_size_mb": 50, "total_mb": 500},
}

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "image/png",
    "image/jpeg",
    "image/webp",
}


@router.get("/", response_model=BrandFileListResponse)
async def list_brand_files(
    client_id: str = Query(..., description="Client UUID"),
    authorization: Optional[str] = Header(None)
) -> BrandFileListResponse:
    """
    List all brand files for a client.
    Returns file metadata and total storage usage.
    """
    try:
        user = await get_current_user(authorization)
        supabase = get_supabase_service()

        result = supabase.client.table("brand_files")\
            .select("*")\
            .eq("client_id", client_id)\
            .order("created_at", desc=True)\
            .execute()

        files = result.data or []
        total_size = sum(f.get("file_size", 0) for f in files)

        return BrandFileListResponse(
            success=True,
            data=[BrandFileProfile(**f) for f in files],
            total=len(files),
            total_size=total_size,
            message=f"Found {len(files)} file(s)"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing brand files: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while listing files"
        )


@router.post("/upload/", response_model=BrandFileResponse)
async def upload_brand_file(
    client_id: str = Query(..., description="Client UUID"),
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
) -> BrandFileResponse:
    """
    Upload brand file to Supabase Storage.
    Validates plan limits and file types.
    """
    try:
        user = await get_current_user(authorization)
        supabase = get_supabase_service()

        # Validate mime type
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de archivo no permitido: {file.content_type}"
            )

        # Get client plan
        client_result = supabase.client.table("clients")\
            .select("plan")\
            .eq("id", client_id)\
            .single()\
            .execute()

        if not client_result.data:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        plan = client_result.data.get("plan", "basic")
        limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["basic"])

        # Check existing files
        existing = supabase.client.table("brand_files")\
            .select("file_size")\
            .eq("client_id", client_id)\
            .execute()

        existing_files = existing.data or []
        existing_count = len(existing_files)
        existing_total_mb = sum(f.get("file_size", 0) for f in existing_files) / (1024 * 1024)

        # Validate file count limit
        if existing_count >= limits["max_files"]:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"Límite alcanzado. Plan {plan.capitalize()} permite "
                    f"{limits['max_files']} archivos. Actualiza tu plan para más espacio."
                )
            )

        # Read file content and check size
        file_content = await file.read()
        file_size_mb = len(file_content) / (1024 * 1024)

        if file_size_mb > limits["max_size_mb"]:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Archivo muy grande ({file_size_mb:.1f}MB). "
                    f"Máximo {limits['max_size_mb']}MB por archivo en plan {plan.capitalize()}."
                )
            )

        # Validate total storage limit
        if existing_total_mb + file_size_mb > limits["total_mb"]:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"Espacio insuficiente. Plan {plan.capitalize()} tiene "
                    f"{limits['total_mb']}MB total. Usando {existing_total_mb:.1f}MB. "
                    f"Actualiza tu plan."
                )
            )

        # Upload to Supabase Storage
        file_id = str(uuid.uuid4())
        file_ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
        storage_path = f"{client_id}/{file_id}.{file_ext}"

        storage_result = supabase.client.storage\
            .from_("brand-guides")\
            .upload(storage_path, file_content, {"content-type": file.content_type})

        # Get public URL
        url_result = supabase.client.storage\
            .from_("brand-guides")\
            .get_public_url(storage_path)

        # Save to brand_files table
        db_result = supabase.client.table("brand_files").insert({
            "client_id": client_id,
            "file_name": file.filename,
            "file_path": storage_path,
            "file_size": len(file_content),
            "mime_type": file.content_type,
            "storage_url": url_result,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()

        if not db_result.data:
            raise HTTPException(
                status_code=500,
                detail="Error guardando referencia del archivo"
            )

        logger.info(
            f"Brand file uploaded: {file.filename} for client {client_id} "
            f"({file_size_mb:.1f}MB)"
        )

        return BrandFileResponse(
            success=True,
            data=BrandFileProfile(**db_result.data[0]),
            message=f"Archivo {file.filename} subido exitosamente"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading brand file: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while uploading file"
        )


@router.delete("/{file_id}/", response_model=BrandFileResponse)
async def delete_brand_file(
    file_id: str,
    authorization: Optional[str] = Header(None)
) -> BrandFileResponse:
    """
    Delete brand file from Storage and database.
    """
    try:
        user = await get_current_user(authorization)
        supabase = get_supabase_service()

        # Get file record
        file_result = supabase.client.table("brand_files")\
            .select("*")\
            .eq("id", file_id)\
            .single()\
            .execute()

        if not file_result.data:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        file_record = file_result.data

        # Delete from Storage
        supabase.client.storage\
            .from_("brand-guides")\
            .remove([file_record["file_path"]])

        # Delete from DB
        supabase.client.table("brand_files")\
            .delete()\
            .eq("id", file_id)\
            .execute()

        logger.info(f"Brand file deleted: {file_record['file_name']} (ID: {file_id})")

        return BrandFileResponse(
            success=True,
            message=f"Archivo {file_record['file_name']} eliminado"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting brand file: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while deleting file"
        )
