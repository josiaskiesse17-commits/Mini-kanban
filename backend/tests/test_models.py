from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Board, Card, Column, User


def test_model_schema_and_relationships() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    tables = set(inspect(engine).get_table_names())
    assert tables == {"users", "boards", "columns", "cards"}

    with Session(engine) as session:
        user = User(username="alice", hashed_password="hashed")
        board = Board(name="Work", user=user)
        column = Column(name="To Do", position=0, board=board)
        Card(title="First task", priority="high", position=0, column=column)
        session.add(user)
        session.commit()

        loaded = session.query(User).one()
        assert loaded.boards[0].columns[0].cards[0].priority == "high"
        assert loaded.boards[0].columns[0].cards[0].column is loaded.boards[0].columns[0]
