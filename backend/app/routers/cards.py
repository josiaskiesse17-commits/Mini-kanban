from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.database import get_db
from app.models import Card, Column, User
from app.schemas.kanban import (
    CardCreate,
    CardMove,
    CardResponse,
    CardUpdate,
    ReorderRequest,
)

router = APIRouter(tags=["Cards"])


def require_column(column_id: int, user: User, db: Session) -> Column:
    column = db.get(Column, column_id)
    if column is None:
        raise HTTPException(status_code=404, detail="Column not found")
    if column.board.user_id != user.id:
        raise HTTPException(status_code=403, detail="You do not own this column")
    return column


def require_card(card_id: int, user: User, db: Session) -> Card:
    card = db.get(Card, card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")
    if card.column.board.user_id != user.id:
        raise HTTPException(status_code=403, detail="You do not own this card")
    return card


def ordered_cards(column: Column) -> list[Card]:
    return sorted(column.cards, key=lambda card: card.position)


@router.post(
    "/columns/{column_id}/cards",
    response_model=CardResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_card(
    column_id: int,
    request: CardCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Card:
    column = require_column(column_id, user, db)
    cards = ordered_cards(column)
    position = min(request.position, len(cards))
    card = Card(
        title=request.title,
        description=request.description,
        priority=request.priority,
        due_date=request.due_date,
        position=position,
        column=column,
    )
    for existing in cards[position:]:
        existing.position += 1
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


@router.get("/cards/{card_id}", response_model=CardResponse)
def get_card(
    card_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Card:
    return require_card(card_id, user, db)


@router.patch("/cards/{card_id}", response_model=CardResponse)
def update_card(
    card_id: int,
    request: CardUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Card:
    card = require_card(card_id, user, db)
    updates = request.model_dump(exclude_unset=True)
    requested_position = updates.pop("position", None)
    for field, value in updates.items():
        setattr(card, field, value)
    if requested_position is not None:
        cards = [item for item in ordered_cards(card.column) if item.id != card.id]
        position = min(requested_position, len(cards))
        cards.insert(position, card)
        for index, item in enumerate(cards):
            item.position = index
    db.commit()
    db.refresh(card)
    return card


@router.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(
    card_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> None:
    card = require_card(card_id, user, db)
    source_cards = [item for item in ordered_cards(card.column) if item.id != card.id]
    for index, item in enumerate(source_cards):
        item.position = index
    db.delete(card)
    db.commit()


@router.post("/cards/{card_id}/move", response_model=CardResponse)
def move_card(
    card_id: int,
    request: CardMove,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Card:
    card = require_card(card_id, user, db)
    target_column = require_column(request.column_id, user, db)
    source_column = card.column
    target_cards = [item for item in ordered_cards(target_column) if item.id != card.id]
    if target_column.id == source_column.id:
        target_cards = [item for item in ordered_cards(source_column) if item.id != card.id]
    position = min(request.position, len(target_cards))
    target_cards.insert(position, card)
    card.column = target_column
    for index, item in enumerate(target_cards):
        item.position = index
    if source_column.id != target_column.id:
        for index, item in enumerate(ordered_cards(source_column)):
            item.position = index
    db.commit()
    db.refresh(card)
    return card


@router.put("/columns/{column_id}/cards/reorder", response_model=list[CardResponse])
def reorder_cards(
    column_id: int,
    request: ReorderRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Card]:
    column = require_column(column_id, user, db)
    cards_by_id = {card.id: card for card in column.cards}
    if len(request.ids) != len(cards_by_id) or set(request.ids) != set(cards_by_id):
        raise HTTPException(status_code=422, detail="IDs must contain every column card exactly once")
    for position, card_id in enumerate(request.ids):
        cards_by_id[card_id].position = position
    db.commit()
    return sorted(column.cards, key=lambda card: card.position)
