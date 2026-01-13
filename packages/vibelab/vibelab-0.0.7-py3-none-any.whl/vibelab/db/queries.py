"""Database queries."""

import sqlite3
from datetime import datetime
from typing import Any

from ..models.commit_draft import CommitScenarioDraft
from ..models.dataset import Dataset
from ..models.judge import Judgement, LLMScenarioJudge
from ..models.pairwise import PairwisePreference, PreferenceType
from ..models.project import Project
from ..models.result import Result, ResultStatus
from ..models.scenario import Scenario

# --- Project functions ---


def create_project(conn: sqlite3.Connection, name: str, description: str | None = None) -> Project:
    """Create a new project."""
    now = datetime.now().isoformat()
    cursor = conn.execute(
        """
        INSERT INTO projects (name, description, created_at)
        VALUES (?, ?, ?)
        """,
        (name, description, now),
    )
    conn.commit()
    return Project(
        id=cursor.lastrowid,  # type: ignore[arg-type]
        name=name,
        description=description,
        created_at=datetime.fromisoformat(now),
    )


def get_project(conn: sqlite3.Connection, project_id: int) -> Project | None:
    """Get project by ID."""
    cursor = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return Project.from_db_dict(dict(row))


def get_project_by_name(conn: sqlite3.Connection, name: str) -> Project | None:
    """Get project by name."""
    cursor = conn.execute("SELECT * FROM projects WHERE name = ?", (name,))
    row = cursor.fetchone()
    if not row:
        return None
    return Project.from_db_dict(dict(row))


def list_projects(conn: sqlite3.Connection) -> list[Project]:
    """List all projects."""
    cursor = conn.execute("SELECT * FROM projects ORDER BY created_at DESC")
    return [Project.from_db_dict(dict(row)) for row in cursor.fetchall()]


def update_project(
    conn: sqlite3.Connection,
    project_id: int,
    name: str | None = None,
    description: str | None = None,
) -> Project | None:
    """Update a project."""
    updates: list[str] = []
    params: list[Any] = []

    if name is not None:
        updates.append("name = ?")
        params.append(name)
    if description is not None:
        updates.append("description = ?")
        params.append(description)

    if not updates:
        return get_project(conn, project_id)

    params.append(project_id)
    query = f"UPDATE projects SET {', '.join(updates)} WHERE id = ?"
    conn.execute(query, params)
    conn.commit()
    return get_project(conn, project_id)


def delete_project(conn: sqlite3.Connection, project_id: int) -> bool:
    """Delete a project.

    Note: This will fail if there are scenarios, datasets, or tasks referencing
    this project (due to FK constraints). Delete those first.
    """
    cursor = conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    return cursor.rowcount > 0


def get_or_create_project(conn: sqlite3.Connection, name: str) -> Project:
    """Get a project by name, or create it if it doesn't exist."""
    project = get_project_by_name(conn, name)
    if project:
        return project
    return create_project(conn, name)


def get_project_id_for_result(conn: sqlite3.Connection, result_id: int) -> int | None:
    """Look up project_id for a result via result -> scenario -> project_id.

    This is used to determine the blob storage path for result files.
    Returns None if the result or scenario doesn't exist.
    """
    cursor = conn.execute(
        """
        SELECT s.project_id
        FROM results r
        INNER JOIN scenarios s ON r.scenario_id = s.id
        WHERE r.id = ?
        """,
        (result_id,),
    )
    row = cursor.fetchone()
    if not row:
        return None
    return row["project_id"]


