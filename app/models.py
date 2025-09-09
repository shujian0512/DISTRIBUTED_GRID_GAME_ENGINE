"""
This file contains the SQLModel for the database models.
Table definitions for Player, Game, GamePlayer, and Move. 4 tables. And their relationships.
The models are used to create the database tables and to validate the data that is passed to the database.
"""
from sqlmodel import Field, SQLModel, Relationship, UniqueConstraint
from datetime import datetime, timezone
from enum import Enum

class GameStatus(str, Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress" 
    FINISHED = "finished"

class Player(SQLModel, table=True):
    """
    Each player has a unique id.
    Also added the aggregate fields for each player to be used for the leaderboard.
    Relationships attributes easy access to a list of the game_player and moves objects for each player.
    """
    id: int | None = Field(default=None, primary_key=True)
    
    games_played: int = Field(default=0)
    games_won: int = Field(default=0)
    total_moves: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    game_players: list["GamePlayer"] = Relationship(back_populates="player")
    moves: list["Move"] = Relationship(back_populates="player")

class Game(SQLModel, table=True):
    """
    Game table has a unique id.
    current_turn_player_id field for the current turn player.
    Relationships attributes easy access to a list of the game_player and moves objects for each game.
    """
    id: int | None = Field(default=None, primary_key=True)
    current_turn_number: int = Field(default=1)
    status: GameStatus = Field(default=GameStatus.WAITING)
    winner_id: int | None = Field(default=None, foreign_key="player.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    game_players: list["GamePlayer"] = Relationship(back_populates="game")
    moves: list["Move"] = Relationship(back_populates="game")
    
    @property
    def current_turn_player_id(self) -> int | None:
        if self.status != GameStatus.IN_PROGRESS or len(self.game_players) < 2:
            return None
        
        player1 = next(gp for gp in self.game_players if gp.player_order == 1)
        player2 = next(gp for gp in self.game_players if gp.player_order == 2)
        
        return player1.player_id if self.current_turn_number % 2 == 1 else player2.player_id

class GamePlayer(SQLModel, table=True):
    """
    Association table linking players to games with metadata.
    player_order is the order of the player in the game.
    Relationships for easy accessto the Game and Player obecjt.
    """
    game_id: int = Field(foreign_key="game.id", primary_key=True)
    player_id: int = Field(foreign_key="player.id", primary_key=True)
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    player_order: int = Field(description="1 for creator, 2 for joiner")
    
    game: Game = Relationship(back_populates="game_players")
    player: Player = Relationship(back_populates="game_players")
    
    # Constraint to ensure each player only joins one game once.
    __table_args__ = (
        UniqueConstraint('game_id', 'player_order', name='unique_game_player_order'),
    )

class Move(SQLModel, table=True):
    """
    Move table for each move made in a game.
    position is from 0-8 for the 3x3 grid. 0 is the top left, 8 is the bottom right.
    move_number is the turn number when the move was made.
    Relationships for easy accessto the Game and Player obecjt.
    """
    id: int | None = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="game.id")
    player_id: int = Field(foreign_key="player.id")
    position: int = Field(ge=0, le=8)
    move_number: int = Field(description="Turn number when move was made")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    game: Game = Relationship(back_populates="moves")
    player: Player = Relationship(back_populates="moves")

    # Constraint to ensure each position is only used once per game.
    __table_args__ = (
        UniqueConstraint('game_id', 'position', name='unique_game_position'),
    )