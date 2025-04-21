import pandas as pd
from pathlib import Path
from datetime import datetime
import json
from rnl_tournament import RNLTournament
from rnl_player import RNLPlayer

RULES_PATH = r"dutch-roundnet-ranking/object_based_ranking_calculator/rules.json"
RULES = json.load(open(Path(RULES_PATH).resolve()))


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

    def add_tournament(self, tournament_file : Path, playerbook : dict[str, str]):
        tournament_date, tournament_basename = tournament_file.stem.split("_")
        tournament_date = datetime.strptime(tournament_date, "%Y-%m-%d")
        tournament_key = self.build_tournament_key(tournament_basename, tournament_date)
        
        if tournament_key in self.tournaments:
            print(f"Tournament {tournament_key} already exists")
            return
        
        # TODO: make function to read tournament data
        tournament_data = pd.read_csv(tournament_file)
        category_set = RULES["category_sets"][int(RULES["category_selected"])-1]
        tournament_data = tournament_data[tournament_data["category"].isin(category_set["category_entries"])]
        if len(category_set["category_entries"]) > 1:
            # Get lowest rank from first category (highest ranking number)
            lowest_rank = tournament_data[tournament_data["category"] == category_set["category_entries"][0]]["rank"].max()
            # add this ranking shift to the second category
            tournament_data.loc[tournament_data["category"] == category_set["category_entries"][1], "rank"] += lowest_rank - RULES["ranking_shift"]

        tournament = RNLTournament(tournament_basename, tournament_key, tournament_date, tournament_data, playerbook)
        self.tournaments[tournament_key] = tournament
        return tournament_key

    def calculate_tournament_points(self, tournament_key : str, ranking : pd.DataFrame):
        tournament = self.tournaments[tournament_key]
        tournament.update_tournament_level_multiplier(ranking)
        tournament.calculate_tournament_points()
        return tournament.get_tournament_points()

    @staticmethod
    def get_tournament_player_names(tournament_file : Path):
        tournament_data = pd.read_csv(tournament_file)
        category_set = RULES["category_sets"][int(RULES["category_selected"])-1]
        tournament_data = tournament_data[tournament_data["category"].isin(category_set["category_entries"])]
        return tournament_data["name"].unique()

    @staticmethod
    def build_tournament_key(basename : str, tournament_date : datetime):
        key = tournament_date.strftime("%y%m%d") + basename[0]
        return key
    
    @staticmethod
    def get_tournament_date(tournament_file : Path):
        tournament_date = tournament_file.stem.split("_")[0]
        return datetime.strptime(tournament_date, "%Y-%m-%d")
    
    def get_tournaments(self) -> dict[str, RNLTournament]:
        return self.tournaments

    def get_tournament(self, tournament_key : str) -> RNLTournament:
        return self.tournaments[tournament_key]


