from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Board, Card, Column, User
from app.seed import DEVELOPMENT_USERNAME, seed_database


def test_seed_is_deterministic_and_complete() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        seed_database(session)
        seed_database(session)

        users = session.scalars(select(User)).all()
        boards = session.scalars(select(Board)).all()
        columns = session.scalars(select(Column).order_by(Column.position)).all()
        cards = session.scalars(select(Card).order_by(Card.id)).all()

        assert [user.username for user in users] == [DEVELOPMENT_USERNAME]
        assert [board.name for board in boards] == ["Development Board"]
        assert [column.name for column in columns] == ["To Do", "In Progress", "Done"]
        assert len(cards) == 4
        assert {card.priority for card in cards} == {"low", "medium", "high"}
        assert len({card.due_date for card in cards}) == 4
