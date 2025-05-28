from datetime import datetime
from pathlib import Path

import pandas as pd

from ranking_calculator.config import RANKING_RESULT_FOLDER
from ranking_calculator.rnl_tournament import RNLTournament


class RNLTournamentMgr:
    """
    This class manages the tournaments and calculates the points for each tournament.
    todo:
    - add tournament to the database
    - calculate tournament points
    - update ranking
    - save tournaments to the database
    - load tournaments from the database

    """

    def __init__(self, categories: list[str]):
        self.categories = categories
        self.tournament_db_file = RANKING_RESULT_FOLDER / "tournaments.db"
        self.tournaments: dict[str, RNLTournament] = {}

    def add_tournament(self, tournament_file: Path, playerbook: dict[str, str]):
        tournament_date, tournament_basename = tournament_file.stem.split("_")
        tournament_date = datetime.strptime(tournament_date, "%Y-%m-%d")
        tournament_key = self.build_tournament_key(tournament_basename, tournament_date)

        if tournament_key in self.tournaments:
            print(f"Tournament {tournament_key} already exists")
            return None

        # TODO: make function to read tournament data
        tournament_data = pd.read_csv(tournament_file)
        tournament_data = tournament_data[
            tournament_data["category"].isin(self.categories)
        ]
        if len(self.categories) > 1:
            # Get lowest rank from the first category (highest ranking number)
            lowest_rank = tournament_data.loc[
                tournament_data["category"] == self.categories[0], "rank"
            ].max()
            # Add this ranking shift to the second category
            tournament_data.loc[
                tournament_data["category"] == self.categories[1], "rank"
            ] += lowest_rank

        tournament = RNLTournament(
            tournament_basename,
            tournament_key,
            tournament_date,
            tournament_data,
            playerbook,
        )
        self.tournaments[tournament_key] = tournament
        return tournament_key

    def calculate_tournament_points(self, tournament_key: str, ranking: pd.DataFrame):
        tournament = self.tournaments[tournament_key]
        tournament.update_tournament_level_multiplier(ranking)
        tournament.calculate_tournament_points()
        return tournament.get_tournament_points()

    def get_tournament_player_names(self, tournament_file: Path):
        tournament_data = pd.read_csv(tournament_file)
        tournament_data = tournament_data[
            tournament_data["category"].isin(self.categories)
        ]
        return tournament_data["name"].unique()

    @staticmethod
    def build_tournament_key(basename: str, tournament_date: datetime):
        key = tournament_date.strftime("%y%m%d") + basename[0]
        return key

    def get_tournaments(self) -> dict[str, RNLTournament]:
        return self.tournaments
