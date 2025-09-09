# FastAPI app with API endpoints
from fastapi import FastAPI
from .database import create_db_and_tables
from .router import players, games, leaderboard

app = FastAPI()

# Include routers
app.include_router(players.router)
app.include_router(games.router)
app.include_router(leaderboard.router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
