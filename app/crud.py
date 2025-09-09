from sqlmodel import Session, select
from .models import Player, Game, GamePlayer, Move, GameStatus


def create_player(session: Session) -> Player:
    player = Player()
    session.add(player)
    session.commit()
    session.refresh(player)
    return player


def get_player(session: Session, player_id: int) -> Player | None:
    return session.get(Player, player_id)


def get_player_unfinished_game(session: Session, player_id: int) -> Game | None:
    return session.exec(
        select(Game)
        .join(GamePlayer)
        .where(GamePlayer.player_id == player_id)
        .where(Game.status != GameStatus.FINISHED)
    ).first()


def create_game(session: Session, player_id: int) -> Game:
    new_game = Game(status=GameStatus.WAITING)
    session.add(new_game)
    session.flush()  # Get game ID

    assert new_game.id is not None
    game_player = GamePlayer(game_id=new_game.id, player_id=player_id, player_order=1)
    session.add(game_player)
    session.commit()
    session.refresh(new_game)
    return new_game


def get_game(session: Session, game_id: int) -> Game | None:
    return session.get(Game, game_id)


def join_game(session: Session, game_id: int, player_id: int) -> Game:
    game_player = GamePlayer(game_id=game_id, player_id=player_id, player_order=2)
    session.add(game_player)

    # Start the game after joining
    game = session.get(Game, game_id)
    if game:
        game.status = GameStatus.IN_PROGRESS

    session.commit()
    if game:
        session.refresh(game)
    assert game is not None
    return game

def get_available_games(session: Session) -> list[Game]:
    return list(session.exec(
        select(Game).where(Game.status == GameStatus.WAITING)
    ).all())


def get_moves_for_game(session: Session, game_id: int) -> list[Move]:
    return list(session.exec(
        select(Move)
        .where(Move.game_id == game_id)
        .order_by("move_number")
    ).all())


def create_move(
    session: Session, game_id: int, player_id: int, position: int, move_number: int
) -> Move:
    move = Move(
        game_id=game_id, player_id=player_id, position=position, move_number=move_number
    )
    session.add(move)
    session.commit()
    session.refresh(move)
    return move


def get_players_with_wins(session: Session) -> list[Player]:
    return list(session.exec(
        select(Player).where(Player.games_won > 0)
    ).all())