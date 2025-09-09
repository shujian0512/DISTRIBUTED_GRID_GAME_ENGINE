# Simple SQLite setup
import os
from typing import Annotated
from fastapi import Depends
from sqlmodel import create_engine, Session, SQLModel
from app.models import Player, Game, GamePlayer, Move

# Get the project root directory (one level up from app/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create database in project root directory
sqlite_file_name = "database.db"
sqlite_file_path = os.path.join(PROJECT_ROOT, sqlite_file_name)
sqlite_url = f"sqlite:///{sqlite_file_path}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
