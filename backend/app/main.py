from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models import Board, Card, Column, User
from app.routers.auth import router as auth_router
from app.routers.boards import router as boards_router
from app.routers.cards import router as cards_router
from app.routers.health import router as health_router


@asynccontextmanager
async def lifespan(_: FastAPI):
	Base.metadata.create_all(bind=engine)
	yield


app = FastAPI(title="Mini Kanban API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(boards_router)
app.include_router(cards_router)
