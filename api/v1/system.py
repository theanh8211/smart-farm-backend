from fastapi import APIRouter, Depends, Request
from core.rate_limit import limiter

router = APIRouter()

@router.get("/health")
@limiter.limit("60/minute")
async def health_check(request: Request):
    return {"status": "healthy", "service": "Smart Farm Backend"}

@router.get("/storage")
async def storage_info():
    import shutil
    total, used, free = shutil.disk_usage("./uploaded_images")
    return {
        "total_gb": round(total // (2**30), 2),
        "used_gb": round(used // (2**30), 2),
        "free_gb": round(free // (2**30), 2)
    }