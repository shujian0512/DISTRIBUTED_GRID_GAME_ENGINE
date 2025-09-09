from datetime import datetime, timezone

from app.game_logic import (
    calculate_grid_from_moves, check_win_condition, check_draw_condition, validate_move,
    validate_player_can_join_new_game, validate_game_status_for_join, validate_game_status_for_move
)
from app.models import Move, GamePlayer, Game, GameStatus


class TestGameLogic:
    def test_calculate_grid_from_moves(self):
        assert calculate_grid_from_moves([], []) == [0,0,0,0,0,0,0,0,0]
        
        # Create actual model instances for testing (without database)
        game_players = [
            GamePlayer(game_id=1, player_id=1, player_order=1, joined_at=datetime.now(timezone.utc)),
            GamePlayer(game_id=1, player_id=2, player_order=2, joined_at=datetime.now(timezone.utc))
        ]
        
        moves = [
            Move(game_id=1, player_id=1, position=0, move_number=1, created_at=datetime.now(timezone.utc)),
            Move(game_id=1, player_id=2, position=4, move_number=2, created_at=datetime.now(timezone.utc)),
            Move(game_id=1, player_id=1, position=8, move_number=3, created_at=datetime.now(timezone.utc)),
        ]
        
        expected_grid = [1, 0, 0, 0, 2, 0, 0, 0, 1]
        assert calculate_grid_from_moves(moves, game_players) == expected_grid

    def test_check_win_condition(self):
        # Test horizontal wins
        assert check_win_condition([1,1,1,0,0,0,0,0,0], 1)  
        assert check_win_condition([0,0,0,1,1,1,0,0,0], 1)
        assert check_win_condition([0,0,0,0,0,0,1,1,1], 1)
        
        # Test vertical wins
        assert check_win_condition([1,0,0,1,0,0,1,0,0], 1)
        assert check_win_condition([0,1,0,0,1,0,0,1,0], 1)
        assert check_win_condition([0,0,1,0,0,1,0,0,1], 1)
        
        # Test diagonal wins
        assert check_win_condition([1,0,0,0,1,0,0,0,1], 1)
        assert check_win_condition([0,0,1,0,1,0,1,0,0], 1)
        
        # Test no win conditions
        assert not check_win_condition([2,1,2,1,1,2,1,2,1], 1)
        assert not check_win_condition([0,0,0,0,0,0,0,0,0], 1)
        assert not check_win_condition([1,1,2,0,0,0,0,0,0], 1)

    def test_check_draw_condition(self):
        assert not check_draw_condition([0,0,0,0,0,0,0,0,0])
        assert not check_draw_condition([0,1,2,0,0,0,0,0,0])
        assert not check_draw_condition([1,1,2,2,2,1,2,1,0])
        
        # Full board, no winner
        assert check_draw_condition([2,1,2,1,1,2,1,2,1])

    def test_validate_move(self):
        # Test valid moves on empty board
        empty_grid = [0,0,0,0,0,0,0,0,0]
        assert validate_move(empty_grid, 0) == (True, 200, "Valid move")
        assert validate_move(empty_grid, 1) == (True, 200, "Valid move")
        assert validate_move(empty_grid, 2) == (True, 200, "Valid move")
        assert validate_move(empty_grid, 3) == (True, 200, "Valid move")
        assert validate_move(empty_grid, 4) == (True, 200, "Valid move")
        assert validate_move(empty_grid, 5) == (True, 200, "Valid move")
        assert validate_move(empty_grid, 6) == (True, 200, "Valid move")
        assert validate_move(empty_grid, 7) == (True, 200, "Valid move")
        assert validate_move(empty_grid, 8) == (True, 200, "Valid move")
        
        # Test invalid moves on occupied positions
        occupied_grid = [1,2,0,1,0,2,0,1,2]
        assert validate_move(occupied_grid, 0) == (False, 409, "Position already occupied")
        assert validate_move(occupied_grid, 1) == (False, 409, "Position already occupied")
        assert validate_move(occupied_grid, 3) == (False, 409, "Position already occupied")
        
        # Test valid moves on partially occupied board
        assert validate_move(occupied_grid, 2) == (True, 200, "Valid move")
        assert validate_move(occupied_grid, 4) == (True, 200, "Valid move")
        assert validate_move(occupied_grid, 6) == (True, 200, "Valid move")


    def test_validate_player_can_join_new_game(self):
        """Test validation for player joining/creating new games"""
        
        # Test case 1: No unfinished game (player can join)
        assert validate_player_can_join_new_game(None) == (True, 200, "Player can join new game")
        
        # Test case 2: Player has unfinished game in WAITING status
        waiting_game = Game(
            id=1,
            status=GameStatus.WAITING,
            current_turn_number=1,
            created_at=datetime.now(timezone.utc)
        )
        
        is_valid, status_code, message = validate_player_can_join_new_game(waiting_game)
        assert not is_valid
        assert status_code == 409
        assert "waiting for another player" in message
        assert "ID: 1" in message
        
        # Test case 3: Player has unfinished game in IN_PROGRESS status  
        in_progress_game = Game(
            id=2,
            status=GameStatus.IN_PROGRESS,
            current_turn_number=3,
            created_at=datetime.now(timezone.utc)
        )
        
        is_valid, status_code, message = validate_player_can_join_new_game(in_progress_game)
        assert not is_valid
        assert status_code == 409
        assert "in progress" in message
        assert "ID: 2" in message


    def test_validate_game_status_for_join(self):
        """Test validation for joining an existing game"""
        
        # Test case 1: Game not found (None)
        is_valid, status_code, message = validate_game_status_for_join(None, player_id=1)
        assert not is_valid
        assert status_code == 404
        assert message == "Game not found"
        
        # Test case 2: Game already started (IN_PROGRESS)
        in_progress_game = Game(
            id=1,
            status=GameStatus.IN_PROGRESS,
            current_turn_number=1,
            created_at=datetime.now(timezone.utc)
        )
        
        is_valid, status_code, message = validate_game_status_for_join(in_progress_game, player_id=1)
        assert not is_valid
        assert status_code == 409
        assert message == "Game already started or finished"
        
        # Test case 3: Game finished
        finished_game = Game(
            id=2,
            status=GameStatus.FINISHED,
            current_turn_number=5,
            winner_id=1,
            created_at=datetime.now(timezone.utc)
        )
        
        is_valid, status_code, message = validate_game_status_for_join(finished_game, player_id=2)
        assert not is_valid
        assert status_code == 409
        assert message == "Game already started or finished"
        
        # Test case 4: Game is full (2 players already)
        waiting_game_full = Game(
            id=3,
            status=GameStatus.WAITING,
            current_turn_number=1,
            created_at=datetime.now(timezone.utc)
        )
        waiting_game_full.game_players = [
            GamePlayer(game_id=3, player_id=1, player_order=1, joined_at=datetime.now(timezone.utc)),
            GamePlayer(game_id=3, player_id=2, player_order=2, joined_at=datetime.now(timezone.utc))
        ]
        
        is_valid, status_code, message = validate_game_status_for_join(waiting_game_full, player_id=3)
        assert not is_valid
        assert status_code == 409
        assert message == "Game is full"
        
        # Test case 5: Player already in game
        waiting_game_with_player = Game(
            id=4,
            status=GameStatus.WAITING,
            current_turn_number=1,
            created_at=datetime.now(timezone.utc)
        )
        waiting_game_with_player.game_players = [
            GamePlayer(game_id=4, player_id=1, player_order=1, joined_at=datetime.now(timezone.utc))
        ]
        
        is_valid, status_code, message = validate_game_status_for_join(waiting_game_with_player, player_id=1)
        assert not is_valid
        assert status_code == 409
        assert message == "Player already in game"
        
        # Test case 6: Valid join scenario
        waiting_game_valid = Game(
            id=5,
            status=GameStatus.WAITING,
            current_turn_number=1,
            created_at=datetime.now(timezone.utc)
        )
        waiting_game_valid.game_players = [
            GamePlayer(game_id=5, player_id=1, player_order=1, joined_at=datetime.now(timezone.utc))
        ]
        
        is_valid, status_code, message = validate_game_status_for_join(waiting_game_valid, player_id=2)
        assert is_valid
        assert status_code == 200
        assert message == "Valid game status"


    def test_validate_game_status_for_move(self):
        """Test validation for making a move in a game"""
        
        # Test case 1: Game not found (None)
        is_valid, status_code, message = validate_game_status_for_move(None, player_id=1)
        assert not is_valid
        assert status_code == 404
        assert message == "Game not found"
        
        # Test case 2: Game not in progress (WAITING)
        waiting_game = Game(
            id=1,
            status=GameStatus.WAITING,
            current_turn_number=1,
            created_at=datetime.now(timezone.utc)
        )
        
        is_valid, status_code, message = validate_game_status_for_move(waiting_game, player_id=1)
        assert not is_valid
        assert status_code == 409
        assert message == "Game is not in progress"
        
        # Test case 3: Game finished
        finished_game = Game(
            id=2,
            status=GameStatus.FINISHED,
            current_turn_number=9,
            winner_id=1,
            created_at=datetime.now(timezone.utc)
        )
        
        is_valid, status_code, message = validate_game_status_for_move(finished_game, player_id=1)
        assert not is_valid
        assert status_code == 409
        assert message == "Game is not in progress"
        
        # Test case 4: Game not full (less than 2 players)
        in_progress_game_not_full = Game(
            id=3,
            status=GameStatus.IN_PROGRESS,
            current_turn_number=1,
            created_at=datetime.now(timezone.utc)
        )
        in_progress_game_not_full.game_players = [
            GamePlayer(game_id=3, player_id=1, player_order=1, joined_at=datetime.now(timezone.utc))
        ]
        
        is_valid, status_code, message = validate_game_status_for_move(in_progress_game_not_full, player_id=1)
        assert not is_valid
        assert status_code == 409
        assert message == "Game is not full"
        
        # Test case 5: Player not in game
        in_progress_game = Game(
            id=4,
            status=GameStatus.IN_PROGRESS,
            current_turn_number=1,
            created_at=datetime.now(timezone.utc)
        )
        in_progress_game.game_players = [
            GamePlayer(game_id=4, player_id=1, player_order=1, joined_at=datetime.now(timezone.utc)),
            GamePlayer(game_id=4, player_id=2, player_order=2, joined_at=datetime.now(timezone.utc))
        ]
        
        is_valid, status_code, message = validate_game_status_for_move(in_progress_game, player_id=3)
        assert not is_valid
        assert status_code == 403
        assert message == "Player not in game"
        
        # Test case 6: Not player's turn
        # current_turn_number=2 means it's player 2's turn (even number), but we test with player 1
        in_progress_game_wrong_turn = Game(
            id=5,
            status=GameStatus.IN_PROGRESS,
            current_turn_number=2,  # Even number = player 2's turn
            created_at=datetime.now(timezone.utc)
        )
        in_progress_game_wrong_turn.game_players = [
            GamePlayer(game_id=5, player_id=1, player_order=1, joined_at=datetime.now(timezone.utc)),  # Player 1
            GamePlayer(game_id=5, player_id=2, player_order=2, joined_at=datetime.now(timezone.utc))   # Player 2
        ]
        # current_turn_player_id will return player 2 (since turn 2 is even), but we're trying to move as player 1
        
        is_valid, status_code, message = validate_game_status_for_move(in_progress_game_wrong_turn, player_id=1)
        assert not is_valid
        assert status_code == 409
        assert message == "Not your turn"
        
        # Test case 7: Valid move scenario
        # current_turn_number=1 means it's player 1's turn (odd number)
        in_progress_game_valid = Game(
            id=6,
            status=GameStatus.IN_PROGRESS,
            current_turn_number=1,  # Odd number = player 1's turn
            created_at=datetime.now(timezone.utc)
        )
        in_progress_game_valid.game_players = [
            GamePlayer(game_id=6, player_id=1, player_order=1, joined_at=datetime.now(timezone.utc)),  # Player 1
            GamePlayer(game_id=6, player_id=2, player_order=2, joined_at=datetime.now(timezone.utc))   # Player 2
        ]
        # current_turn_player_id will return player 1 (since turn 1 is odd), and we're moving as player 1
        
        is_valid, status_code, message = validate_game_status_for_move(in_progress_game_valid, player_id=1)
        assert is_valid
        assert status_code == 200
        assert message == "Valid game status"