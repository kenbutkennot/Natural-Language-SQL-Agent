from pathlib import Path

from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine, text


# Minimal sample schema used to validate SQL interactions in the demo app.
SAMPLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    customer TEXT NOT NULL,
    product TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    total_cents INTEGER NOT NULL,
    ordered_at TEXT NOT NULL
)
"""

# Seed rows chosen to exercise common SQL questions like totals, customers, and product trends.
SAMPLE_ROWS = [
    (1, "Ada Lovelace", "Notebook", 2, 2400, "2026-01-05"),
    (2, "Grace Hopper", "Keyboard", 1, 8900, "2026-01-09"),
    (3, "Ada Lovelace", "Monitor", 1, 21900, "2026-02-02"),
    (4, "Linus Torvalds", "Notebook", 5, 6000, "2026-02-14"),
]


def create_database(database_url: str) -> SQLDatabase:
    """Create a LangChain SQLDatabase, creating local SQLite parent folders."""
    # Ensure a file-based SQLite path has a directory available before creating the database.
    if database_url.startswith("sqlite:///") and ":memory:" not in database_url:
        database_path = Path(database_url.removeprefix("sqlite:///"))
        database_path.parent.mkdir(parents=True, exist_ok=True)

    return SQLDatabase.from_uri(database_url)


def seed_demo_database(database_url: str) -> None:
    """Create the demo orders table and seed it once."""
    if not database_url.startswith("sqlite:///"):
        raise ValueError("The demo seed command only supports SQLite databases.")

    # SQLite file databases need a parent directory before the engine can open them.
    if ":memory:" not in database_url:
        database_path = Path(database_url.removeprefix("sqlite:///"))
        database_path.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.execute(text(SAMPLE_SCHEMA))
        count = connection.execute(text("SELECT COUNT(*) FROM orders")).scalar_one()
        if count == 0:
            connection.execute(
                text(
                    "INSERT INTO orders "
                    "(id, customer, product, quantity, total_cents, ordered_at) "
                    "VALUES (:id, :customer, :product, :quantity, :total_cents, :ordered_at)"
                ),
                [
                    {
                        "id": row[0],
                        "customer": row[1],
                        "product": row[2],
                        "quantity": row[3],
                        "total_cents": row[4],
                        "ordered_at": row[5],
                    }
                    for row in SAMPLE_ROWS
                ],
            )
