from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from ranking_calculator.config import AGE_MULTIPLIERS, TOURNAMENT_BASE_POINTS


@dataclass(frozen=True)
class TournamentResult:
    player_name: str
    rank: int
    category: Literal["women", "advanced", "intermediate", "beginner"]


@dataclass
class Tournament:
    name: str
    date: datetime
    tournament_results: list[TournamentResult]
    player_multiplier: float = 1.0
    age_multiplier: float = 1.0

    @property
    def id(self) -> str:
        return f"{self.name}_{self.date.strftime('%Y-%m-%d')}"

    def update_age_multiplier(self, calculation_date: datetime) -> None:
        age_in_months = int((calculation_date - self.date).days / 30.44)
        self.age_multiplier = AGE_MULTIPLIERS.get(age_in_months, 0)

    def get_points(self, rank: int) -> float:
        base_points = TOURNAMENT_BASE_POINTS.get(rank, 0)
        return base_points * self.player_multiplier * self.age_multiplier
