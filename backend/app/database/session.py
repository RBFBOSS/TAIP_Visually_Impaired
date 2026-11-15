from app.database.connection import engine
from collections.abc import Generator
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()