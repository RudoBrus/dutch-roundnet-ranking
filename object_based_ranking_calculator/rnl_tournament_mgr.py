import pandas as pd
from pathlib import Path
from datetime import datetime

from rnl_tournament import RNLTournament

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
    def __init__(self, ranking_folder : Path):
        self.ranking_folder = ranking_folder
        self.tournament_db_file = self.ranking_folder / "tournaments.db"

        self.tournaments : dict[str, RNLTournament] = {}

        pass

    def add_tournament(self, tournament_file : Path):
        tournament_date, tournament_basename = tournament_file.stem.split("_")
        tournament_key = self.build_tournament_key(tournament_basename, tournament_date)

        tournament_data = pd.read_csv(tournament_file)

        tournament = RNLTournament(tournament_basename, tournament_key, tournament_date, tournament_data)
        self.tournaments[tournament_key] = tournament


    def calculate_tournament_points(self, tournament_key : str, ranking : pd.DataFrame):
        tournament = self.tournaments[tournament_key]
        tournament.update_tournament_level_multiplier(ranking)
        tournament.calculate_tournament_points()
        return tournament.get_tournament_points()

    @staticmethod
    def build_tournament_key(basename : str, tournament_date : datetime.date):
        key = tournament_date.strftime("%y%m%d") + basename[0]
        return key
    


