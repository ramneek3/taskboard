import os
import sqlite3
import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]


def test_alembic_upgrade_and_downgrade(tmp_path):
    database = tmp_path / "migrated.db"
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{database}"
    upgrade = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert upgrade.returncode == 0, upgrade.stderr
    connection = sqlite3.connect(database)
    try:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(tasks)")}
        indexes = {row[1] for row in connection.execute("PRAGMA index_list(tasks)")}
    finally:
        connection.close()
    assert {"id", "title", "description", "priority", "status", "assignee", "created_at"} <= columns
    assert "ix_tasks_status" in indexes

    downgrade = subprocess.run(
        [sys.executable, "-m", "alembic", "downgrade", "base"],
        cwd=BACKEND,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert downgrade.returncode == 0, downgrade.stderr
    connection = sqlite3.connect(database)
    try:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    finally:
        connection.close()
    assert "tasks" not in tables
