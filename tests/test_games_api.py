from fastapi.testclient import TestClient
from tests import utils

class TestCreateGame:
    """Test the POST /games endpoint"""
    
    def test_valid_player_creates_new_game(self, client: TestClient):
        """Test that a valid player can successfully create a new game"""
        player_response = utils.create_player(client)
        assert player_response.status_code == 201
        player_id = player_response.json()["id"]
        
        game_response = utils.create_game(client, player_id)
        
        assert game_response.status_code == 201
        
        game_data = game_response.json()
        assert "id" in game_data
        assert isinstance(game_data["id"], int)
        assert game_data["id"] > 0
        
        assert game_data["status"] == "waiting"
        assert game_data["player1_id"] == player_id
        assert game_data["player2_id"] is None
        assert game_data["current_turn_number"] == 1
        assert game_data["current_turn_player_id"] is None  # No turn until game starts
        assert game_data["winner_id"] is None
        
        assert game_data["grid"] == [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        
        assert "message" in game_data
        expected_message = f"Game created with ID: {game_data['id']} by player {player_id}, waiting for another player to join"
        assert game_data["message"] == expected_message

    def test_player_with_unfinished_game_cannot_create_new_one(self, client: TestClient):
        """Test that a player who already has an unfinished game cannot create a new one"""
        player_response = utils.create_player(client)
        assert player_response.status_code == 201
        player_id = player_response.json()["id"]
        
        first_game_response = utils.create_game(client, player_id)
        assert first_game_response.status_code == 201
        first_game_id = first_game_response.json()["id"]
        
        second_game_response = utils.create_game(client, player_id)
        
        assert second_game_response.status_code == 409  # Conflict
        
        error_data = second_game_response.json()
        assert "detail" in error_data
        expected_error = f"Player already has an unfinished game (ID: {first_game_id}) that is waiting for another player. Complete that game first."
        assert error_data["detail"] == expected_error

    def test_nonexistent_player_cannot_create_game(self, client: TestClient):
        """Test that a nonexistent player cannot create a game"""
        nonexistent_player_id = 99999
        
        response = utils.create_game(client, nonexistent_player_id)
        
        assert response.status_code == 404
        
        error_data = response.json()
        assert "detail" in error_data
        assert error_data["detail"] == "Player not found"

class TestJoinGame:
    """Test the POST /games/{game_id}/join endpoint"""
    
    def test_valid_player_joins_available_game(self, client: TestClient):
        """Test that a second valid player can successfully join an available game"""
        player1_response = utils.create_player(client)
        assert player1_response.status_code == 201
        player1_id = player1_response.json()["id"]
        
        player2_response = utils.create_player(client)
        assert player2_response.status_code == 201
        player2_id = player2_response.json()["id"]
        
        game_response = utils.create_game(client, player1_id)
        assert game_response.status_code == 201
        game_id = game_response.json()["id"]
        
        initial_game = game_response.json()
        assert initial_game["status"] == "waiting"
        assert initial_game["player1_id"] == player1_id
        assert initial_game["player2_id"] is None
        assert initial_game["current_turn_player_id"] is None
        
        join_response = utils.join_game(client, game_id, player2_id)
        
        assert join_response.status_code == 200
        
        joined_game = join_response.json()
        assert joined_game["id"] == game_id
        assert joined_game["status"] == "in_progress"
        assert joined_game["player1_id"] == player1_id
        assert joined_game["player2_id"] == player2_id
        assert joined_game["current_turn_number"] == 1
        assert joined_game["current_turn_player_id"] == player1_id  # Player 1 goes first
        assert joined_game["winner_id"] is None
        
        assert joined_game["grid"] == [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        
        expected_message = f"Player {player2_id} joined game with ID: {game_id}, game is now in progress, waiting for player {player1_id} to make a move"
        assert joined_game["message"] == expected_message

    def test_player_cannot_join_full_or_in_progress_game(self, client: TestClient):
        """Test that a player cannot join a game that is already full or in progress"""
        player1_response = utils.create_player(client)
        player1_id = player1_response.json()["id"]
        
        player2_response = utils.create_player(client)
        player2_id = player2_response.json()["id"]
        
        player3_response = utils.create_player(client)
        player3_id = player3_response.json()["id"]
        
        game_response = utils.create_game(client, player1_id)
        game_id = game_response.json()["id"]
        
        join_response = utils.join_game(client, game_id, player2_id)
        assert join_response.status_code == 200
        
        joined_game = join_response.json()
        assert joined_game["status"] == "in_progress"
        assert joined_game["player1_id"] == player1_id
        assert joined_game["player2_id"] == player2_id
        
        third_join_response = utils.join_game(client, game_id, player3_id)
        
        assert third_join_response.status_code == 409  # Conflict
        
        error_data = third_join_response.json()
        assert "detail" in error_data
        assert error_data["detail"] == "Game already started or finished"

    def test_player_cannot_join_game_they_are_already_in(self, client: TestClient):
        """Test that a player cannot join a game they are already participating in"""
        player1_response = utils.create_player(client)
        player1_id = player1_response.json()["id"]
        
        player2_response = utils.create_player(client)
        player2_id = player2_response.json()["id"]
        
        game_response = utils.create_game(client, player1_id)
        game_id = game_response.json()["id"]
        
        self_join_response = utils.join_game(client, game_id, player1_id)
        
        assert self_join_response.status_code == 409  # Conflict
        
        error_data = self_join_response.json()
        assert "detail" in error_data
        assert error_data["detail"] == "Player already in game"
        
        join_response = utils.join_game(client, game_id, player2_id)
        assert join_response.status_code == 200
        
        joined_game = join_response.json()
        assert joined_game["status"] == "in_progress"
        assert joined_game["player1_id"] == player1_id
        assert joined_game["player2_id"] == player2_id
        
        second_join_response = utils.join_game(client, game_id, player2_id)
        
        assert second_join_response.status_code == 409  # Conflict
        
        error_data = second_join_response.json()
        assert "detail" in error_data
        assert error_data["detail"] == "Player already in game"

    def test_join_nonexistent_game(self, client: TestClient):
        """Test that joining a nonexistent game returns 404"""
        player_response = utils.create_player(client)
        player_id = player_response.json()["id"]
        
        nonexistent_game_id = 99999
        response = utils.join_game(client, nonexistent_game_id, player_id)
        
        assert response.status_code == 404
        error_data = response.json()
        assert error_data["detail"] == "Game not found"

    def test_player_with_unfinished_game_cannot_join_another_game(self, client: TestClient):
        """Test that a player with an unfinished game cannot join another game"""
        player1_response = utils.create_player(client)
        player1_id = player1_response.json()["id"]
        
        player2_response = utils.create_player(client)
        player2_id = player2_response.json()["id"]
        
        player3_response = utils.create_player(client)
        player3_id = player3_response.json()["id"]
        
        game1_response = utils.create_game(client, player1_id)
        game1_id = game1_response.json()["id"]
        
        game2_response = utils.create_game(client, player2_id)
        game2_id = game2_response.json()["id"]
        
        join_response = utils.join_game(client, game1_id, player3_id)
        assert join_response.status_code == 200

        second_join_response = utils.join_game(client, game2_id, player3_id)
        
        assert second_join_response.status_code == 409  # Conflict
        
        error_data = second_join_response.json()
        assert "detail" in error_data
        expected_error = f"Player already has an unfinished game (ID: {game1_id}) that is in progress. Complete that game first."
        assert error_data["detail"] == expected_error


class TestGetGame:
    """Test the GET /games/{game_id} endpoint"""
    
    def test_get_game_success(self, client: TestClient):
        """Test successfully retrieving an existing game"""
        player_response = utils.create_player(client)
        player_id = player_response.json()["id"]
        
        game_response = utils.create_game(client, player_id)
        game_id = game_response.json()["id"]
        
        get_response = utils.get_game(client, game_id)
        
        assert get_response.status_code == 200
        
        get_data = get_response.json()
        create_data = game_response.json()
        
        assert get_data["id"] == create_data["id"]
        assert get_data["status"] == create_data["status"]
        assert get_data["player1_id"] == create_data["player1_id"]
        assert get_data["player2_id"] == create_data["player2_id"]
        assert get_data["grid"] == create_data["grid"]

    def test_get_nonexistent_game(self, client: TestClient):
        """Test getting a game that doesn't exist"""
        nonexistent_game_id = 99999
        
        response = utils.get_game(client, nonexistent_game_id)
        
        assert response.status_code == 404
        error_data = response.json()
        assert error_data["detail"] == "Game not found"

class TestGetAvailableGames:
    """Test the GET /games/available endpoint"""
    
    def test_get_available_games(self, client: TestClient):
        """Test getting all available games"""
        player1_response = utils.create_player(client)
        player1_id = player1_response.json()["id"]
        
        player2_response = utils.create_player(client)
        player2_id = player2_response.json()["id"]
        
        game1_response = utils.create_game(client, player1_id)
        game1_id = game1_response.json()["id"]
        
        game2_response = utils.create_game(client, player2_id)
        game2_id = game2_response.json()["id"]

        response = utils.get_available_games(client)
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["id"] == game1_id
        assert response.json()[1]["id"] == game2_id

class TestMakeMove:
    """Test the POST /games/{game_id}/move endpoint"""
    
    def test_make_move_success(self, client: TestClient):
        """Test making a move in a game"""
        player1_response = utils.create_player(client)
        player1_id = player1_response.json()["id"]
        
        player2_response = utils.create_player(client)
        player2_id = player2_response.json()["id"]
        
        game_response = utils.create_game(client, player1_id)
        game_id = game_response.json()["id"]
        
        join_response = utils.join_game(client, game_id, player2_id)
        assert join_response.status_code == 200
        
        move_response = utils.make_move(client, game_id, player1_id, 0)
        assert move_response.status_code == 200
        
        move_data = move_response.json()
        assert move_data["status"] == "in_progress"
        assert move_data["player1_id"] == player1_id
        assert move_data["player2_id"] == player2_id
        assert move_data["current_turn_number"] == 2
        assert move_data["current_turn_player_id"] == player2_id
        assert move_data["winner_id"] is None
        
        assert move_data["grid"] == [[1, 0, 0], [0, 0, 0], [0, 0, 0]]
        assert move_data["message"] == f"Player {player1_id} made a move at position 0, game is still in progress, waiting for player {player2_id} to make a move"

    def test_make_move_invalid_position(self, client: TestClient):
        """Test making a move in a game with an invalid position"""
        player1_response = utils.create_player(client)
        player1_id = player1_response.json()["id"]
        
        player2_response = utils.create_player(client)
        player2_id = player2_response.json()["id"]
        
        game_response = utils.create_game(client, player1_id)
        game_id = game_response.json()["id"]
        
        join_response = utils.join_game(client, game_id, player2_id)
        assert join_response.status_code == 200
        move_response1 = utils.make_move(client, game_id, player1_id, 0)
        assert move_response1.status_code == 200

        move_response2 = utils.make_move(client, game_id, player2_id, 0)
        assert move_response2.status_code == 409
        error_data = move_response2.json()
        assert "detail" in error_data
        assert error_data["detail"] == "Position already occupied"

    def test_make_move_player_wrong_turn(self, client: TestClient):
        """Test making a move in a game with an wrong turn"""
        player1_response = utils.create_player(client)
        player1_id = player1_response.json()["id"]
        
        player2_response = utils.create_player(client)
        player2_id = player2_response.json()["id"]
        
        game_response = utils.create_game(client, player1_id)
        game_id = game_response.json()["id"]
        
        join_response = utils.join_game(client, game_id, player2_id)
        assert join_response.status_code == 200
        move_response1 = utils.make_move(client, game_id, player1_id, 0)
        assert move_response1.status_code == 200
        move_response2 = utils.make_move(client, game_id, player1_id, 1)
        assert move_response2.status_code == 409
        error_data = move_response2.json()
        assert "detail" in error_data
        assert error_data["detail"] == "Not your turn"

    def test_make_move_player_not_in_game(self, client: TestClient):
        """Test making a move in a game that the player is not in"""
        player1_response = utils.create_player(client)
        player1_id = player1_response.json()["id"]
        
        player2_response = utils.create_player(client)
        player2_id = player2_response.json()["id"]

        player3_response = utils.create_player(client)
        player3_id = player3_response.json()["id"]
        
        game_response = utils.create_game(client, player1_id)
        game_id = game_response.json()["id"]
        
        join_response = utils.join_game(client, game_id, player2_id)
        assert join_response.status_code == 200
        move_response = utils.make_move(client, game_id, player3_id, 0)
        assert move_response.status_code == 403
        error_data = move_response.json()
        assert "detail" in error_data
        assert error_data["detail"] == "Player not in game"
                
    def test_make_move_win_game(self, client: TestClient):
        """Test making a move in a game that wins the game"""
        player1_response = utils.create_player(client)
        player1_id = player1_response.json()["id"]
        
        player2_response = utils.create_player(client)
        player2_id = player2_response.json()["id"]
        
        game_response = utils.create_game(client, player1_id)
        game_id = game_response.json()["id"]
        
        join_response = utils.join_game(client, game_id, player2_id)
        assert join_response.status_code == 200


        move_responses = utils.play_first_player_win_game(client, game_id, player1_id, player2_id)
        for move_response in move_responses:
            assert move_response.status_code == 200

        move_data5 = move_responses[-1].json()
        assert move_data5["status"] == "finished"
        assert move_data5["winner_id"] == player1_id
        assert move_data5["message"] == f"Player {player1_id} made a move at position 2 and won! Game is now finished"
    
    def test_make_move_draw_game(self, client: TestClient):
        """Test making a move in a game that draws the game"""
        player1_response = utils.create_player(client)
        player1_id = player1_response.json()["id"]
        
        player2_response = utils.create_player(client)
        player2_id = player2_response.json()["id"]
        
        game_response = utils.create_game(client, player1_id)
        game_id = game_response.json()["id"]
        
        join_response = utils.join_game(client, game_id, player2_id)
        assert join_response.status_code == 200

        move_responses = utils.play_draw_game(client, game_id, player1_id, player2_id)
        for move_response in move_responses:
            assert move_response.status_code == 200

        move_data9 = move_responses[-1].json()
        assert move_data9["status"] == "finished"
        assert move_data9["winner_id"] is None
        assert move_data9["message"] == f"Player {player1_id} made a move at position 8 and it's a draw! Game is now finished"
