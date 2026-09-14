from datetime import date

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.auth.security import hash_password
from app.database import Base, SessionLocal, engine
from app.models import Board, Card, Column, User

DEVELOPMENT_USERNAME = "dev@example.com"
DEVELOPMENT_PASSWORD = "dev-password-123"


def seed_database(db: Session) -> None:
    db.execute(delete(Card))
    db.execute(delete(Column))
    db.execute(delete(Board))
    db.execute(delete(User))

    user = User(
        username=DEVELOPMENT_USERNAME,
        hashed_password=hash_password(DEVELOPMENT_PASSWORD),
    )
    board = Board(name="Development Board", user=user)
    todo = Column(name="To Do", position=0, board=board)
    progress = Column(name="In Progress", position=1, board=board)
    done = Column(name="Done", position=2, board=board)
    todo.cards = [
        Card(
            title="Connect frontend to API",
            description="Build the shared API client.",
            priority="high",
            due_date=date(2026, 9, 20),
            position=0,
        ),
        Card(
            title="Review empty states",
            description="Check loading and empty board views.",
            priority="low",
            due_date=date(2026, 9, 24),
            position=1,
        ),
    ]
    progress.cards = [
        Card(
            title="Implement drag and drop",
            description="Persist card movement and ordering.",
            priority="high",
            due_date=date(2026, 9, 18),
            position=0,
        )
    ]
    done.cards = [
        Card(
            title="Define API contract",
            description="Document the MVP endpoints in OpenAPI.",
            priority="medium",
            due_date=date(2026, 9, 12),
            position=0,
        )
    ]
    db.add(user)
    db.commit()


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)
    print(f"Seeded {DEVELOPMENT_USERNAME} with Development Board")


if __name__ == "__main__":
    main()