def create_scenario(
    conn: sqlite3.Connection, scenario: Scenario, project_id: int | None = None
) -> Scenario:
    """Create a new scenario.

    Args:
        conn: Database connection.
        scenario: Scenario to create.
        project_id: Project ID to assign the scenario to. If None, uses the
            current project context.

    Raises:
        ValueError: If project_id is not provided and no project context is set.
    """
    from .connection import get_current_project_id

    if project_id is None:
        project_id = get_current_project_id()
    if project_id is None:
        raise ValueError("project_id is required (no project context set)")

    data = scenario.to_db_dict()
    cursor = conn.execute(
        """
        INSERT INTO scenarios (code_type, code_ref, prompt, created_at, project_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        (data["code_type"], data["code_ref"], data["prompt"], data["created_at"], project_id),
    )
    conn.commit()
    return Scenario.from_db_dict(
        {
            "id": cursor.lastrowid,
            "code_type": data["code_type"],
            "code_ref": data["code_ref"],
            "prompt": data["prompt"],
            "created_at": data["created_at"],
        }
    )


def get_scenario(conn: sqlite3.Connection, scenario_id: int) -> Scenario | None:
    """Get scenario by ID."""
    cursor = conn.execute("SELECT * FROM scenarios WHERE id = ?", (scenario_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return Scenario.from_db_dict(dict(row))


def list_scenarios(
    conn: sqlite3.Connection,
    limit: int | None = None,
    include_archived: bool = False,
    project_id: int | None = None,
) -> list[Scenario]:
    """List scenarios.

    Args:
        conn: Database connection.
        limit: Maximum number of scenarios to return.
        include_archived: If True, include archived scenarios. Default is False.
        project_id: Filter by project. If None, uses current project context.
    """
    from .connection import get_current_project_id

    if project_id is None:
        project_id = get_current_project_id()

    conditions: list[str] = []
    params: list[Any] = []

    if not include_archived:
        conditions.append("archived = 0")

    if project_id is not None:
        conditions.append("project_id = ?")
        params.append(project_id)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"SELECT * FROM scenarios {where_clause} ORDER BY created_at DESC"

    if limit:
        query += f" LIMIT {limit}"

    cursor = conn.execute(query, params)
    return [Scenario.from_db_dict(dict(row)) for row in cursor.fetchall()]


def update_scenario_archived(conn: sqlite3.Connection, scenario_id: int, archived: bool) -> bool:
    """Update the archived status of a scenario.

    Args:
        conn: Database connection.
        scenario_id: ID of the scenario to update.
        archived: New archived status.

    Returns:
        True if the scenario was updated, False if not found.
    """
    cursor = conn.execute(
        "UPDATE scenarios SET archived = ? WHERE id = ?",
        (1 if archived else 0, scenario_id),
    )
    conn.commit()
    return cursor.rowcount > 0


def create_result(conn: sqlite3.Connection, result: Result) -> Result:
    """Create a new result."""
    data = result.to_db_dict()
    # Set updated_at to created_at on creation
    data["updated_at"] = data["created_at"]
    cursor = conn.execute(
        """
        INSERT INTO results (
            scenario_id, harness, provider, model, status, created_at, updated_at,
            started_at, finished_at, duration_ms, lines_added, lines_removed,
            files_changed, tokens_used, cost_usd, harness_metrics, annotations,
            timeout_seconds, driver, error_message
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["scenario_id"],
            data["harness"],
            data["provider"],
            data["model"],
            data["status"],
            data["created_at"],
            data["updated_at"],
            data["started_at"],
            data["finished_at"],
            data["duration_ms"],
            data["lines_added"],
            data["lines_removed"],
            data["files_changed"],
            data["tokens_used"],
            data["cost_usd"],
            data["harness_metrics"],
            data["annotations"],
            data["timeout_seconds"],
            data["driver"],
            data["error_message"],
        ),
    )
    conn.commit()
    return Result.from_db_dict({**data, "id": cursor.lastrowid})


