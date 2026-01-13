"""FastAPI application."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from vibelab import __version__

from ..db.connection import get_db, set_current_project_id
from ..db.queries import get_or_create_project
from . import (
    admin,
    datasets,
    executors,
    judges,
    pairwise,
    projects,
    results,
    review_queue,
    runs,
    scenarios,
    streaming,
    tasks,
)


class ProjectContextMiddleware(BaseHTTPMiddleware):
    """Middleware to set project context from request header.

    Reads the X-VibeLab-Project header (project name) and sets the
    current project ID in context for the request.
    """

    async def dispatch(self, request: Request, call_next):
        project_name = request.headers.get("X-VibeLab-Project", "default")

        # Look up or create the project
        project_id = None
        try:
            for conn in get_db():
                project = get_or_create_project(conn, project_name)
                project_id = project.id
                break
        except Exception:
            # If we can't get the project, default to 1
            project_id = 1

        set_current_project_id(project_id)

        response = await call_next(request)

        # Add project info to response headers for debugging
        response.headers["X-VibeLab-Project-Id"] = str(project_id)

        return response


app = FastAPI(title="VibeLab API", version=__version__)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Project context middleware (after CORS so headers work)
app.add_middleware(ProjectContextMiddleware)

# Include routers
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(scenarios.router, prefix="/api/scenarios", tags=["scenarios"])
app.include_router(results.router, prefix="/api/results", tags=["results"])
app.include_router(runs.router, prefix="/api/runs", tags=["runs"])
app.include_router(executors.router, prefix="/api/executors", tags=["executors"])
app.include_router(streaming.router, prefix="/api/results", tags=["streaming"])
app.include_router(datasets.router, prefix="/api/datasets", tags=["datasets"])
app.include_router(judges.router, prefix="/api/judges", tags=["judges"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(review_queue.router, prefix="/api/review-queue", tags=["review-queue"])
app.include_router(pairwise.router, prefix="/api/pairwise", tags=["pairwise"])

# Serve static files (React app)
try:
    from pathlib import Path

    # Try to find static files in the installed package
    # When installed via build hook, files are at vibelab/web/dist
    package_dir = Path(__file__).parent.parent
    static_dir = package_dir / "web" / "dist"

    # If not found in package, try relative to source (development)
    if not static_dir.exists():
        static_dir = Path(__file__).parent.parent.parent.parent / "web" / "dist"

    if static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
except Exception:
    pass  # Static files not available


@app.get("/api")
def root() -> str:
    """Root endpoint."""
    return "vibelab"


@app.get("/api/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "version": __version__}
