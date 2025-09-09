from fastapi import APIRouter, HTTPException, Path
from ..database import SessionDep
from ..models import GameStatus
from ..schemas import GameCreate, GameJoin, GamePublic, MoveCreate
from .. import crud, game_logic
from typing import Annotated

router = APIRouter(prefix="/games", tags=["games"])

@router.post("", response_model=GamePublic, status_code=201)
def create_game(game_data: GameCreate, session: SessionDep):
    """
    Create a new game and return the game id of this game

    If the player already has an unfinished game, it will return an error.
    """
    player = crud.get_player(session, game_data.player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    unfinished_game = crud.get_player_unfinished_game(session, game_data.player_id)
    can_player_create, status_code, error_msg = game_logic.validate_player_can_join_new_game(unfinished_game)
    if not can_player_create:
        raise HTTPException(status_code=status_code, detail=error_msg)
    
    game = crud.create_game(session, game_data.player_id)
    message = f"Game created with ID: {game.id} by player {game_data.player_id}, waiting for another player to join"

    return build_game_response(game, message=message)

@router.post("/{game_id}/join", response_model=GamePublic)
def join_game(
        game_id: Annotated[int, Path(gt=0, description="Game ID must be a positive integer.")],
        join_data: GameJoin,
        session: SessionDep
    ):
    """
    Allows a player to join an existing, waiting game session.

    This endpoint validates that the game exists and is in a 'waiting'
    state before adding the second player and starting the game.
    """

    game = crud.get_game(session, game_id)
    is_game_status_valid, status_code, error_msg = game_logic.validate_game_status_for_join(game, join_data.player_id)
    if not is_game_status_valid:
        raise HTTPException(status_code=status_code, detail=error_msg)

    player = crud.get_player(session, join_data.player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    unfinished_game = crud.get_player_unfinished_game(session, join_data.player_id)
    can_player_join, status_code, error_msg = game_logic.validate_player_can_join_new_game(unfinished_game)
    if not can_player_join:
        raise HTTPException(status_code=status_code, detail=error_msg)
    
    game = crud.join_game(session, game_id, join_data.player_id)
    message = f"Player {join_data.player_id} joined game with ID: {game.id}, game is now in progress, waiting for player {game.current_turn_player_id} to make a move"
    return build_game_response(game, message=message)

@router.get("/available", response_model=list[GamePublic])
def get_available_games(session: SessionDep):
    """
    Get all games available to join (waiting for players)
    """
    games = crud.get_available_games(session)
    return [build_game_response(game) for game in games]

@router.get("/{game_id}", response_model=GamePublic)
def get_game(
        game_id: Annotated[int, Path(gt=0, description="Game ID must be a positive integer.")],
        session: SessionDep
    ):
    """
    Get a game status and grid by its id
    """
    game = crud.get_game(session, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    moves = crud.get_moves_for_game(session, game_id)
    grid = game_logic.calculate_grid_from_moves(moves, game.game_players)
    return build_game_response(game, grid)

@router.post("/{game_id}/move", response_model=GamePublic)
def make_move(
        game_id: Annotated[int, Path(gt=0, description="Game ID must be a positive integer.")],
        move_data: MoveCreate,
        session: SessionDep
    ):
    """
    Make a move in a game
    
    Only make a move if the game is in progress and it is the player's turn.
    """
    game = crud.get_game(session, game_id)

    # Validate game status
    is_game_status_valid, status_code, error_msg = game_logic.validate_game_status_for_move(game, move_data.player_id)
    if not is_game_status_valid:
        raise HTTPException(status_code=status_code, detail=error_msg)

    # Validate move using game logic
    assert game is not None
    move_number = game.current_turn_number    
    moves = crud.get_moves_for_game(session, game_id)
    grid = game_logic.calculate_grid_from_moves(moves, game.game_players)
    is_move_valid, status_code, error_msg = game_logic.validate_move(grid, move_data.position)   
    if not is_move_valid:
        raise HTTPException(status_code=status_code, detail=error_msg)
    
    move = crud.create_move(session, game_id, move_data.player_id, move_data.position, move_number)
    
    all_moves = moves + [move]
    
    # Advance the turn and check for win/draw
    game.current_turn_number += 1
    
    new_grid = game_logic.calculate_grid_from_moves(all_moves, game.game_players)
    player_number = next((gp.player_order for gp in game.game_players if gp.player_id == move_data.player_id), 0)
    
    if game_logic.check_win_condition(new_grid, player_number):
        game.status = GameStatus.FINISHED
        game.winner_id = move_data.player_id
        message = f"Player {move_data.player_id} made a move at position {move_data.position} and won! Game is now finished"
        
        update_player_stats_on_game_finish(session, game, all_moves, winner_id=move_data.player_id)
        
    elif game_logic.check_draw_condition(new_grid):
        game.status = GameStatus.FINISHED
        # winner_id remains None for draw
        message = f"Player {move_data.player_id} made a move at position {move_data.position} and it's a draw! Game is now finished"
        
        update_player_stats_on_game_finish(session, game, all_moves, winner_id=None)
    else:
        message = f"Player {move_data.player_id} made a move at position {move_data.position}, game is still in progress, waiting for player {game.current_turn_player_id} to make a move"

    session.add(game)
    session.commit()
    session.refresh(game)
    
    return build_game_response(game, new_grid, message)

def update_player_stats_on_game_finish(session: SessionDep, game, all_moves: list, winner_id: int | None):
    """
    Update player statistics when a game finishes (win or draw)
    """
    # Update stats for both players
    for game_player in game.game_players:
        player = crud.get_player(session, game_player.player_id)
        if not player:
            continue
            
        player_moves_count = len([move for move in all_moves if move.player_id == game_player.player_id])
        
        player.games_played += 1
        player.total_moves += player_moves_count
        
        if winner_id and game_player.player_id == winner_id:
            player.games_won += 1
        
        session.add(player)


def build_game_response(game, grid: list[int] = [0,0,0,0,0,0,0,0,0], message: str | None = None) -> GamePublic:
    """
    Build GamePublic response using cached moves and grid to avoid database queries
    """
    # Extract player IDs by order (no database query needed)
    player1_id = next((gp.player_id for gp in game.game_players if gp.player_order == 1), None)
    player2_id = next((gp.player_id for gp in game.game_players if gp.player_order == 2), None)
    
    return GamePublic(
        id=game.id,
        status=game.status,
        player1_id=player1_id or 0,
        player2_id=player2_id,
        current_turn_number=game.current_turn_number,
        current_turn_player_id=game.current_turn_player_id,
        winner_id=game.winner_id,
        grid=[[grid[0],grid[1],grid[2]],[grid[3],grid[4],grid[5]],[grid[6],grid[7],grid[8]]],
        message=message
    )
