"""Pytest configuration."""

import pytest

from vibelab.db import get_db
from vibelab.db.connection import init_db, set_current_project_id
from vibelab.db.queries import get_or_create_project


@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    """Initialize an isolated VIBELAB_HOME + project DB for each test.

    Creates a 'test' project and sets it as the current project context.
    """
    monkeypatch.setenv("VIBELAB_HOME", str(tmp_path / ".vibelab"))
    monkeypatch.setenv("VIBELAB_PROJECT", "test")
    init_db()

    # Create a project and set it as the current context
    for db in get_db():
        project = get_or_create_project(db, "test")
        set_current_project_id(project.id)
        break

    yield

    # Clean up context
    set_current_project_id(None)
