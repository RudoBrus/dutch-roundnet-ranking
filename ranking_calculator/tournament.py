from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from ranking_calculator.config import AGE_MULTIPLIERS


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
    player_multiplier: float | None = None
    age_multiplier: float = 1.0

    def update_age_multiplier(self, calculation_date: datetime):
        age_in_months = int((calculation_date - self.date).days / 30.44)
        self.age_multiplier = AGE_MULTIPLIERS.get(age_in_months, 0)
