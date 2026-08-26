import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    secret: str
    database_path: str
    token_minutes: int


def get_settings() -> Settings:
    return Settings(
        secret=os.getenv("APP_SECRET", "development-only-change-me"),
        database_path=os.getenv("DATABASE_PATH", "./metricnest.db"),
        token_minutes=int(os.getenv("ACCESS_TOKEN_MINUTES", "60")),
    )

