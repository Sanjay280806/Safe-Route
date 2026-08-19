from app.database import SessionLocal
from app.services.seed_service import seed_users


def main() -> None:
    db = SessionLocal()
    try:
        created = seed_users(db)
        print("Seeded users:" + (", ".join(created) if created else " already present"))
    finally:
        db.close()


if __name__ == "__main__":
    main()
