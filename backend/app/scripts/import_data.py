from app.database import SessionLocal
from app.services.import_service import import_all


def main() -> None:
    db = SessionLocal()
    try:
        counts = import_all(db)
        print(f"Imported {counts}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
