from datetime import datetime
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends
from pathlib import Path
from services.ai_queue import enqueue_image
from services.ffmpeg_stream import (
    start_camera_hls, stop_camera_hls, cleanup_hls_directory, restart_camera_hls,
    start_supervised_hls, stop_supervised_hls, restart_supervised_hls
)
from schemas.camera import CameraCreate, CameraResponse, CameraUpdate
from crud.camera import create_camera, get_all_cameras, update_camera, delete_camera, get_camera_by_id
from sqlmodel.ext.asyncio.session import AsyncSession
from core.dependencies import get_db
from typing import List, Dict
import subprocess
import logging

router = APIRouter(tags=["cameras"])

camera_processes: dict[int, object] = {}

BASE_DIR = Path(__file__).resolve().parent.parent.parent
IMAGE_DIR = BASE_DIR / "uploaded_images" / "raw"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

@router.get("", response_model=List[CameraResponse])
async def list_cameras(db: AsyncSession = Depends(get_db)):
    try:
        return await get_all_cameras(db)
    except Exception as e:
        logging.exception("Failed to list cameras")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=CameraResponse)
async def add_camera(camera_in: CameraCreate, db: AsyncSession = Depends(get_db)):
    camera = await create_camera(db, camera_in)
    # Start supervised ffmpeg so it restarts on failure
    ctrl = start_supervised_hls(camera.id, camera.rtsp_url)
    camera_processes[camera.id] = ctrl
    return camera

@router.patch("/{camera_id}", response_model=CameraResponse)
async def update_camera_endpoint(
    camera_id: int,
    camera_in: CameraUpdate,
    db: AsyncSession = Depends(get_db)
):
    camera = await get_camera_by_id(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    update_data = camera_in.dict(exclude_unset=True)
    
    update_data.pop("last_snapshot", None)
    
    updated_camera = await update_camera(db, camera, update_data)
    
    ctrl = camera_processes.get(camera_id)

    if 'rtsp_url' in update_data:
        new_url = update_data['rtsp_url']
        # restart supervised process with new URL
        new_ctrl = restart_supervised_hls(camera_id, new_url)
        camera_processes[camera_id] = new_ctrl

    if 'is_active' in update_data:
        if not update_data['is_active']:
            stop_supervised_hls(camera_id)
            camera_processes.pop(camera_id, None)
        else:
            if camera_id not in camera_processes and updated_camera.rtsp_url:
                camera_processes[camera_id] = start_supervised_hls(camera_id, updated_camera.rtsp_url)
    
    return updated_camera

@router.delete("/{camera_id}")
async def delete_camera_endpoint(
    camera_id: int,
    db: AsyncSession = Depends(get_db)
):
    camera = await get_camera_by_id(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # Stop FFmpeg và cleanup thư mục HLS
    ctrl = camera_processes.pop(camera_id, None)
    stop_supervised_hls(camera_id)
    cleanup_hls_directory(camera_id)
    
    await delete_camera(db, camera)
    return {"detail": "Camera deleted successfully"}

@router.post("/{camera_id}/snapshot")
async def upload_snapshot(
    camera_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image file")

    filename = f"{camera_id}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
    path = IMAGE_DIR / filename

    content = await file.read()
    path.write_bytes(content)

    background_tasks.add_task(enqueue_image, str(path), camera_id)

    return {"filename": filename, "status": "queued for AI"}