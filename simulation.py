import asyncio
import httpx

BASE_URL = "http://127.0.0.1:8000"
NUM_PLAYERS = 10
CONCURRENT_GAMES = 5 # Number of games to run at the same time

def get_winning_moves(player1_id: int, player2_id: int) -> list[tuple[int, int]]:
    return [
        (player1_id, 0),
        (player2_id, 6),
        (player1_id, 1),
        (player2_id, 7),
        (player1_id, 2),  
    ]

def get_draw_moves(player1_id: int, player2_id: int) -> list[tuple[int, int]]:
    return [
        (player1_id, 1),
        (player2_id, 0),
        (player1_id, 3),
        (player2_id, 2),
        (player1_id, 4),
        (player2_id, 5),
        (player1_id, 6),
        (player2_id, 7),
        (player1_id, 8),
    ]

async def play_winning_game(player1_id: int, player2_id: int):
    """Simulates a game where player1 wins using predefined moves."""
    async with httpx.AsyncClient() as client:
        try:
            print(f"INFO: Starting WINNING game between Player {player1_id} and Player {player2_id}...")
            
            # Create game
            response = await client.post(f"{BASE_URL}/games", json={"player_id": player1_id})
            response.raise_for_status()
            game = response.json()
            game_id = game["id"]
            print(f"Game {game_id}: Player {player1_id} created the game.")

            # Join game
            response = await client.post(f"{BASE_URL}/games/{game_id}/join", json={"player_id": player2_id})
            response.raise_for_status()
            print(f"Game {game_id}: Player {player2_id} joined.")

            # Play predefined winning moves
            moves = get_winning_moves(player1_id, player2_id)
            for i, (player_id, position) in enumerate(moves):
                print(f"Game {game_id}: Move {i+1} - Player {player_id} moves to position {position}")
                move_payload = {"player_id": player_id, "position": position}
                response = await client.post(f"{BASE_URL}/games/{game_id}/move", json=move_payload)
                response.raise_for_status()
                
                # Check if game is finished
                game_state = response.json()
                if game_state["status"] == "finished":
                    winner = game_state.get("winner_id")
                    if winner:
                        print(f"Game {game_id}: Finished! Player {winner} won.")
                    else:
                        print(f"Game {game_id}: Finished! It's a draw.")
                    break
                
                await asyncio.sleep(0.1)

        except httpx.HTTPStatusError as e:
            print(f"ERROR in winning game between {player1_id} and {player2_id}: {e.response.text}")
        except Exception as e:
            print(f"An unexpected ERROR occurred in winning game: {e}")

async def play_draw_game(player1_id: int, player2_id: int):
    """Simulates a game that ends in a draw using predefined moves."""
    async with httpx.AsyncClient() as client:
        try:
            print(f"INFO: Starting DRAW game between Player {player1_id} and Player {player2_id}...")
            
            # Create game
            response = await client.post(f"{BASE_URL}/games", json={"player_id": player1_id})
            response.raise_for_status()
            game = response.json()
            game_id = game["id"]
            print(f"Game {game_id}: Player {player1_id} created the game.")

            # Join game
            response = await client.post(f"{BASE_URL}/games/{game_id}/join", json={"player_id": player2_id})
            response.raise_for_status()
            print(f"Game {game_id}: Player {player2_id} joined.")

            # Play predefined draw moves
            moves = get_draw_moves(player1_id, player2_id)
            for i, (player_id, position) in enumerate(moves):
                print(f"Game {game_id}: Move {i+1} - Player {player_id} moves to position {position}")
                move_payload = {"player_id": player_id, "position": position}
                response = await client.post(f"{BASE_URL}/games/{game_id}/move", json=move_payload)
                response.raise_for_status()
                
                # Check if game is finished
                game_state = response.json()
                if game_state["status"] == "finished":
                    winner = game_state.get("winner_id")
                    if winner:
                        print(f"Game {game_id}: Finished! Player {winner} won.")
                    else:
                        print(f"Game {game_id}: Finished! It's a draw.")
                    break
                
                await asyncio.sleep(0.1)

        except httpx.HTTPStatusError as e:
            print(f"ERROR in draw game between {player1_id} and {player2_id}: {e.response.text}")
        except Exception as e:
            print(f"An unexpected ERROR occurred in draw game: {e}")

