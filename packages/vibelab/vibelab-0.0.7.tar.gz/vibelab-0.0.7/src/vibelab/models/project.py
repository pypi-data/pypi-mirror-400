"""Project model definitions."""

from datetime import datetime

from pydantic import BaseModel


class Project(BaseModel):
    """A VibeLab project - a namespace for scenarios, datasets, and tasks."""

    id: int
    name: str
    description: str | None = None
    created_at: datetime

    def to_db_dict(self) -> dict[str, object]:
        """Convert to dictionary for database storage."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_db_dict(cls, data: dict[str, object]) -> "Project":
        """Create from database dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
