from __future__ import annotations

import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .config import MAX_UPLOAD_BYTES, PATHS
from .engines import ENGINES
from .jobs import RUNNER
from .product import PRODUCT
from .security import (
    TOKEN_COOKIE,
    origin_is_allowed,
    request_is_authorized,
    request_is_loopback,
    token_matches,
)
from .store import STORE
from .utils import remove_work_tree, resolve_artifact, safe_name

STATIC = PATHS.app / "static"
CHUNK_SIZE = 1024 * 1024


def public_job(job: dict[str, Any]) -> dict[str, Any]:
    visible = dict(job)
    visible.pop("options", None)
    return visible


@asynccontextmanager
async def lifespan(_: FastAPI):
    RUNNER.start()
    yield
    RUNNER.stop()


app = FastAPI(
    title=PRODUCT.name,
    version=PRODUCT.version,
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)
app.mount("/assets", StaticFiles(directory=STATIC), name="assets")


@app.middleware("http")
async def local_security(request: Request, call_next):
    if not request_is_loopback(request):
        return JSONResponse({"detail": "Loopback access only"}, status_code=403)
    if request.url.path.startswith("/api/"):
        if not request_is_authorized(request):
            return JSONResponse({"detail": "Unauthorized local request"}, 401)
        if request.method not in {"GET", "HEAD", "OPTIONS"} and not origin_is_allowed(
            request
        ):
            return JSONResponse({"detail": "Invalid origin"}, 403)

    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "connect-src 'self'; "
        "font-src 'self'; "
        "img-src 'self' data:; "
        "object-src 'none'; "
        "base-uri 'none'; "
        "frame-ancestors 'none'; "
        "form-action 'self'"
    )
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"app": PRODUCT.slug, "status": "ok", "version": PRODUCT.version}


@app.get("/")
def index(token: str | None = None):
    if token_matches(token):
        response = RedirectResponse("/", status_code=303)
        response.set_cookie(
            TOKEN_COOKIE,
            token,
            httponly=True,
            samesite="strict",
            secure=False,
            path="/",
        )
        return response
    return FileResponse(STATIC / "index.html")


@app.get("/api/product")
def product() -> dict[str, str]:
    return PRODUCT.public_dict()


@app.get("/api/engines")
def engines() -> list[dict[str, Any]]:
    return [engine.public_dict() for engine in ENGINES.values()]


@app.get("/api/jobs")
def list_jobs() -> list[dict[str, Any]]:
    return [public_job(job) for job in STORE.list()]


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    job = STORE.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return public_job(job)


@app.post("/api/jobs", status_code=202)
async def create_job(
    engine: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
    options: Annotated[str, Form()] = "{}",
) -> dict[str, Any]:
    selected = ENGINES.get(engine)
    if selected is None:
        raise HTTPException(400, "Unknown engine")
    if len(options.encode("utf-8")) > 16 * 1024:
        raise HTTPException(413, "Options exceed the configured local limit")
    try:
        parsed_options = json.loads(options)
    except ValueError as exc:
        raise HTTPException(400, "Options must be valid JSON") from exc
    if not isinstance(parsed_options, dict):
        raise HTTPException(400, "Options must be a JSON object")

    input_name = safe_name(file.filename or "document")
    if not selected.accepts(Path(input_name)):
        raise HTTPException(415, "File extension not accepted by this engine")

    job = RUNNER.submit(engine, input_name, parsed_options)
    job_id = str(job["id"])
    work_dir = PATHS.work / job_id
    destination = work_dir / input_name
    total = 0
    try:
        work_dir.mkdir(mode=0o700, parents=True, exist_ok=False)
        with destination.open("xb") as handle:
            while chunk := await file.read(CHUNK_SIZE):
                total += len(chunk)
                if total > MAX_UPLOAD_BYTES:
                    raise HTTPException(413, "File exceeds the configured local limit")
                handle.write(chunk)
        job = STORE.mark_queued(job_id)
        RUNNER.enqueue(job_id)
        return public_job(job)
    except Exception:
        remove_work_tree(work_dir)
        STORE.update(
            job_id,
            status="failed",
            message="Upload failed",
            error="The private working copy could not be stored.",
        )
        raise
    finally:
        await file.close()


@app.get("/api/jobs/{job_id}/files/{artifact:path}")
def download_artifact(job_id: str, artifact: str):
    job = STORE.get(job_id)
    if not job or job["status"] != "completed":
        raise HTTPException(404, "Completed job not found")
    if artifact not in job["artifacts"]:
        raise HTTPException(404, "Artifact not found")
    try:
        path = resolve_artifact(PATHS.outputs / job_id, artifact)
    except ValueError as exc:
        raise HTTPException(404, "Artifact not found") from exc
    return FileResponse(path, filename=path.name)
