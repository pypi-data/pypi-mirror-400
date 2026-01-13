from vibelab.db.connection import (
    get_blob_dir,
    get_db_dir,
    get_db_path,
    get_repos_dir,
    get_results_dir,
    get_tmp_dir,
    get_worktrees_dir,
)


def test_three_tier_storage_layout(tmp_path, monkeypatch):
    """Test the three-tier storage layout: db/, blob/, tmp/."""
    monkeypatch.setenv("VIBELAB_HOME", str(tmp_path))

    # Tier 1: db/ - Database storage
    assert get_db_dir() == tmp_path / "db"
    assert get_db_path() == tmp_path / "db" / "data.db"

    # Tier 2: blob/ - Persistent application artifacts
    assert get_blob_dir() == tmp_path / "blob"

    # Results are stored under blob/projects/{project_id}/results/
    assert get_results_dir(1) == tmp_path / "blob" / "projects" / "1" / "results"
    assert get_results_dir(42) == tmp_path / "blob" / "projects" / "42" / "results"

    # Tier 3: tmp/ - Ephemeral/deletable cache
    assert get_tmp_dir() == tmp_path / "tmp"
    assert get_repos_dir() == tmp_path / "tmp" / "repos"
    assert get_worktrees_dir() == tmp_path / "tmp" / "worktrees"


def test_directories_are_created(tmp_path, monkeypatch):
    """Test that directories are created when accessed."""
    monkeypatch.setenv("VIBELAB_HOME", str(tmp_path))

    # Access various directories - they should be created
    db_dir = get_db_dir()
    blob_dir = get_blob_dir()
    tmp_dir = get_tmp_dir()
    repos_dir = get_repos_dir()
    worktrees_dir = get_worktrees_dir()
    results_dir = get_results_dir(1)

    assert db_dir.exists()
    assert blob_dir.exists()
    assert tmp_dir.exists()
    assert repos_dir.exists()
    assert worktrees_dir.exists()
    assert results_dir.exists()


def test_results_dir_per_project(tmp_path, monkeypatch):
    """Test that results are isolated by project_id."""
    monkeypatch.setenv("VIBELAB_HOME", str(tmp_path))

    # Create results dirs for different projects
    results_1 = get_results_dir(1)
    results_2 = get_results_dir(2)

    # They should be in different directories
    assert results_1 != results_2
    assert results_1.parent.name == "1"
    assert results_2.parent.name == "2"

    # Both should exist under blob/projects/
    assert "blob" in str(results_1)
    assert "blob" in str(results_2)
