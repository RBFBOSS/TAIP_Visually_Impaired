from sqlalchemy import text

from app.database.connection import engine


def check_database_connection() -> bool:
    """Checks if the DB connection is working."""

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return True

    except Exception as error:
        print(f"Database connection failed: {error}")
        return False