from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class BoardCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class BoardUpdate(BoardCreate):
    pass


class ColumnCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class ColumnUpdate(ColumnCreate):
    pass


class ReorderRequest(BaseModel):
    ids: list[int] = Field(min_length=1)


class CardCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    description: str = Field(default="", max_length=5000)
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    due_date: date | None = None
    position: int = Field(default=0, ge=0)


class CardUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=5000)
    priority: str | None = Field(default=None, pattern="^(low|medium|high)$")
    due_date: date | None = None
    position: int | None = Field(default=None, ge=0)


class CardMove(BaseModel):
    column_id: int = Field(ge=1)
    position: int = Field(ge=0)


class CardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    column_id: int
    title: str
    description: str
    priority: str
    due_date: date | None
    position: int
    created_at: datetime
    updated_at: datetime


class ColumnResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    board_id: int
    name: str
    position: int
    cards: list[CardResponse]


class BoardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    columns: list[ColumnResponse]
