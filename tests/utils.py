"""
Utility functions for test helpers
"""
from fastapi.testclient import TestClient
from httpx import Response


def create_player(client: TestClient) -> Response:
    response = client.post("/players")
    return response

def get_player(client: TestClient, player_id: int) -> Response:
    response = client.get(f"/players/{player_id}")
    return response

def create_game(client: TestClient, player_id: int) -> Response:
    response = client.post("/games", json={"player_id": player_id})
    return response


def join_game(client: TestClient, game_id: int, player_id: int) -> Response:
    response = client.post(f"/games/{game_id}/join", json={"player_id": player_id})
    return response

def get_game(client: TestClient, game_id: int) -> Response:
    response = client.get(f"/games/{game_id}")
    return response

def get_available_games(client: TestClient) -> Response:
    response = client.get("/games/available")
    return response

def make_move(client: TestClient, game_id: int, player_id: int, position: int) -> Response:
    response = client.post(f"/games/{game_id}/move", json={
        "player_id": player_id,
        "position": position
    })
    return response


def play_moves_sequence(client: TestClient, game_id: int, moves: list[tuple[int, int]]) -> list[Response]:
    """
    Play a sequence of moves in a game.
        
    Example:
        moves = [(player1_id, 0), (player2_id, 1), (player1_id, 2)]
    """
    move_results = []
    
    for player_id, position in moves:
        game_data = make_move(client, game_id, player_id, position)
        move_results.append(game_data)
    
    return move_results

def play_first_player_win_game(client: TestClient, game_id: int, player1_id: int, player2_id: int) -> list[Response]:
    moves = [(player1_id, 0), (player2_id, 6), (player1_id, 1), (player2_id, 7), (player1_id, 2)]
    return play_moves_sequence(client, game_id, moves)

def play_draw_game(client: TestClient, game_id: int, player1_id: int, player2_id: int) -> list[Response]:
    moves = [(player1_id, 1), (player2_id, 0), (player1_id, 3), (player2_id, 2), (player1_id, 4), (player2_id, 5), (player1_id, 6), (player2_id, 7), (player1_id, 8)]
    return play_moves_sequence(client, game_id, moves)

def get_leaderboard_by_wins(client: TestClient) -> Response:
    response = client.get("/leaderboard/wins")
    return response

def get_leaderboard_by_win_rate(client: TestClient) -> Response:
    response = client.get("/leaderboard/win_rate")
    return response

def get_leaderboard_by_efficiency(client: TestClient) -> Response:
    response = client.get("/leaderboard/efficiency")
    return response