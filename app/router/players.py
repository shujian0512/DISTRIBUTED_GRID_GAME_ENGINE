from fastapi import APIRouter, HTTPException, Path
from ..database import SessionDep
from ..schemas import PlayerPublic
from .. import crud
from typing import Annotated

router = APIRouter(prefix="/players", tags=["players"])


@router.post("", response_model=PlayerPublic, status_code=201)
def create_player(session: SessionDep):
    """
    Create a new player and return the player id of this player
    """
    player = crud.create_player(session)
    assert player.id is not None
    return PlayerPublic(
        id=player.id,
        games_played=player.games_played,
        games_won=player.games_won,
        message=f"Player created with ID: {player.id}",
    )


@router.get("/{player_id}", response_model=PlayerPublic)
def get_player(
        player_id: Annotated[int, Path(gt=0, description="Player ID must be a positive integer.")],
        session: SessionDep
    ):
    """
    Get a player info by their id
    """
    player = crud.get_player(session, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    assert player.id is not None
    return PlayerPublic(
        id=player.id,
        games_played=player.games_played,
        games_won=player.games_won,
        message=f"Player with ID: {player.id} found",
    )