def get_result(conn: sqlite3.Connection, result_id: int) -> Result | None:
    """Get result by ID."""
    cursor = conn.execute("SELECT * FROM results WHERE id = ?", (result_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return Result.from_db_dict(dict(row))


def list_results(
    conn: sqlite3.Connection,
    scenario_id: int | None = None,
    executor_spec: str | None = None,
    status: ResultStatus | None = None,
) -> list[Result]:
    """List results with optional filtering."""
    query = "SELECT * FROM results WHERE 1=1"
    params: list[Any] = []

    if scenario_id:
        query += " AND scenario_id = ?"
        params.append(scenario_id)

    if executor_spec:
        parts = executor_spec.split(":")
        if len(parts) >= 1:
            query += " AND harness = ?"
            params.append(parts[0])
        if len(parts) >= 2:
            query += " AND provider = ?"
            params.append(parts[1])
        if len(parts) >= 3:
            query += " AND model = ?"
            params.append(parts[2])

    if status:
        query += " AND status = ?"
        params.append(status.value)

    query += " ORDER BY created_at DESC"

    cursor = conn.execute(query, params)
    return [Result.from_db_dict(dict(row)) for row in cursor.fetchall()]


def update_result_status(
    conn: sqlite3.Connection,
    result_id: int,
    status: ResultStatus,
    started_at: datetime | None = None,
    finished_at: datetime | None = None,
    duration_ms: int | None = None,
    error_message: str | None = None,
) -> None:
    """Update result status and timing."""
    updates = ["status = ?", "updated_at = ?"]
    params: list[Any] = [status.value, datetime.now().isoformat()]

    if started_at:
        updates.append("started_at = ?")
        params.append(started_at.isoformat())

    if finished_at:
        updates.append("finished_at = ?")
        params.append(finished_at.isoformat())

    if duration_ms is not None:
        updates.append("duration_ms = ?")
        params.append(duration_ms)

    if error_message is not None:
        updates.append("error_message = ?")
        params.append(error_message)

    params.append(result_id)
    conn.execute(
        f"UPDATE results SET {', '.join(updates)} WHERE id = ?",
        params,
    )
    conn.commit()


def update_result_metrics(
    conn: sqlite3.Connection,
    result_id: int,
    lines_added: int | None = None,
    lines_removed: int | None = None,
    files_changed: int | None = None,
    tokens_used: int | None = None,
    cost_usd: float | None = None,
) -> None:
    """Update result metrics."""
    updates = ["updated_at = ?"]
    params: list[Any] = [datetime.now().isoformat()]

    if lines_added is not None:
        updates.append("lines_added = ?")
        params.append(lines_added)

    if lines_removed is not None:
        updates.append("lines_removed = ?")
        params.append(lines_removed)

    if files_changed is not None:
        updates.append("files_changed = ?")
        params.append(files_changed)

    if tokens_used is not None:
        updates.append("tokens_used = ?")
        params.append(tokens_used)

    if cost_usd is not None:
        updates.append("cost_usd = ?")
        params.append(cost_usd)

    params.append(result_id)
    conn.execute(
        f"UPDATE results SET {', '.join(updates)} WHERE id = ?",
        params,
    )
    conn.commit()


def update_result_annotations(
    conn: sqlite3.Connection, result_id: int, annotations: dict[str, Any]
) -> None:
    """Update result annotations."""
    import json

    conn.execute(
        "UPDATE results SET annotations = ? WHERE id = ?",
        (json.dumps(annotations), result_id),
    )
    conn.commit()


def update_result_notes(conn: sqlite3.Connection, result_id: int, notes: str | None) -> None:
    """Update result notes."""
    conn.execute(
        "UPDATE results SET notes = ?, updated_at = ? WHERE id = ?",
        (notes, datetime.now().isoformat(), result_id),
    )
    conn.commit()


def update_result_quality(conn: sqlite3.Connection, result_id: int, quality: int | None) -> None:
    """Update result quality score."""
    conn.execute(
        "UPDATE results SET quality = ?, updated_at = ? WHERE id = ?",
        (quality, datetime.now().isoformat(), result_id),
    )
    conn.commit()


def update_result_notes_and_quality(
    conn: sqlite3.Connection, result_id: int, notes: str | None = None, quality: int | None = None
) -> None:
    """Update result notes and/or quality score."""
    updates = ["updated_at = ?"]
    params: list[Any] = [datetime.now().isoformat()]

    if notes is not None:
        updates.append("notes = ?")
        params.append(notes)

    if quality is not None:
        updates.append("quality = ?")
        params.append(quality)

    params.append(result_id)
    conn.execute(
        f"UPDATE results SET {', '.join(updates)} WHERE id = ?",
        params,
    )
    conn.commit()


def delete_result(conn: sqlite3.Connection, result_id: int) -> bool:
    """Delete a result by ID. Returns True if deleted, False if not found."""
    cursor = conn.execute("DELETE FROM results WHERE id = ?", (result_id,))
    conn.commit()
    return cursor.rowcount > 0


def delete_scenario(conn: sqlite3.Connection, scenario_id: int) -> bool:
    """Delete a scenario and all its results (cascade delete). Returns True if deleted, False if not found."""
    # First delete all results for this scenario
    conn.execute("DELETE FROM results WHERE scenario_id = ?", (scenario_id,))
    # Then delete the scenario
    cursor = conn.execute("DELETE FROM scenarios WHERE id = ?", (scenario_id,))
    conn.commit()
    return cursor.rowcount > 0


# Dataset functions
def create_dataset(
    conn: sqlite3.Connection, dataset: Dataset, project_id: int | None = None
) -> Dataset:
    """Create a new dataset.

    Args:
        conn: Database connection.
        dataset: Dataset to create.
        project_id: Project ID to assign the dataset to. If None, uses the
            current project context.

    Raises:
        ValueError: If project_id is not provided and no project context is set.
    """
    from .connection import get_current_project_id

    if project_id is None:
        project_id = get_current_project_id()
    if project_id is None:
        raise ValueError("project_id is required (no project context set)")

    data = dataset.to_db_dict()
    cursor = conn.execute(
        """
        INSERT INTO datasets (name, description, created_at, project_id)
        VALUES (?, ?, ?, ?)
        """,
        (data["name"], data["description"], data["created_at"], project_id),
    )
    conn.commit()
    return Dataset.from_db_dict(
        {
            "id": cursor.lastrowid,
            "name": data["name"],
            "description": data["description"],
            "created_at": data["created_at"],
        }
    )


def get_dataset(conn: sqlite3.Connection, dataset_id: int) -> Dataset | None:
    """Get dataset by ID."""
    cursor = conn.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return Dataset.from_db_dict(dict(row))


def list_datasets(
    conn: sqlite3.Connection, limit: int | None = None, project_id: int | None = None
) -> list[Dataset]:
    """List datasets.

    Args:
        conn: Database connection.
        limit: Maximum number of datasets to return.
        project_id: Filter by project. If None, uses current project context.
    """
    from .connection import get_current_project_id

    if project_id is None:
        project_id = get_current_project_id()

    if project_id is not None:
        query = "SELECT * FROM datasets WHERE project_id = ? ORDER BY created_at DESC"
        params: list[Any] = [project_id]
    else:
        query = "SELECT * FROM datasets ORDER BY created_at DESC"
        params = []

    if limit:
        query += f" LIMIT {limit}"

    cursor = conn.execute(query, params)
    return [Dataset.from_db_dict(dict(row)) for row in cursor.fetchall()]


def delete_dataset(conn: sqlite3.Connection, dataset_id: int) -> bool:
    """Delete a dataset. Returns True if deleted, False if not found."""
    cursor = conn.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))
    conn.commit()
    return cursor.rowcount > 0


