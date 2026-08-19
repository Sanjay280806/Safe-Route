from collections.abc import Generator

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session, sessionmaker
except ImportError:
    create_engine = None
    Session = object
    sessionmaker = None

from app.config import DATABASE_URL


if create_engine is not None and sessionmaker is not None:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None
    SessionLocal = None


def get_db() -> Generator[Session, None, None]:
    if SessionLocal is None:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
