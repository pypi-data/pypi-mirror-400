"""Scenario API endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..db import (
    create_commit_scenario_draft,
    create_scenario,
    delete_scenario,
    get_commit_scenario_draft,
    get_db,
    get_scenario,
    list_results,
    list_scenarios,
    update_commit_scenario_draft,
    update_scenario_archived,
)
from ..db.connection import get_results_dir
from ..db.queries import get_project_id_for_result
from ..engine.commit_analyzer import (
    fetch_commit_diff,
    fetch_commit_info,
    fetch_pr_for_commit,
    parse_commit_url,
)
from ..engine.queue import enqueue_generate_scenario_from_commit
from ..lib import resolve_github_code_ref
from ..models.commit_draft import CommitScenarioDraft
from ..models.scenario import CodeType, GitHubCodeRef, LocalCodeRef, Scenario
from .datasets import build_analytics_matrix

router = APIRouter()


class CreateScenarioRequest(BaseModel):
    """Request to create a scenario."""

    code_type: str
    code_ref: dict | None = None
    prompt: str


@router.get("")
def list_scenarios_endpoint(limit: int | None = None, include_archived: bool = False):
    """List scenarios.

    Args:
        limit: Maximum number of scenarios to return.
        include_archived: If True, include archived scenarios in the response.
    """
    for db in get_db():
        from ..db import get_latest_llm_scenario_judge

        scenarios = list_scenarios(db, limit=limit, include_archived=include_archived)
        results_by_scenario = {}
        judges_by_scenario = {}

        for scenario in scenarios:
            results = list_results(db, scenario_id=scenario.id)
            results_by_scenario[scenario.id] = [
                {**r.model_dump(), "is_stale": r.is_stale()} for r in results
            ]

            # Get latest judge for scenario
            judge = get_latest_llm_scenario_judge(db, scenario.id)
            if judge:
                judges_by_scenario[scenario.id] = {
                    "id": judge.id,
                    "alignment_score": judge.alignment_score,
                }

        return {
            "scenarios": [s.model_dump() for s in scenarios],
            "results_by_scenario": {str(k): v for k, v in results_by_scenario.items()},
            "judges_by_scenario": {str(k): v for k, v in judges_by_scenario.items()},
        }


@router.get("/{scenario_id}")
def get_scenario_endpoint(scenario_id: int):
    """Get scenario with results."""
    for db in get_db():
        scenario = get_scenario(db, scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        results = list_results(db, scenario_id=scenario_id)
        return {
            "scenario": scenario.model_dump(),
            "results": [{**r.model_dump(), "is_stale": r.is_stale()} for r in results],
        }


@router.post("")
def create_scenario_endpoint(request: CreateScenarioRequest):
    """Create a new scenario."""
    code_type = CodeType(request.code_type)

    code_ref = None
    if request.code_ref:
        if code_type == CodeType.GITHUB:
            code_ref = GitHubCodeRef(**request.code_ref)
            # Resolve branch/tag names to commit SHAs BEFORE searching
            code_ref = resolve_github_code_ref(code_ref)
        elif code_type == CodeType.LOCAL:
            code_ref = LocalCodeRef(**request.code_ref)

    # Find or create scenario (matching on resolved commit SHA)
    scenario_obj = None
    for db in get_db():
        scenarios = list_scenarios(db)
        for s in scenarios:
            if s.code_type == code_type and s.prompt == request.prompt:
                if code_type == CodeType.GITHUB and isinstance(code_ref, GitHubCodeRef):
                    if isinstance(s.code_ref, GitHubCodeRef):
                        # Match on owner, repo, AND commit SHA (after resolution)
                        if (
                            s.code_ref.owner == code_ref.owner
                            and s.code_ref.repo == code_ref.repo
                            and s.code_ref.commit_sha == code_ref.commit_sha
                        ):
                            scenario_obj = s
                            break
                elif code_type == CodeType.LOCAL and isinstance(code_ref, LocalCodeRef):
                    if isinstance(s.code_ref, LocalCodeRef):
                        if s.code_ref.path == code_ref.path:
                            scenario_obj = s
                            break
                elif code_type == CodeType.EMPTY:
                    scenario_obj = s
                    break

        if not scenario_obj:
            scenario_obj = Scenario(
                id=0,
                code_type=code_type,
                code_ref=code_ref,
                prompt=request.prompt,
                created_at=datetime.now(UTC),
            )
            scenario_obj = create_scenario(db, scenario_obj)
        break

    if not scenario_obj:
        raise HTTPException(status_code=500, detail="Failed to create scenario")

    return scenario_obj.model_dump()


@router.delete("/{scenario_id}")
def delete_scenario_endpoint(scenario_id: int):
    """Delete a scenario and all its results (cascade delete)."""
    import shutil

    for db in get_db():
        scenario = get_scenario(db, scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")

        # Get all results for this scenario to delete their files
        results = list_results(db, scenario_id=scenario_id)

        # Get project_ids for each result before deleting (needed for file paths)
        result_project_ids: dict[int, int] = {}
        for result in results:
            project_id = get_project_id_for_result(db, result.id)
            if project_id is None:
                raise HTTPException(
                    status_code=500, detail=f"Could not determine project_id for result {result.id}"
                )
            result_project_ids[result.id] = project_id

        # Delete the scenario (cascade deletes results in DB)
        deleted = delete_scenario(db, scenario_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Scenario not found")

        # Delete result files
        for result in results:
            project_id = result_project_ids[result.id]
            result_dir = get_results_dir(project_id) / str(result.id)
            if result_dir.exists():
                shutil.rmtree(result_dir)

        break

    return {"status": "deleted", "scenario_id": scenario_id}


class ArchiveScenarioRequest(BaseModel):
    """Request to archive or unarchive a scenario."""

    archived: bool


@router.patch("/{scenario_id}/archive")
def archive_scenario_endpoint(scenario_id: int, request: ArchiveScenarioRequest):
    """Archive or unarchive a scenario.

    Archiving hides the scenario from the main scenario list and global report
    without deleting any data.
    """
    for db in get_db():
        scenario = get_scenario(db, scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")

        updated = update_scenario_archived(db, scenario_id, request.archived)
        if not updated:
            raise HTTPException(status_code=404, detail="Scenario not found")

        # Fetch updated scenario
        scenario = get_scenario(db, scenario_id)
        return scenario.model_dump() if scenario else None

    raise HTTPException(status_code=500, detail="Database error")


class FromCommitRequest(BaseModel):
    """Request to create a scenario from a commit."""

    commit_url: str | None = None
    owner: str | None = None
    repo: str | None = None
    commit_sha: str | None = None


@router.post("/from-commit")
def from_commit_endpoint(request: FromCommitRequest):
    """Analyze a GitHub commit and queue a task to generate a scenario."""
    # Parse commit reference
    if request.commit_url:
        parsed = parse_commit_url(request.commit_url)
        if not parsed:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid commit URL format: {request.commit_url}",
            )
        owner, repo, commit_sha = parsed
    elif request.owner and request.repo and request.commit_sha:
        owner = request.owner
        repo = request.repo
        commit_sha = request.commit_sha
    else:
        raise HTTPException(
            status_code=400,
            detail="Either commit_url or (owner, repo, commit_sha) must be provided",
        )

    # Fetch commit info and diff
    try:
        commit_info = fetch_commit_info(owner, repo, commit_sha)
        diff = fetch_commit_diff(owner, repo, commit_sha)
        pr_info = fetch_pr_for_commit(owner, repo, commit_sha)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create draft (task_id will be set after task creation)
    draft = CommitScenarioDraft(
        id=0,
        task_id=None,  # Will be set after task creation
        owner=owner,
        repo=repo,
        commit_sha=commit_sha,
        parent_sha=commit_info.parent_sha,
        commit_message=commit_info.commit_message,
        commit_author=commit_info.commit_author,
        pr_number=pr_info.number if pr_info else None,
        pr_title=pr_info.title if pr_info else None,
        pr_body=pr_info.body if pr_info else None,
        diff=diff,
        status="pending",
        created_at=datetime.now(UTC),
    )

    # Save draft, then create task with draft_id, then update draft with task_id
    for db in get_db():
        draft = create_commit_scenario_draft(db, draft)
        task_id = enqueue_generate_scenario_from_commit(db, draft_id=draft.id, priority=5)
        # Update draft to link back to task
        db.execute(
            "UPDATE commit_scenario_drafts SET task_id = ? WHERE id = ?",
            (task_id, draft.id),
        )
        db.commit()
        break

    return {
        "draft_id": draft.id,
        "task_id": task_id,
        "status": "pending",
        "commit_info": {
            "owner": owner,
            "repo": repo,
            "commit_sha": commit_sha,
            "parent_sha": commit_info.parent_sha,
            "commit_message": commit_info.commit_message,
            "commit_author": commit_info.commit_author,
            "pr_number": pr_info.number if pr_info else None,
            "pr_title": pr_info.title if pr_info else None,
        },
    }


@router.get("/drafts/{draft_id}")
def get_draft_endpoint(draft_id: int):
    """Get a commit scenario draft with task status."""
    from ..engine.queue import get_task

    for db in get_db():
        draft = get_commit_scenario_draft(db, draft_id)
        if not draft:
            raise HTTPException(status_code=404, detail="Draft not found")

        # Get task info if available
        task_info = None
        if draft.task_id:
            task = get_task(db, draft.task_id)
            if task:
                task_info = {
                    "id": task.id,
                    "status": task.status.value,
                    "error_message": task.error_message,
                    "started_at": task.started_at,
                    "finished_at": task.finished_at,
                }

        return {
            "draft": draft.model_dump(),
            "status": draft.status,
            "task": task_info,
        }
    raise HTTPException(status_code=500, detail="Database error")


class SaveDraftRequest(BaseModel):
    """Request to save a draft as a scenario."""

    prompt: str
    judge_guidance: str
    enable_judge: bool = True


@router.post("/drafts/{draft_id}/save")
def save_draft_endpoint(draft_id: int, request: SaveDraftRequest):
    """Save a draft as a scenario (and optionally create a judge)."""
    from ..db import create_llm_scenario_judge

    for db in get_db():
        draft = get_commit_scenario_draft(db, draft_id)
        if not draft:
            raise HTTPException(status_code=404, detail="Draft not found")
        if draft.status == "saved":
            raise HTTPException(status_code=400, detail="Draft already saved")

        # Create scenario pointing to parent commit
        code_ref = GitHubCodeRef(
            owner=draft.owner,
            repo=draft.repo,
            commit_sha=draft.parent_sha,  # Parent commit is the starting point
        )
        code_ref = resolve_github_code_ref(code_ref)

        scenario = Scenario(
            id=0,
            code_type=CodeType.GITHUB,
            code_ref=code_ref,
            prompt=request.prompt,
            created_at=datetime.now(UTC),
        )
        scenario = create_scenario(db, scenario)

        judge_id = None
        if request.enable_judge:
            # Create judge with guidance that includes reference diff
            judge = create_llm_scenario_judge(
                db,
                scenario_id=scenario.id,
                guidance=request.judge_guidance,
                judge_provider="anthropic",
                judge_model="claude-sonnet-4-20250514",
            )
            judge_id = judge.id

        # Update draft status
        update_commit_scenario_draft(
            db,
            draft_id,
            status="saved",
            scenario_id=scenario.id,
            judge_id=judge_id,
        )

        return {
            "scenario_id": scenario.id,
            "judge_id": judge_id,
            "status": "saved",
        }
    raise HTTPException(status_code=500, detail="Database error")


@router.get("/analytics/global")
def get_global_analytics_endpoint(include_archived: bool = False):
    """Get analytics for ALL scenarios showing scenario-executor matrix (global report).

    By default, archived scenarios are excluded from the global report.
    """
    for db in get_db():
        scenarios = list_scenarios(db, include_archived=include_archived)

        if not scenarios:
            return {
                "title": "Global Report",
                "description": "All scenarios across the system",
                "executors": [],
                "matrix": [],
                "aggregations": {
                    "global": {
                        "quality": {"mean": None, "std": None, "count": 0},
                        "latency": {"mean": None, "std": None, "count": 0},
                    },
                    "byExecutor": {},
                    "byScenario": {},
                },
            }

        analytics = build_analytics_matrix(db, scenarios)

        return {
            "title": "Global Report",
            "description": f"All {len(scenarios)} scenarios across the system",
            "scenario_count": len(scenarios),
            **analytics,
        }