def get_dataset_scenarios(conn: sqlite3.Connection, dataset_id: int) -> list[Scenario]:
    """Get all scenarios in a dataset."""
    cursor = conn.execute(
        """
        SELECT s.* FROM scenarios s
        INNER JOIN dataset_scenarios ds ON s.id = ds.scenario_id
        WHERE ds.dataset_id = ?
        ORDER BY s.created_at DESC
        """,
        (dataset_id,),
    )
    return [Scenario.from_db_dict(dict(row)) for row in cursor.fetchall()]


def add_scenario_to_dataset(conn: sqlite3.Connection, dataset_id: int, scenario_id: int) -> None:
    """Add a scenario to a dataset."""
    conn.execute(
        """
        INSERT OR IGNORE INTO dataset_scenarios (dataset_id, scenario_id)
        VALUES (?, ?)
        """,
        (dataset_id, scenario_id),
    )
    conn.commit()


def remove_scenario_from_dataset(
    conn: sqlite3.Connection, dataset_id: int, scenario_id: int
) -> None:
    """Remove a scenario from a dataset."""
    conn.execute(
        """
        DELETE FROM dataset_scenarios
        WHERE dataset_id = ? AND scenario_id = ?
        """,
        (dataset_id, scenario_id),
    )
    conn.commit()


