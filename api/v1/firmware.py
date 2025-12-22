from fastapi import APIRouter, UploadFile, File, Depends
import os
import shutil

router = APIRouter()

FIRMWARE_DIR = "./firmware"
os.makedirs(FIRMWARE_DIR, exist_ok=True)

@router.post("/upload")
async def upload_firmware(version: str, changelog: str, file: UploadFile = File(...)):
    path = f"{FIRMWARE_DIR}/{version}.bin"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    # Tạo record trong DB...
    return {"version": version, "status": "uploaded"}