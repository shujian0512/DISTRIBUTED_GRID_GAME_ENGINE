from fastapi.testclient import TestClient
from tests import utils


class TestLeaderboard:
    """Test the GET /leaderboard endpoint"""
    
    def test_get_leaderboard(self, client: TestClient):
        """Test getting the leaderboard"""
        player1_response = utils.create_player(client)
        player1_id = player1_response.json()["id"]
        
        player2_response = utils.create_player(client)
        player2_id = player2_response.json()["id"]

        player3_response = utils.create_player(client)
        player3_id = player3_response.json()["id"]
        
        game_response1 = utils.create_game(client, player1_id)
        game_id1 = game_response1.json()["id"]
        join_response = utils.join_game(client, game_id1, player2_id)
        assert join_response.status_code == 200

        move_responses = utils.play_first_player_win_game(client, game_id1, player1_id, player2_id)
        for move_response in move_responses:
            assert move_response.status_code == 200

        move_data5 = move_responses[-1].json()
        assert move_data5["status"] == "finished"
        assert move_data5["winner_id"] == player1_id
        assert move_data5["message"] == f"Player {player1_id} made a move at position 2 and won! Game is now finished"

        game_response2 = utils.create_game(client, player3_id)
        game_id2 = game_response2.json()["id"]
        join_response = utils.join_game(client, game_id2, player2_id)
        assert join_response.status_code == 200
        
        move_responses = utils.play_first_player_win_game(client, game_id2, player3_id, player2_id)
        for move_response in move_responses:
            assert move_response.status_code == 200

        move_data5 = move_responses[-1].json()
        assert move_data5["status"] == "finished"
        assert move_data5["winner_id"] == player3_id
        assert move_data5["message"] == f"Player {player3_id} made a move at position 2 and won! Game is now finished"

        game_response3 = utils.create_game(client, player1_id)
        game_id3 = game_response3.json()["id"]
        join_response = utils.join_game(client, game_id3, player2_id)
        assert join_response.status_code == 200
        
        move_responses = utils.play_draw_game(client, game_id3, player1_id, player2_id)
        for move_response in move_responses:
            assert move_response.status_code == 200

        move_data9 = move_responses[-1].json()
        assert move_data9["status"] == "finished"
        assert move_data9["winner_id"] is None
        assert move_data9["message"] == f"Player {player1_id} made a move at position 8 and it's a draw! Game is now finished"

        game_response4 = utils.create_game(client, player2_id)
        game_id4 = game_response4.json()["id"]
        join_response = utils.join_game(client, game_id4, player3_id)
        assert join_response.status_code == 200

        move_responses = utils.play_first_player_win_game(client, game_id4, player2_id, player3_id)
        for move_response in move_responses:
            assert move_response.status_code == 200

        move_data5 = move_responses[-1].json()
        assert move_data5["status"] == "finished"
        assert move_data5["winner_id"] == player2_id
        assert move_data5["message"] == f"Player {player2_id} made a move at position 2 and won! Game is now finished"

        game_response5 = utils.create_game(client, player1_id)
        game_id5 = game_response5.json()["id"]
        join_response = utils.join_game(client, game_id5, player2_id)
        assert join_response.status_code == 200
        
        move_responses = utils.play_first_player_win_game(client, game_id5, player1_id, player2_id)
        for move_response in move_responses:
            assert move_response.status_code == 200

        move_data5 = move_responses[-1].json()
        assert move_data5["status"] == "finished"
        assert move_data5["winner_id"] == player1_id
        assert move_data5["message"] == f"Player {player1_id} made a move at position 2 and won! Game is now finished"

        game_response6 = utils.create_game(client, player3_id)
        game_id6 = game_response6.json()["id"]
        join_response = utils.join_game(client, game_id6, player2_id)
        assert join_response.status_code == 200
        
        move_responses = utils.play_first_player_win_game(client, game_id6, player3_id, player2_id)
        for move_response in move_responses:
            assert move_response.status_code == 200

        move_data5 = move_responses[-1].json()
        assert move_data5["status"] == "finished"
        assert move_data5["winner_id"] == player3_id
        assert move_data5["message"] == f"Player {player3_id} made a move at position 2 and won! Game is now finished"

        game_response7 = utils.create_game(client, player1_id)
        game_id7 = game_response7.json()["id"]
        join_response = utils.join_game(client, game_id7, player3_id)
        assert join_response.status_code == 200
        
        move_responses = utils.play_first_player_win_game(client, game_id7, player1_id, player3_id)
        for move_response in move_responses:
            assert move_response.status_code == 200

        move_data5 = move_responses[-1].json()
        assert move_data5["status"] == "finished"
        assert move_data5["winner_id"] == player1_id
        assert move_data5["message"] == f"Player {player1_id} made a move at position 2 and won! Game is now finished"

        # Get the leaderboard
        win_count_response = utils.get_leaderboard_by_wins(client)
        assert win_count_response.status_code == 200

        win_count_data = win_count_response.json()
        assert win_count_data[0]["player_id"] == player1_id
        assert win_count_data[0]["games_played"] == 4
        assert win_count_data[0]["games_won"] == 3
        assert win_count_data[0]["total_moves"] == 14
        assert win_count_data[0]["win_rate"] == 0.75
        assert win_count_data[0]["efficiency"] == 4.67
        assert win_count_data[0]["rank"] == 1
        
        assert win_count_data[1]["player_id"] == player3_id
        assert win_count_data[1]["games_played"] == 4
        assert win_count_data[1]["games_won"] == 2
        assert win_count_data[1]["total_moves"] == 10
        assert win_count_data[1]["win_rate"] == 0.5
        assert win_count_data[1]["efficiency"] == 5
        assert win_count_data[1]["rank"] == 2
        
        assert win_count_data[2]["player_id"] == player2_id
        assert win_count_data[2]["games_played"] == 6
        assert win_count_data[2]["games_won"] == 1
        assert win_count_data[2]["total_moves"] == 15
        assert win_count_data[2]["win_rate"] == 0.167
        assert win_count_data[2]["efficiency"] == 15
        assert win_count_data[2]["rank"] == 3

        win_rate_response = utils.get_leaderboard_by_win_rate(client)
        assert win_rate_response.status_code == 200

        win_rate_data = win_rate_response.json()
        assert win_rate_data[0]["player_id"] == player1_id
        assert win_rate_data[0]["win_rate"] == 0.75
        assert win_rate_data[0]["rank"] == 1

        assert win_rate_data[1]["player_id"] == player3_id
        assert win_rate_data[1]["win_rate"] == 0.5
        assert win_rate_data[1]["rank"] == 2

        assert win_rate_data[2]["player_id"] == player2_id
        assert win_rate_data[2]["win_rate"] == 0.167
        assert win_rate_data[2]["rank"] == 3

        efficiency_response = utils.get_leaderboard_by_efficiency(client)
        assert efficiency_response.status_code == 200

        efficiency_data = efficiency_response.json()
        assert efficiency_data[0]["player_id"] == player1_id
        assert efficiency_data[0]["efficiency"] == 4.67
        assert efficiency_data[0]["rank"] == 1

        assert efficiency_data[1]["player_id"] == player3_id
        assert efficiency_data[1]["efficiency"] == 5
        assert efficiency_data[1]["rank"] == 2

        assert efficiency_data[2]["player_id"] == player2_id
        assert efficiency_data[2]["efficiency"] == 15
        assert efficiency_data[2]["rank"] == 3