from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from sql_agent.config import Settings
from sql_agent.database import create_database, seed_demo_database


def test_settings_use_demo_database_by_default(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = Settings.from_env()
    assert settings.database_url == "sqlite:///data/example.db"


def test_settings_use_environment_overrides(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///tmp/custom.db")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-flash")

    settings = Settings.from_env()

    assert settings.database_url == "sqlite:///tmp/custom.db"
    assert settings.google_api_key == "test-key"
    assert settings.gemini_model == "gemini-2.5-flash"


def test_create_database_creates_parent_directory_for_sqlite_file(tmp_path: Path):
    nested_dir = tmp_path / "nested" / "db"
    database_url = f"sqlite:///{nested_dir / 'orders.db'}"

    create_database(database_url)

    assert nested_dir.exists()


def test_seed_demo_database_inserts_expected_rows(tmp_path: Path):
    database_url = f"sqlite:///{tmp_path / 'orders.db'}"
    seed_demo_database(database_url)

    engine = create_engine(database_url)
    with engine.connect() as connection:
        rows = connection.execute(
            text(
                "SELECT customer, product, quantity, total_cents FROM orders ORDER BY id"
            )
        ).all()

    assert rows == [
        ("Ada Lovelace", "Notebook", 2, 2400),
        ("Grace Hopper", "Keyboard", 1, 8900),
        ("Ada Lovelace", "Monitor", 1, 21900),
        ("Linus Torvalds", "Notebook", 5, 6000),
    ]


def test_seed_demo_database_rejects_non_sqlite_database_urls():
    with pytest.raises(ValueError, match="only supports SQLite"):
        seed_demo_database("postgresql://localhost/test")


def test_seed_demo_database_is_idempotent(tmp_path: Path):
    database_url = f"sqlite:///{tmp_path / 'orders.db'}"
    seed_demo_database(database_url)
    seed_demo_database(database_url)

    engine = create_engine(database_url)
    with engine.connect() as connection:
        count = connection.execute(text("SELECT COUNT(*) FROM orders")).scalar_one()

    assert count == 4


