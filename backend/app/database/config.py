from pydantic_settings import BaseSettings, SettingsConfigDict

from sqlalchemy import URL


class Settings(BaseSettings):
    """Database configuration loaded from environment variables."""

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    APP_ENV: str = "development"

    model_config = SettingsConfigDict(
        env_file="backend/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def DATABASE_URL(self) -> str:
        """Build the SQLAlchemy connection URL for PostgreSQL using the `psycopg` driver."""

        return URL.create(
            drivername="postgresql+psycopg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )


settings = Settings()
