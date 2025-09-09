"""
API tests for players endpoints
"""
from fastapi.testclient import TestClient
from tests import utils


class TestCreatePlayer:
    """Test the POST /players endpoint"""
    
    def test_create_player_success(self, client: TestClient):
        """Test successful player creation"""
        response = utils.create_player(client)
        
        assert response.status_code == 201
        
        data = response.json()
        assert "id" in data
        assert isinstance(data["id"], int)
        assert data["id"] > 0
        assert data["games_played"] == 0
        assert data["games_won"] == 0
        assert "message" in data
        assert f"Player created with ID: {data['id']}" in data["message"]
    
    def test_create_multiple_players(self, client: TestClient):
        """Test creating multiple players generates unique IDs"""
        # Create first player
        response1 = utils.create_player(client)
        assert response1.status_code == 201
        player1_id = response1.json()["id"]
        
        # Create second player
        response2 = utils.create_player(client)
        assert response2.status_code == 201
        player2_id = response2.json()["id"]
        
        # Ensure IDs are unique
        assert player1_id != player2_id
        assert player2_id == player1_id + 1  # Sequential IDs


class TestGetPlayer:
    """Test the GET /players/{player_id} endpoint"""
    
    def test_get_player_success(self, client: TestClient):
        """Test successfully retrieving an existing player"""
        # First create a player
        create_response = utils.create_player(client)
        assert create_response.status_code == 201
        player_id = create_response.json()["id"]
        
        # Get the player
        response = utils.get_player(client, player_id)
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == player_id
        assert data["games_played"] == 0
        assert data["games_won"] == 0
        assert "message" in data
        assert f"Player with ID: {player_id} found" in data["message"]
    
    def test_get_player_not_found(self, client: TestClient):
        """Test getting a non-existent player returns 404"""
        non_existent_id = 99999
        response = utils.get_player(client, non_existent_id)
        
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Player not found"