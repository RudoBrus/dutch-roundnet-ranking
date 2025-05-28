from dataclasses import dataclass

from ranking_calculator.config import MAX_COUNTING_TOURNAMENTS, TOURNAMENT_BASE_POINTS
from ranking_calculator.tournament import Tournament


@dataclass
class TournamentPlacements:
    tournament: Tournament
    rank: int

    @property
    def points(self) -> float:
        base_points = TOURNAMENT_BASE_POINTS.get(self.rank, 0)
        return (
            base_points
            * self.tournament.player_multiplier
            * self.tournament.age_multiplier
        )


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
