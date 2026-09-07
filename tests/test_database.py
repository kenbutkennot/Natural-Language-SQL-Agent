from pathlib import Path

from sqlalchemy import create_engine, text

from sql_agent.config import Settings
from sql_agent.database import seed_demo_database


def test_settings_use_demo_database_by_default(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = Settings.from_env()
    assert settings.database_url == "sqlite:///data/example.db"


def test_seed_demo_database_is_idempotent(tmp_path: Path):
    database_url = f"sqlite:///{tmp_path / 'orders.db'}"
    seed_demo_database(database_url)
    seed_demo_database(database_url)

    engine = create_engine(database_url)
    with engine.connect() as connection:
        count = connection.execute(text("SELECT COUNT(*) FROM orders")).scalar_one()

    assert count == 4
