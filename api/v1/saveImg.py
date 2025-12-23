from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import PlainTextResponse

import os
import time
from PIL import Image
import io
import httpx
import logging
from datetime import datetime, timezone, timedelta

# Use timezone GMT+7 for filenames/timestamps
TZ = timezone(timedelta(hours=7))

router = APIRouter(tags=["saveImg"])  # Routes under /api/v1/... typically

BASE_FOLDER = "/home/theanh/Desktop/SmartFarm/Smart_farm/ai-worker/capture_photo"


def _ensure_camera_folders(camera_id: str):
    base = os.path.join(BASE_FOLDER, str(camera_id))
    photo_folder = os.path.join(base, "image")
    timelapse_folder = os.path.join(base, "timelapse")
    os.makedirs(photo_folder, exist_ok=True)
    os.makedirs(timelapse_folder, exist_ok=True)
    return photo_folder, timelapse_folder


@router.get("/")
async def index():
    return {"message": "ESP32-CAM Image Server is Running"}


@router.post("/create_folder/{camera_id}")
async def create_folder(camera_id: str):
    """Create folders for a given camera. No DB updates performed."""
    photo_folder, timelapse_folder = _ensure_camera_folders(camera_id)
    return {"photo_folder": photo_folder, "timelapse_folder": timelapse_folder}


@router.post("/photo/{camera_id}")
async def save_photo(camera_id: str, request: Request):
    data = await request.body()
    if not data:
        raise HTTPException(status_code=400, detail="Empty data")
    try:
        Image.open(io.BytesIO(data)).verify()
        dt = datetime.now(TZ)
        ts_str = dt.strftime("%y.%m.%d.%H.%M.%S")
        photo_folder, _ = _ensure_camera_folders(camera_id)
        filename = os.path.join(photo_folder, f"{ts_str}.jpg")
        with open(filename, "wb") as f:
            f.write(data)
        return PlainTextResponse("OK", status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JPEG: {e}")


@router.post("/photo")
async def save_photo_noid(request: Request):
    """Accept photo uploads from cameras that POST without camera_id in URL.
    Determine camera_id from `X-Camera-ID` header or client host fallback.
    Supports raw binary body or multipart form uploads (file field).
    """
    # determine camera id
    camera_id = request.headers.get("X-Camera-ID")
    client = request.client
    client_host = None
    if client:
        client_host = client.host
    if not camera_id:
        camera_id = client_host or "camera_unknown"

    # try body first
    data = await request.body()
    if not data:
        # try form upload
        try:
            form = await request.form()
            for v in form.values():
                # v can be UploadFile or plain value
                if hasattr(v, "file"):
                    data = await v.read()
                    break
        except Exception:
            data = b""

    if not data:
        logging.warning("Received empty photo data from %s", client_host)
        raise HTTPException(status_code=400, detail="Empty data")

    try:
        Image.open(io.BytesIO(data)).verify()
    except Exception as e:
        logging.warning("Image verification failed from %s: %s", client_host, e)
        # still attempt to save raw data, but return 400 to indicate verification failed
        photo_folder, _ = _ensure_camera_folders(camera_id)
        dt = datetime.now(TZ)
        ts_str = dt.strftime("%Y.%m.%d.%H.%M.%S")
        filename = os.path.join(photo_folder, f"{ts_str}.raw.jpg")
        with open(filename, "wb") as f:
            f.write(data)
        raise HTTPException(status_code=400, detail=f"Invalid JPEG, raw saved: {filename}")

    dt = datetime.now(TZ)
    ts_str = dt.strftime("%Y.%m.%d.%H.%M.%S")
    photo_folder, _ = _ensure_camera_folders(camera_id)
    filename = os.path.join(photo_folder, f"{ts_str}.jpg")
    with open(filename, "wb") as f:
        f.write(data)
    logging.info("Saved photo from %s to %s", client_host, filename)
    return PlainTextResponse("OK", status_code=200)


@router.post("/timelapse/{camera_id}")
async def save_timelapse(camera_id: str, request: Request):
    data = await request.body()
    if not data:
        raise HTTPException(status_code=400, detail="Empty data")
    try:
        Image.open(io.BytesIO(data)).verify()
        dt = datetime.now(TZ)
        ts_str = dt.strftime("%Y.%m.%d.%H.%M.%S")
        _, timelapse_folder = _ensure_camera_folders(camera_id)
        filename = os.path.join(timelapse_folder, f"{ts_str}.timelapse.jpg")
        with open(filename, "wb") as f:
            f.write(data)
        return PlainTextResponse("OK", status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JPEG: {e}")


@router.post("/capture/{camera_host}/{camera_id}")
async def capture_and_save(camera_host: str, camera_id: str):
    """Server-side proxy: call camera capture endpoint and save image into camera_id folder.
    This avoids CORS issues when frontend cannot call camera directly.
    Example: POST /api/v1/saveImg/capture/192.168.31.189/cam123"""
    url = f"http://{camera_host}/capture_photo"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to reach camera: {e}")

    if resp.status_code != 200 or not resp.content:
        raise HTTPException(status_code=502, detail=f"Camera returned {resp.status_code}")

    data = resp.content
    try:
        Image.open(io.BytesIO(data)).verify()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image from camera: {e}")

    dt = datetime.now(TZ)
    ts_str = dt.strftime("%Y.%m.%d.%H.%M.%S")
    photo_folder, _ = _ensure_camera_folders(camera_id)
    filename = os.path.join(photo_folder, f"{ts_str}.jpg")
    with open(filename, "wb") as f:
        f.write(data)

    return {"saved": filename, "size": len(data)}
