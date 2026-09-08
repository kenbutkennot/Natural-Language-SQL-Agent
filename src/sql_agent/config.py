from dataclasses import dataclass
import os

from dotenv import load_dotenv

# Load application-level environment values from a local .env file when present.
load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite:///data/example.db"
    google_api_key: str | None = None
    gemini_model: str = "gemini-3.5-flash-lite"

    @classmethod
    def from_env(cls) -> "Settings":
        # Keep config centralized so CLI and Streamlit share the same defaults and overrides.
        return cls(
            database_url=os.getenv("DATABASE_URL", cls.database_url),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            gemini_model=os.getenv("GEMINI_MODEL", cls.gemini_model),
        )
