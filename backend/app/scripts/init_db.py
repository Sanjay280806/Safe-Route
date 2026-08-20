from app.main import bootstrap_database


def main() -> None:
    bootstrap_database()
    print("Database initialized, users seeded, and placeholder data imported.")


if __name__ == "__main__":
    main()
