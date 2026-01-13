"""Projects API endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..db.connection import get_current_project_id, get_db
from ..db.queries import (
    create_project,
    delete_project,
    get_project,
    get_project_by_name,
    list_projects,
    update_project,
)

router = APIRouter()


# --- Request/Response Models ---


class ProjectCreate(BaseModel):
    """Request model for creating a project."""

    name: str
    description: str | None = None


class ProjectUpdate(BaseModel):
    """Request model for updating a project."""

    name: str | None = None
    description: str | None = None


class ProjectResponse(BaseModel):
    """Response model for a project."""

    id: int
    name: str
    description: str | None
    created_at: str


class ProjectWithStats(ProjectResponse):
    """Project response with statistics."""

    scenario_count: int
    dataset_count: int
    task_count: int


# --- Endpoints ---


@router.get("", response_model=list[ProjectWithStats])
def list_projects_endpoint() -> list[dict[str, Any]]:
    """List all projects with statistics."""
    for conn in get_db():
        projects = list_projects(conn)
        result = []
        for project in projects:
            # Get counts for this project
            scenario_count = conn.execute(
                "SELECT COUNT(*) FROM scenarios WHERE project_id = ?",
                (project.id,),
            ).fetchone()[0]
            dataset_count = conn.execute(
                "SELECT COUNT(*) FROM datasets WHERE project_id = ?",
                (project.id,),
            ).fetchone()[0]
            task_count = conn.execute(
                "SELECT COUNT(*) FROM tasks WHERE project_id = ?",
                (project.id,),
            ).fetchone()[0]

            result.append(
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "created_at": project.created_at.isoformat(),
                    "scenario_count": scenario_count,
                    "dataset_count": dataset_count,
                    "task_count": task_count,
                }
            )
        return result
    raise RuntimeError("Database connection failed")


@router.get("/current")
def get_current_project() -> dict[str, Any]:
    """Get the current project from context."""
    project_id = get_current_project_id()
    if project_id is None:
        return {"project": None, "message": "No project context set"}

    for conn in get_db():
        project = get_project(conn, project_id)
        if not project:
            return {"project": None, "message": f"Project {project_id} not found"}
        return {
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "created_at": project.created_at.isoformat(),
            }
        }
    raise RuntimeError("Database connection failed")


@router.post("", response_model=ProjectResponse)
def create_project_endpoint(data: ProjectCreate) -> dict[str, Any]:
    """Create a new project."""
    for conn in get_db():
        # Check if project with this name already exists
        existing = get_project_by_name(conn, data.name)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Project with name '{data.name}' already exists",
            )

        project = create_project(conn, data.name, data.description)
        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "created_at": project.created_at.isoformat(),
        }
    raise RuntimeError("Database connection failed")


@router.get("/{project_id}", response_model=ProjectWithStats)
def get_project_endpoint(project_id: int) -> dict[str, Any]:
    """Get a project by ID."""
    for conn in get_db():
        project = get_project(conn, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        scenario_count = conn.execute(
            "SELECT COUNT(*) FROM scenarios WHERE project_id = ?",
            (project.id,),
        ).fetchone()[0]
        dataset_count = conn.execute(
            "SELECT COUNT(*) FROM datasets WHERE project_id = ?",
            (project.id,),
        ).fetchone()[0]
        task_count = conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE project_id = ?",
            (project.id,),
        ).fetchone()[0]

        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "created_at": project.created_at.isoformat(),
            "scenario_count": scenario_count,
            "dataset_count": dataset_count,
            "task_count": task_count,
        }
    raise RuntimeError("Database connection failed")


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project_endpoint(project_id: int, data: ProjectUpdate) -> dict[str, Any]:
    """Update a project."""
    for conn in get_db():
        project = get_project(conn, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Check for name conflicts if name is being updated
        if data.name and data.name != project.name:
            existing = get_project_by_name(conn, data.name)
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Project with name '{data.name}' already exists",
                )

        updated = update_project(
            conn,
            project_id,
            name=data.name,
            description=data.description,
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Project not found")

        return {
            "id": updated.id,
            "name": updated.name,
            "description": updated.description,
            "created_at": updated.created_at.isoformat(),
        }
    raise RuntimeError("Database connection failed")


@router.delete("/{project_id}")
def delete_project_endpoint(project_id: int) -> dict[str, Any]:
    """Delete a project.

    Note: This will fail if there are scenarios, datasets, or tasks
    referencing this project.
    """
    for conn in get_db():
        project = get_project(conn, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Check for references
        scenario_count = conn.execute(
            "SELECT COUNT(*) FROM scenarios WHERE project_id = ?",
            (project_id,),
        ).fetchone()[0]
        if scenario_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete project with {scenario_count} scenarios. "
                "Delete scenarios first.",
            )

        dataset_count = conn.execute(
            "SELECT COUNT(*) FROM datasets WHERE project_id = ?",
            (project_id,),
        ).fetchone()[0]
        if dataset_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete project with {dataset_count} datasets. Delete datasets first.",
            )

        if not delete_project(conn, project_id):
            raise HTTPException(status_code=404, detail="Project not found")

        return {"status": "deleted", "project_id": project_id}
    raise RuntimeError("Database connection failed")


@router.get("/by-name/{name}", response_model=ProjectResponse)
def get_project_by_name_endpoint(name: str) -> dict[str, Any]:
    """Get a project by name."""
    for conn in get_db():
        project = get_project_by_name(conn, name)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "created_at": project.created_at.isoformat(),
        }
    raise RuntimeError("Database connection failed")