async def main():
    """Main function to set up and run the simulation."""
    player_ids = []
    print(f"--- Creating {NUM_PLAYERS} players ---")
    async with httpx.AsyncClient() as client:
        # Create players sequentially to ensure they exist before games start
        for _ in range(NUM_PLAYERS):
            try:
                response = await client.post(f"{BASE_URL}/players")
                if response.status_code == 201:
                    player_ids.append(response.json()["id"])
            except Exception as e:
                print(f"Could not create player: {e}")
    
    if len(player_ids) < 2:
        print("Not enough players created to start games. Exiting.")
        return
        
    print(f"Players created: {player_ids}")

    print("--- Running Tournament Simulation ---")
    
    # Create a list of tasks with four rounds of games
    round1_game_tasks = []
    round2_game_tasks = []
    round3_game_tasks = []
    round4_game_tasks = []
    round5_game_tasks = []
    # Round 1: All players play, players 1,2,3,4,5 will win
    print(f"Round 1: All {CONCURRENT_GAMES} pairs play - Players 1,2,3,4,5 will win")
    for i in range(CONCURRENT_GAMES):
        p1, p2 = player_ids[i], player_ids[i + CONCURRENT_GAMES]
        task = play_winning_game(p1, p2)
        round1_game_tasks.append(task)

    # Round 2: Players 1,2,3,6,7,8 play, players 1,2,3 will win
    print("Round 2: 3 pairs play - Players 1,2,3 will win")
    for i in range(3):
        p1, p2 = player_ids[i], player_ids[i + CONCURRENT_GAMES]
        task = play_winning_game(p1, p2)
        round2_game_tasks.append(task)
    
    # Round 3: Players 1,2,7,8 play, players 1,2 will win
    print("Round 3: 2 pairs play - Players 1,2 will win")
    for i in range(2):
        p1, p2 = player_ids[i], player_ids[i + CONCURRENT_GAMES]
        task = play_winning_game(p1, p2)
        round3_game_tasks.append(task)

    # Round 4: All players play, every game is a draw
    print(f"Round 4: All {CONCURRENT_GAMES} pairs play - All games will be draws")
    for i in range(CONCURRENT_GAMES):
        p1, p2 = player_ids[i], player_ids[i + CONCURRENT_GAMES]
        task = play_draw_game(p1, p2)
        round4_game_tasks.append(task)

    # Round 5: Players 1, 6 play, player 1 will win
    print("Round 5: 1 pair play - Player 1 will win")
    p1, p2 = player_ids[0], player_ids[6]
    task = play_winning_game(p1, p2)
    round5_game_tasks.append(task)

    # Run all game tasks concurrently
    print("Executing Round 1...")
    await asyncio.gather(*round1_game_tasks)
    print("Round 1 completed!")
    
    print("Executing Round 2...")
    await asyncio.gather(*round2_game_tasks)
    print("Round 2 completed!")
    
    print("Executing Round 3...")
    await asyncio.gather(*round3_game_tasks)
    print("Round 3 completed!")
    
    print("Executing Round 4...")
    await asyncio.gather(*round4_game_tasks)
    print("Round 4 completed!")

    print("Executing Round 5...")
    await asyncio.gather(*round5_game_tasks)
    print("Round 5 completed!")

    print("\n--- Simulation Finished. Calling Leaderboard APIs ---")
    async with httpx.AsyncClient() as client:
        leaderboards = {}
        
        response = await client.get(f"{BASE_URL}/leaderboard/wins")
        if response.status_code == 200:
            leaderboards["wins"] = response.json()
            print("Successfully fetched wins leaderboard")
        else:
            print(f"✗ Failed to fetch wins leaderboard: {response.status_code}")
            leaderboards["wins"] = []

        response = await client.get(f"{BASE_URL}/leaderboard/win_rate")
        if response.status_code == 200:
            leaderboards["win_rate"] = response.json()
            print("Successfully fetched win rate leaderboard")
        else:
            print(f"✗ Failed to fetch win rate leaderboard: {response.status_code}")
            leaderboards["win_rate"] = []

        response = await client.get(f"{BASE_URL}/leaderboard/efficiency")
        if response.status_code == 200:
            leaderboards["efficiency"] = response.json()
            print("Successfully fetched efficiency leaderboard")
        else:
            print(f"Failed to fetch efficiency leaderboard: {response.status_code}")
            leaderboards["efficiency"] = []

    # Display formatted results
    print("\n" + "="*80)
    print("LEADERBOARD RESULTS")
    print("="*80)
    
    # Display wins leaderboard
    print("---  Top Players by Wins ---")
    if leaderboards["wins"]:
        for player in leaderboards["wins"]:
            print(
                f"#{player.get('rank', 'N/A')}: Player {player['player_id']} | "
                f"Wins: {player['games_won']} | "
                f"Games Played: {player['games_played']} | "
                f"Win Rate: {player['win_rate']:.1%} | "
                f"Efficiency: {player['efficiency']:.2f} moves/win"
            )
    else:
        print("No players with wins found")
    
    # Display win rate leaderboard
    print("---  Top Players by Win Rate ---")
    if leaderboards["win_rate"]:
        for player in leaderboards["win_rate"]:
            print(
                f"#{player.get('rank', 'N/A')}: Player {player['player_id']} | "
                f"Win Rate: {player['win_rate']:.1%} | "
                f"Wins: {player['games_won']} | "
                f"Games Played: {player['games_played']} | "
                f"Efficiency: {player['efficiency']:.2f} moves/win"
            )
    else:
        print("No players found")
    
    # Display efficiency leaderboard
    print("---  Top Players by Efficiency (Lower is Better) ---")
    if leaderboards["efficiency"]:
        for player in leaderboards["efficiency"]:
            print(
                f"#{player.get('rank', 'N/A')}: Player {player['player_id']} | "
                f"Efficiency: {player['efficiency']:.2f} moves/win | "
                f"Wins: {player['games_won']} | "
                f"Total Moves: {player['total_moves']} | "
                f"Win Rate: {player['win_rate']:.1%}"
            )
    else:
        print("No players with wins found for efficiency calculation")
    
    print("="*80)
    print("Simulation Finished. Leaderboard APIs called.")
    

if __name__ == "__main__":
    asyncio.run(main())