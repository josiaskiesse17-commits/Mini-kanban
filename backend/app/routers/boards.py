from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.database import get_db
from app.models import Board, Column, User
from app.schemas.kanban import (
    BoardCreate,
    BoardResponse,
    BoardUpdate,
    ColumnCreate,
    ColumnResponse,
    ColumnUpdate,
    ReorderRequest,
)

router = APIRouter(tags=["Boards", "Columns"])


def require_board(board_id: int, user: User, db: Session) -> Board:
    board = db.get(Board, board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    if board.user_id != user.id:
        raise HTTPException(status_code=403, detail="You do not own this board")
    return board


def require_column(column_id: int, user: User, db: Session) -> Column:
    column = db.get(Column, column_id)
    if column is None:
        raise HTTPException(status_code=404, detail="Column not found")
    if column.board.user_id != user.id:
        raise HTTPException(status_code=403, detail="You do not own this column")
    return column


@router.get("/boards", response_model=list[BoardResponse])
def list_boards(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Board]:
    return list(user.boards)


@router.post("/boards", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
def create_board(
    request: BoardCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Board:
    board = Board(name=request.name, user=user)
    board.columns = [
        Column(name="To Do", position=0),
        Column(name="In Progress", position=1),
        Column(name="Done", position=2),
    ]
    db.add(board)
    db.commit()
    db.refresh(board)
    return board


@router.get("/boards/{board_id}", response_model=BoardResponse)
def get_board(
    board_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Board:
    return require_board(board_id, user, db)


@router.patch("/boards/{board_id}", response_model=BoardResponse)
def update_board(
    board_id: int,
    request: BoardUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Board:
    board = require_board(board_id, user, db)
    board.name = request.name
    db.commit()
    db.refresh(board)
    return board


@router.delete("/boards/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_board(
    board_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> None:
    board = require_board(board_id, user, db)
    db.delete(board)
    db.commit()


@router.post(
    "/boards/{board_id}/columns",
    response_model=ColumnResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_column(
    board_id: int,
    request: ColumnCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Column:
    board = require_board(board_id, user, db)
    position = len(board.columns)
    column = Column(name=request.name, position=position, board=board)
    db.add(column)
    db.commit()
    db.refresh(column)
    return column


@router.patch("/columns/{column_id}", response_model=ColumnResponse)
def update_column(
    column_id: int,
    request: ColumnUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Column:
    column = require_column(column_id, user, db)
    column.name = request.name
    db.commit()
    db.refresh(column)
    return column


@router.delete("/columns/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_column(
    column_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> None:
    column = require_column(column_id, user, db)
    if column.cards:
        raise HTTPException(
            status_code=409,
            detail="Move or delete cards before deleting this column",
        )
    db.delete(column)
    db.commit()


@router.put("/boards/{board_id}/columns/reorder", response_model=list[ColumnResponse])
def reorder_columns(
    board_id: int,
    request: ReorderRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Column]:
    board = require_board(board_id, user, db)
    columns_by_id = {column.id: column for column in board.columns}
    if len(request.ids) != len(columns_by_id) or set(request.ids) != set(columns_by_id):
        raise HTTPException(status_code=422, detail="IDs must contain every board column exactly once")
    for position, column_id in enumerate(request.ids):
        columns_by_id[column_id].position = position
    db.commit()
    return sorted(board.columns, key=lambda column: column.position)
