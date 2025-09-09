from pydantic import BaseModel, Field
from typing import Annotated

from .models import GameStatus

class PlayerPublic(BaseModel):
    """Response schema for player"""
    id: int
    games_played: int
    games_won: int
    message: str | None = None

class PlayerStats(BaseModel):
    """Detailed player statistics for leaderboard"""
    player_id: int
    games_played: int
    games_won: int
    total_moves: int
    win_rate: float
    efficiency: float
    rank: int | None = None


class GameCreate(BaseModel):
    """Request schema for creating a game"""
    player_id: Annotated[int, Field(gt=0, description="Player ID must be a positive integer.")]

class GameJoin(BaseModel):
    """Request schema for joining a game"""
    player_id: Annotated[int, Field(gt=0, description="Player ID must be a positive integer.")]

class GamePublic(BaseModel):
    """Response schema for game state"""
    id: int
    status: GameStatus
    player1_id: int
    player2_id: int | None
    current_turn_number: int
    current_turn_player_id: int | None
    winner_id: int | None
    grid: list[list[int]] = Field(description="3x3 grid as list of 2D list (0=empty, 1=player1, 2=player2)")
    message: str | None = None


class MoveCreate(BaseModel):
    """Request schema for making a move"""
    player_id: Annotated[int, Field(gt=0, description="Player ID must be a positive integer.")]
    position: int = Field(ge=0, le=8, description="Grid position 0-8")


class LeaderboardResponse(BaseModel):
    """Response schema for leaderboard"""
    top_players_by_efficiency: list[PlayerStats]
    top_players_by_wins: list[PlayerStats]
    top_players_by_win_rate: list[PlayerStats]