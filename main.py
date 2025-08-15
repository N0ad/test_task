"""
FastAPI Image Processor (async, simplified)

Endpoints:
- POST /upload: Upload an image (JPEG/PNG, <= 5 MB).
                The original is validated and kept in memory.
- GET  /process: Convert the uploaded image to grayscale, save to ./images,
                 return the file, and delete the original from memory.

Run locally:
    uvicorn main:app --reload
"""
from __future__ import annotations

import asyncio
import logging
from logging.handlers import RotatingFileHandler
from io import BytesIO
from pathlib import Path
from typing import Dict
from uuid import uuid4

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse

try:
    from PIL import Image
except ImportError as e:
    raise SystemExit("Pillow is required. Install with: pip install pillow") from e

# Configuration
MAX_BYTES = 5242880  # 5 MB
BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Logging
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("image_api")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    # To terminal
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    # To file
    fh = RotatingFileHandler(
        LOGS_DIR / "app.log",
        maxBytes=10485760, # 10 MB
        backupCount=1,
        encoding="utf-8"
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)

# In-memory storage for originals (bytes), removed after processing
ORIGINALS: Dict[str, bytes] = {}

# FastAPI
app = FastAPI(
    title="FastAPI Image Processor",
    description="Upload JPEG/PNG (<=5MB), then convert to grayscale."
)


# Helper functions
def _normalized_ext(content_type: str | None) -> str | None:
    if content_type == "image/jpeg":
        return "jpg"
    if content_type == "image/png":
        return "png"
    return None


def _work_grayscale(data: bytes) -> bytes:
    img = Image.open(BytesIO(data))
    gray = img.convert("L")
    buf = BytesIO()
    gray.save(buf, format="PNG")
    return buf.getvalue()


async def _make_grayscale(data: bytes) -> bytes:
    return await asyncio.to_thread(_work_grayscale, data)


def _write_bytes(path: Path, data: bytes) -> None:
    path.write_bytes(data)


async def _write_bytes_async(path: Path, data: bytes) -> None:
    await asyncio.to_thread(_write_bytes, path, data)


# Requests
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)) -> JSONResponse:
    # Upload JPEG/PNG up to 5 MB. 
    # Stores original bytes in memory and returns image_id.
    content_type = file.content_type or ""
    ext = _normalized_ext(content_type)
    if ext is None:
        logger.error("Unsupported content type: %s", content_type)
        return JSONResponse(
            {"error":"Unsupported file type. Use JPEG or PNG."},
            status_code=400
        )

    data = await file.read()
    size = len(data)
    if size > MAX_BYTES:
        logger.error("File too large: %d bytes", size)
        return JSONResponse(
            {"error":"File too large. Maximum is 5 MB."},
            status_code=413
        )

    image_id = uuid4().hex
    ORIGINALS[image_id] = data
    logger.info("Original stored in memory: id=%s, size=%d", image_id, size)

    return JSONResponse({
        "image_id": image_id, 
        "note": "Use /process?image_id=<image_id> to get grayscale PNG version."
    })


@app.get("/process")
async def process_image(image_id: str) -> FileResponse:
    # Convert uploaded image to grayscale, save it to ./images, return the file, 
    # and delete the original from memory.
    if image_id not in ORIGINALS:
        logger.error("Original not found for id=%s", image_id)
        return JSONResponse(
            {"error":"Original image not found."},
            status_code=404
        )

    data = ORIGINALS[image_id]

    try:
        processed_bytes = await _make_grayscale(data)
    except Exception as e:
        logger.error("Processing failed: %s", e, exc_info=True)
        return JSONResponse(
            {"error":"Failed to process image."},
            status_code=400
        )
    finally:
        # Remove original from memory
        ORIGINALS.pop(image_id, None)

    out_name = f"{image_id}_grayscale.png"
    out_path = IMAGES_DIR / out_name

    await _write_bytes_async(out_path, processed_bytes)
    logger.info("Processed image saved: %s", out_path)

    return FileResponse(path=out_path, media_type="image/png", filename=out_name)


@app.get("/ping")
async def ping():
    # Health check request.
    return {"status": "ok"}