# LLM Judge functions
def create_llm_scenario_judge(
    conn: sqlite3.Connection, judge: LLMScenarioJudge
) -> LLMScenarioJudge:
    """Create a new LLM scenario judge."""
    data = judge.to_db_dict()
    cursor = conn.execute(
        """
        INSERT INTO llm_scenario_judges (
            scenario_id,
            guidance,
            judge_provider,
            judge_model,
            training_sample_ids,
            alignment_score,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["scenario_id"],
            data["guidance"],
            data["judge_provider"],
            data["judge_model"],
            data["training_sample_ids"],
            data["alignment_score"],
            data["created_at"],
        ),
    )
    conn.commit()
    return LLMScenarioJudge.from_db_dict({**data, "id": cursor.lastrowid})


def get_llm_scenario_judge(conn: sqlite3.Connection, judge_id: int) -> LLMScenarioJudge | None:
    """Get LLM scenario judge by ID."""
    cursor = conn.execute("SELECT * FROM llm_scenario_judges WHERE id = ?", (judge_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return LLMScenarioJudge.from_db_dict(dict(row))


def list_llm_scenario_judges(
    conn: sqlite3.Connection, scenario_id: int | None = None
) -> list[LLMScenarioJudge]:
    """List LLM scenario judges, optionally filtered by scenario."""
    if scenario_id:
        cursor = conn.execute(
            "SELECT * FROM llm_scenario_judges WHERE scenario_id = ? ORDER BY created_at DESC",
            (scenario_id,),
        )
    else:
        cursor = conn.execute("SELECT * FROM llm_scenario_judges ORDER BY created_at DESC")
    return [LLMScenarioJudge.from_db_dict(dict(row)) for row in cursor.fetchall()]


def get_latest_llm_scenario_judge(
    conn: sqlite3.Connection, scenario_id: int
) -> LLMScenarioJudge | None:
    """Get the latest LLM scenario judge for a scenario."""
    cursor = conn.execute(
        "SELECT * FROM llm_scenario_judges WHERE scenario_id = ? ORDER BY created_at DESC LIMIT 1",
        (scenario_id,),
    )
    row = cursor.fetchone()
    if not row:
        return None
    return LLMScenarioJudge.from_db_dict(dict(row))


def update_llm_scenario_judge_alignment(
    conn: sqlite3.Connection, judge_id: int, alignment_score: float | None
) -> None:
    """Update the alignment score for an LLM scenario judge.

    Pass None to set the DB column to NULL (i.e. "not evaluated").
    """
    conn.execute(
        "UPDATE llm_scenario_judges SET alignment_score = ? WHERE id = ?",
        (alignment_score, judge_id),
    )
    conn.commit()


def delete_llm_scenario_judge(conn: sqlite3.Connection, judge_id: int) -> bool:
    """Delete an LLM scenario judge by ID. Returns True if deleted, False if not found."""
    cursor = conn.execute("DELETE FROM llm_scenario_judges WHERE id = ?", (judge_id,))
    conn.commit()
    return cursor.rowcount > 0


def create_judgement(conn: sqlite3.Connection, judgement: Judgement) -> Judgement:
    """Create a new judgement."""
    data = judgement.to_db_dict()
    cursor = conn.execute(
        """
        INSERT OR REPLACE INTO judgements (result_id, judge_id, notes, quality, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            data["result_id"],
            data["judge_id"],
            data["notes"],
            data["quality"],
            data["created_at"],
        ),
    )
    conn.commit()
    return Judgement.from_db_dict({**data, "id": cursor.lastrowid})


