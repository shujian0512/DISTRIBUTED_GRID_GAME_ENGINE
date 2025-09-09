from .models import Move, GamePlayer, GameStatus, Game

WIN_PATTERNS = [    
    # Rows
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    # Columns
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    # Diagonals
    [0, 4, 8],
    [2, 4, 6],
]

def calculate_grid_from_moves(
    moves: list[Move], game_players: list[GamePlayer]
) -> list[int]:
    """Calculate 3x3 grid state from moves"""
    grid = [0] * 9  # 0 = empty

    # Create player_id to player_order mapping
    player_order_map = {gp.player_id: gp.player_order for gp in game_players}

    # Fill grid based on moves
    for move in moves:
        player_number = player_order_map.get(move.player_id, 0)
        grid[move.position] = player_number

    return grid
    
def validate_player_can_join_new_game(unfinished_game : Game | None) -> tuple[bool, int, str]:
    """
    Check if player has unfinished games before joining/creating a new game
    """
    if unfinished_game:
        from .models import GameStatus  # Import here to avoid circular imports
        status_msg = "waiting for another player" if unfinished_game.status == GameStatus.WAITING else "in progress"
        return False, 409, f"Player already has an unfinished game (ID: {unfinished_game.id}) that is {status_msg}. Complete that game first."
    
    return True, 200, "Player can join new game"

def validate_game_status_for_join(game: Game | None, player_id: int) -> tuple[bool, int, str]:
    """
    Validate game status before joining a game
    """
    if not game:
        return False, 404, "Game not found"

    if player_id in [gp.player_id for gp in game.game_players]:
        return False, 409, "Player already in game"

    if game.status != GameStatus.WAITING:
        return False, 409, "Game already started or finished"

    if len(game.game_players) >= 2:
        return False, 409, "Game is full"
    
    return True, 200, "Valid game status"

def validate_game_status_for_move(game: Game | None, player_id: int) -> tuple[bool, int, str]:
    """
    Validate game status before making a move
    """
    if not game:
        return False, 404, "Game not found"

    if game.status != GameStatus.IN_PROGRESS:
        return False, 409, "Game is not in progress"

    if len(game.game_players) < 2:
        return False, 409, "Game is not full"

    if player_id not in [gp.player_id for gp in game.game_players]:
        return False, 403, "Player not in game"

    if game.current_turn_player_id != player_id:
        return False, 409, "Not your turn"

    return True, 200, "Valid game status"


def check_win_condition(grid: list[int], player_number: int) -> bool:
    """
    Check if player has won the game after making a move
    """
    for pattern in WIN_PATTERNS:
        if all(grid[pos] == player_number for pos in pattern):
            return True

    return False


def check_draw_condition(grid: list[int]) -> bool:
    """Check if game is a draw (board full, no winner)"""
    if check_win_condition(grid, 1) or check_win_condition(grid, 2):
        return False
    
    return all(cell != 0 for cell in grid)

def validate_move(grid: list[int], position: int) -> tuple[bool, int, str]:
    """Validate if a move is legal"""
    if grid[position] != 0:
        return False, 409, "Position already occupied"

    return True, 200, "Valid move"