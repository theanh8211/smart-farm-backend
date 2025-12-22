import redis.asyncio as redis
import json
import asyncio

r = redis.from_url("redis://redis:6379/0")

async def enqueue_image(image_path: str, camera_id: str):
    job = {"image_path": image_path, "camera_id": camera_id}
    await r.lpush("ai_queue", json.dumps(job))