def get_judgement(conn: sqlite3.Connection, judgement_id: int) -> Judgement | None:
    """Get judgement by ID."""
    cursor = conn.execute("SELECT * FROM judgements WHERE id = ?", (judgement_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return Judgement.from_db_dict(dict(row))


def get_judgement_for_result(
    conn: sqlite3.Connection, result_id: int, judge_id: int
) -> Judgement | None:
    """Get judgement for a specific result and judge."""
    cursor = conn.execute(
        "SELECT * FROM judgements WHERE result_id = ? AND judge_id = ?",
        (result_id, judge_id),
    )
    row = cursor.fetchone()
    if not row:
        return None
    return Judgement.from_db_dict(dict(row))


def list_judgements(
    conn: sqlite3.Connection, result_id: int | None = None, judge_id: int | None = None
) -> list[Judgement]:
    """List judgements with optional filtering."""
    query = "SELECT * FROM judgements WHERE 1=1"
    params: list[Any] = []

    if result_id:
        query += " AND result_id = ?"
        params.append(result_id)

    if judge_id:
        query += " AND judge_id = ?"
        params.append(judge_id)

    query += " ORDER BY created_at DESC"

    cursor = conn.execute(query, params)
    return [Judgement.from_db_dict(dict(row)) for row in cursor.fetchall()]


def delete_judgement(conn: sqlite3.Connection, judgement_id: int) -> bool:
    """Delete a judgement by ID. Returns True if deleted, False if not found."""
    cursor = conn.execute("DELETE FROM judgements WHERE id = ?", (judgement_id,))
    conn.commit()
    return cursor.rowcount > 0


def create_commit_scenario_draft(
    conn: sqlite3.Connection, draft: CommitScenarioDraft
) -> CommitScenarioDraft:
    """Create a new commit scenario draft."""
    data = draft.to_db_dict()
    cursor = conn.execute(
        """
        INSERT INTO commit_scenario_drafts (
            task_id, owner, repo, commit_sha, parent_sha, commit_message,
            commit_author, pr_number, pr_title, pr_body, diff,
            generated_prompt, generated_judge_guidance, generated_summary,
            status, error_message, scenario_id, judge_id, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["task_id"],
            data["owner"],
            data["repo"],
            data["commit_sha"],
            data["parent_sha"],
            data["commit_message"],
            data["commit_author"],
            data["pr_number"],
            data["pr_title"],
            data["pr_body"],
            data["diff"],
            data["generated_prompt"],
            data["generated_judge_guidance"],
            data["generated_summary"],
            data["status"],
            data["error_message"],
            data["scenario_id"],
            data["judge_id"],
            data["created_at"],
        ),
    )
    conn.commit()
    return CommitScenarioDraft.from_db_dict({**data, "id": cursor.lastrowid})


def get_commit_scenario_draft(
    conn: sqlite3.Connection, draft_id: int
) -> CommitScenarioDraft | None:
    """Get commit scenario draft by ID."""
    cursor = conn.execute("SELECT * FROM commit_scenario_drafts WHERE id = ?", (draft_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return CommitScenarioDraft.from_db_dict(dict(row))


def get_commit_scenario_draft_by_task(
    conn: sqlite3.Connection, task_id: int
) -> CommitScenarioDraft | None:
    """Get commit scenario draft by task ID."""
    cursor = conn.execute("SELECT * FROM commit_scenario_drafts WHERE task_id = ?", (task_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return CommitScenarioDraft.from_db_dict(dict(row))


def update_commit_scenario_draft(
    conn: sqlite3.Connection,
    draft_id: int,
    *,
    generated_prompt: str | None = None,
    generated_judge_guidance: str | None = None,
    generated_summary: str | None = None,
    status: str | None = None,
    error_message: str | None = None,
    scenario_id: int | None = None,
    judge_id: int | None = None,
) -> CommitScenarioDraft | None:
    """Update a commit scenario draft."""
    updates: list[str] = []
    params: list[Any] = []

    if generated_prompt is not None:
        updates.append("generated_prompt = ?")
        params.append(generated_prompt)
    if generated_judge_guidance is not None:
        updates.append("generated_judge_guidance = ?")
        params.append(generated_judge_guidance)
    if generated_summary is not None:
        updates.append("generated_summary = ?")
        params.append(generated_summary)
    if status is not None:
        updates.append("status = ?")
        params.append(status)
    if error_message is not None:
        updates.append("error_message = ?")
        params.append(error_message)
    if scenario_id is not None:
        updates.append("scenario_id = ?")
        params.append(scenario_id)
    if judge_id is not None:
        updates.append("judge_id = ?")
        params.append(judge_id)

    if not updates:
        return get_commit_scenario_draft(conn, draft_id)

    params.append(draft_id)
    query = f"UPDATE commit_scenario_drafts SET {', '.join(updates)} WHERE id = ?"
    conn.execute(query, params)
    conn.commit()
    return get_commit_scenario_draft(conn, draft_id)


# --- Pairwise Preference functions ---


def create_pairwise_preference(
    conn: sqlite3.Connection,
    scenario_id: int,
    result_a_id: int,
    result_b_id: int,
    preference: PreferenceType,
    confidence: float | None = None,
    notes: str | None = None,
) -> PairwisePreference:
    """Create a new pairwise preference.

    Note: result_a_id must be < result_b_id. Use PairwisePreferenceCreate
    to handle normalization automatically.
    """
    if result_a_id >= result_b_id:
        raise ValueError("result_a_id must be less than result_b_id")

    now = datetime.now().isoformat()
    cursor = conn.execute(
        """
        INSERT INTO pairwise_preferences
            (scenario_id, result_a_id, result_b_id, preference, confidence, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (scenario_id, result_a_id, result_b_id, preference.value, confidence, notes, now),
    )
    conn.commit()
    return PairwisePreference(
        id=cursor.lastrowid,  # type: ignore[arg-type]
        scenario_id=scenario_id,
        result_a_id=result_a_id,
        result_b_id=result_b_id,
        preference=preference,
        confidence=confidence,
        notes=notes,
        created_at=datetime.fromisoformat(now),
    )


def get_pairwise_preference(
    conn: sqlite3.Connection, preference_id: int
) -> PairwisePreference | None:
    """Get pairwise preference by ID."""
    cursor = conn.execute("SELECT * FROM pairwise_preferences WHERE id = ?", (preference_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return PairwisePreference.from_db_dict(dict(row))


def get_pairwise_preference_for_results(
    conn: sqlite3.Connection, result_a_id: int, result_b_id: int
) -> PairwisePreference | None:
    """Get pairwise preference for a specific pair of results."""
    # Normalize ordering
    if result_a_id > result_b_id:
        result_a_id, result_b_id = result_b_id, result_a_id

    cursor = conn.execute(
        "SELECT * FROM pairwise_preferences WHERE result_a_id = ? AND result_b_id = ?",
        (result_a_id, result_b_id),
    )
    row = cursor.fetchone()
    if not row:
        return None
    return PairwisePreference.from_db_dict(dict(row))


def list_pairwise_preferences(
    conn: sqlite3.Connection,
    scenario_id: int | None = None,
    result_id: int | None = None,
) -> list[PairwisePreference]:
    """List pairwise preferences with optional filters."""
    query = "SELECT * FROM pairwise_preferences WHERE 1=1"
    params: list[Any] = []

    if scenario_id is not None:
        query += " AND scenario_id = ?"
        params.append(scenario_id)

    if result_id is not None:
        query += " AND (result_a_id = ? OR result_b_id = ?)"
        params.append(result_id)
        params.append(result_id)

    query += " ORDER BY created_at DESC"

    cursor = conn.execute(query, params)
    return [PairwisePreference.from_db_dict(dict(row)) for row in cursor.fetchall()]


def delete_pairwise_preference(conn: sqlite3.Connection, preference_id: int) -> bool:
    """Delete a pairwise preference."""
    cursor = conn.execute("DELETE FROM pairwise_preferences WHERE id = ?", (preference_id,))
    conn.commit()
    return cursor.rowcount > 0


def update_pairwise_preference(
    conn: sqlite3.Connection,
    preference_id: int,
    preference: PreferenceType | None = None,
    confidence: float | None = None,
    notes: str | None = None,
) -> PairwisePreference | None:
    """Update a pairwise preference."""
    updates: list[str] = []
    params: list[Any] = []

    if preference is not None:
        updates.append("preference = ?")
        params.append(preference.value)
    if confidence is not None:
        updates.append("confidence = ?")
        params.append(confidence)
    if notes is not None:
        updates.append("notes = ?")
        params.append(notes)

    if not updates:
        return get_pairwise_preference(conn, preference_id)

    params.append(preference_id)
    query = f"UPDATE pairwise_preferences SET {', '.join(updates)} WHERE id = ?"
    conn.execute(query, params)
    conn.commit()
    return get_pairwise_preference(conn, preference_id)


def count_pairwise_preferences(
    conn: sqlite3.Connection,
    scenario_id: int | None = None,
) -> int:
    """Count pairwise preferences."""
    if scenario_id is not None:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM pairwise_preferences WHERE scenario_id = ?",
            (scenario_id,),
        )
    else:
        cursor = conn.execute("SELECT COUNT(*) FROM pairwise_preferences")
    return cursor.fetchone()[0]


def count_result_comparisons(
    conn: sqlite3.Connection,
    result_id: int,
) -> int:
    """Count how many comparisons a result has been involved in."""
    cursor = conn.execute(
        "SELECT COUNT(*) FROM pairwise_preferences WHERE result_a_id = ? OR result_b_id = ?",
        (result_id, result_id),
    )
    return cursor.fetchone()[0]


def get_compared_result_pairs(
    conn: sqlite3.Connection,
    scenario_id: int,
) -> set[tuple[int, int]]:
    """Get all result pairs that have been compared for a scenario."""
    cursor = conn.execute(
        "SELECT result_a_id, result_b_id FROM pairwise_preferences WHERE scenario_id = ?",
        (scenario_id,),
    )
    return {(row[0], row[1]) for row in cursor.fetchall()}
