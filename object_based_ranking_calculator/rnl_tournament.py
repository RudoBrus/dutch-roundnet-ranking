import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path

RULES_PATH = r"dutch-roundnet-ranking/object_based_ranking_calculator/rules.json"
RULES = json.load(open(Path(RULES_PATH).resolve()))

class RNLTournament:
    def __init__(self, tournament_name : str, tournament_key : str, tournament_date: datetime, tournament_data:pd.DataFrame, playerbook : dict[str, str]):
        self.tournament_name = tournament_name
        self.tournament_key = tournament_key
        self.tournament_date = tournament_date
        self.tournament_data = tournament_data

        reverse_playerbook = {v: k for k, v in playerbook.items()}     
        self.tournament_data["player_id"] = self.tournament_data["name"].map(reverse_playerbook)
        
        if self.tournament_data["player_id"].isna().any():
            missing_players = self.tournament_data[self.tournament_data["player_id"].isna()]["name"].tolist()
            raise ValueError(f"Players not found in playerbook: {', '.join(missing_players)}")

        self.tournament_data["blank_points"] = self.tournament_data["rank"].map(RULES["blank_points"])

        self.level_multiplier = 1.0
        
        pass
  
    def update_tournament_level_multiplier(self, ranking: pd.DataFrame):
        print("not implemented, skipping")
        # raise NotImplementedError("Tournament level multiplier not implemented")
        # calculate based on input ranking the multiplier of the tournament
        # so every player in the tournament within a certain tier adds to the tournament multiplier

#         def calculate_points(
#     tournament_results: pd.DataFrame, ranking: pd.DataFrame
# ) -> pd.Series:
#     multiplier = 1.0
#     for player in tournament_results["name"]:
#         rank_row = ranking[ranking["name"] == player]
#         if not rank_row.empty:
#             rank = rank_row["rank"].values[0]
#             for threshold, player_multiplier in PLAYER_MULTIPLIERS.items():
#                 if rank <= threshold:
#                     multiplier += player_multiplier
#     base_points = tournament_results["rank"].map(POINTS_MAPPING)
#     return base_points * multiplier

        self.level_multiplier = 1.0
        pass

    def calculate_tournament_points(self):
        # calculate the points for the tournament 
        self.tournament_data["tournament_points"] = self.tournament_data["blank_points"] * self.level_multiplier

    def get_tournament_points(self):
        return dict(zip(self.tournament_data["player_id"], [self.tournament_data["rank"], self.tournament_data["tournament_points"]]))
    


