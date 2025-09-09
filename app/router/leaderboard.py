from fastapi import APIRouter
from ..database import SessionDep
from ..schemas import PlayerStats
from .. import crud

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

@router.get("/wins", response_model=list[PlayerStats])
def get_leaderboard_by_wins(session: SessionDep):
    """
    Get top 3 players by count of games won.
    Only includes players who have won at least 1 game.
    """
    player_stats_list = get_player_stats_list(session)
    
    top_players_by_wins = sorted(player_stats_list, key=lambda p: p.games_won, reverse=True)[:3]
    
    # Add rank to each player
    for rank, player in enumerate(top_players_by_wins, 1):
        player.rank = rank
    
    return top_players_by_wins

@router.get("/efficiency", response_model=list[PlayerStats])
def get_leaderboard_by_efficiency(session: SessionDep):
    """
    Get top 3 players by efficiency (average moves per win).
    Only includes players who have won at least 1 game.
    """
    player_stats_list = get_player_stats_list(session)
    
    top_players_by_efficiency = sorted(player_stats_list, key=lambda p: p.efficiency)[:3]
    
    # Add rank to each player
    for rank, player in enumerate(top_players_by_efficiency, 1):
        player.rank = rank
    
    return top_players_by_efficiency

@router.get("/win_rate", response_model=list[PlayerStats])
def get_leaderboard_by_win_rate(session: SessionDep):
    """
    Get top 3 players by win rate (percentage of games won).
    Only includes players who have played at least 1 game.
    """
    player_stats_list = get_player_stats_list(session)
    
    top_players_by_win_rate = sorted(player_stats_list, key=lambda p: p.win_rate, reverse=True)[:3]
    
    # Add rank to each player
    for rank, player in enumerate(top_players_by_win_rate, 1):
        player.rank = rank
    
    return top_players_by_win_rate

def get_player_stats_list(session: SessionDep) -> list[PlayerStats]:
    """
    Helper function to get all player statistics as PlayerStats objects.
    """
    players_with_wins = crud.get_players_with_wins(session)
    player_stats_list = []
    
    for player in players_with_wins:
        win_rate = round(player.games_won / player.games_played, 3) if player.games_played > 0 else 0.0
        efficiency = round(player.total_moves / player.games_won, 2) if player.games_won > 0 else 999999.0
        
        if player.id is None:
            continue
            
        player_stats = PlayerStats(
            player_id=player.id,
            games_played=player.games_played,
            games_won=player.games_won,
            total_moves=player.total_moves,
            win_rate=win_rate,
            efficiency=efficiency
        )
        player_stats_list.append(player_stats)
    
    return player_stats_list
