"""Commit scenario draft model definitions."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class CommitScenarioDraft(BaseModel):
    """A draft scenario generated from a GitHub commit, awaiting user review."""

    id: int
    task_id: int | None = None  # Set after task is created
    owner: str
    repo: str
    commit_sha: str
    parent_sha: str
    commit_message: str
    commit_author: str | None = None
    pr_number: int | None = None
    pr_title: str | None = None
    pr_body: str | None = None
    diff: str
    generated_prompt: str | None = None
    generated_judge_guidance: str | None = None
    generated_summary: str | None = None
    status: Literal["pending", "ready", "saved", "failed"] = "pending"
    error_message: str | None = None
    scenario_id: int | None = None
    judge_id: int | None = None
    created_at: datetime

    def to_db_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "owner": self.owner,
            "repo": self.repo,
            "commit_sha": self.commit_sha,
            "parent_sha": self.parent_sha,
            "commit_message": self.commit_message,
            "commit_author": self.commit_author,
            "pr_number": self.pr_number,
            "pr_title": self.pr_title,
            "pr_body": self.pr_body,
            "diff": self.diff,
            "generated_prompt": self.generated_prompt,
            "generated_judge_guidance": self.generated_judge_guidance,
            "generated_summary": self.generated_summary,
            "status": self.status,
            "error_message": self.error_message,
            "scenario_id": self.scenario_id,
            "judge_id": self.judge_id,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_db_dict(cls, data: dict) -> "CommitScenarioDraft":
        """Create from database dictionary."""
        return cls(
            id=data["id"],
            task_id=data.get("task_id"),
            owner=data["owner"],
            repo=data["repo"],
            commit_sha=data["commit_sha"],
            parent_sha=data["parent_sha"],
            commit_message=data["commit_message"],
            commit_author=data.get("commit_author"),
            pr_number=data.get("pr_number"),
            pr_title=data.get("pr_title"),
            pr_body=data.get("pr_body"),
            diff=data["diff"],
            generated_prompt=data.get("generated_prompt"),
            generated_judge_guidance=data.get("generated_judge_guidance"),
            generated_summary=data.get("generated_summary"),
            status=data.get("status", "pending"),
            error_message=data.get("error_message"),
            scenario_id=data.get("scenario_id"),
            judge_id=data.get("judge_id"),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
