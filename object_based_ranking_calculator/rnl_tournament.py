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
        self.tournament_data["player_id"] = self.tournament_data["name"].str.lower().map(reverse_playerbook)
        
        if self.tournament_data["player_id"].isna().any():
            missing_players = self.tournament_data[self.tournament_data["player_id"].isna()]["name"].tolist()
            raise ValueError(f"Players not found in playerbook: {', '.join(missing_players)}")

        self.map_tournament_points()
        self.level_multiplier = 1.0
        
        pass

    def map_tournament_points(self):
        blank_points = {int(k): v for k, v in RULES["blank_points"].items()}
        self.tournament_data["blank_points"] = self.tournament_data["rank"].map(blank_points)
  
    def update_tournament_level_multiplier(self, ranking: pd.DataFrame):
        self.level_multiplier = 1.0
        for index, row in self.tournament_data.iterrows():
            player_id = row["player_id"]
            if player_id in ranking["player_id"].values:
                player_rank = ranking[ranking["player_id"] == player_id].index[0] + 1
                for threshold, multiplier in RULES["player_multipliers"].items():
                    if player_rank <= int(threshold):
                        self.level_multiplier += multiplier
                        break
            else:
                continue

        return self.level_multiplier

    def calculate_tournament_points(self):
        # calculate the points for the tournament 
        self.tournament_data["tournament_points"] = self.tournament_data["blank_points"] * self.level_multiplier

    def get_tournament_points(self):
        return dict(zip(self.tournament_data["player_id"], zip(self.tournament_data["rank"], self.tournament_data["tournament_points"])))
    


