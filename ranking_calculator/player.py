from dataclasses import dataclass

from ranking_calculator.config import MAX_COUNTING_TOURNAMENTS
from ranking_calculator.tournament import Tournament


@dataclass
class TournamentPlacements:
    tournament: Tournament
    rank: int

    @property
    def points(self) -> float:
        return self.tournament.get_points(self.rank)


@dataclass
class Player:
    name: str
    tournament_placements: list[TournamentPlacements]

    @property
    def ranking_points(self) -> float:
        return sum(
            sorted(
                (placement.points for placement in self.tournament_placements),
                reverse=True,
            )[:MAX_COUNTING_TOURNAMENTS]
        )


@dataclass
class RankedPlayer(Player):
    rank: int


class PlayerList:
    def __init__(self) -> None:
        self.players: list[Player] = []

    def get_or_create_player(self, player_name: str) -> Player:
        player = next((p for p in self.players if p.name == player_name), None)
        if player is None:
            player = Player(name=player_name, tournament_placements=[])
            self.players.append(player)
        return player

    def update_playerlist_from_tournament(self, tournament: Tournament):
        for result in tournament.tournament_results:
            player = self.get_or_create_player(result.player_name)
            player.tournament_placements.append(
                TournamentPlacements(tournament=tournament, rank=result.rank)
            )
