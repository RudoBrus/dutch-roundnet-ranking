from types import Tuple
from datetime import datetime
import numpy as np


N_TOURNAMENTS = 3
from ranking_calculator.settings import AGE_MULTIPLIERS, PLAYER_MULTIPLIERS, POINTS_MAPPING


class RNLPlayer:
    def __init__(self, player_id: str, player_name: str, player_team = None):
        self.player_id = player_id
        self.player_name = player_name

        self.rating = 0.0
        self.player_teams_dict = {}

        if player_team:
            player_team_name, player_team_key = player_team
            self.player_teams_dict[player_team_key] = player_team_name

        self.tournament_participation_history = []
        self.tournament_update = None
        self.rating_composition = []


    def add_tournament_result(self, result):
        tournament_result = {}
        tournament_result["KEY"] = result["tournament_key"]
        tournament_result["DATE"] = result["tournament_date"]
        tournament_result["RANK"] = result["team_rank"]
        tournament_result["POINTS"] = result["team_points"]
        tournament_result["TEAM_KEY"] = result["team_key"]
        tournament_result["TEAM_NAME"] = result["team_name"]

        tournament_result["CUR_POINTS"] = tournament_result["POINTS"]

        self.tournament_participation_history.append(tournament_result)

        if tournament_result["TEAM_KEY"] not in self.player_teams_dict.keys():
            self.player_teams_dict[tournament_result["TEAM_KEY"]] = tournament_result["TEAM_NAME"]
        else:
            # Logging team already in player log.
            pass
    
    @staticmethod
    def get_age_multiplier(tournament_date: str, calculation_date: datetime) -> float:
        tournament_date = datetime.strptime(tournament_date, "%Y-%m-%d")
        age_in_months = (calculation_date - tournament_date).days // 30
        for threshold, age_multiplier in AGE_MULTIPLIERS.items():
            if age_in_months <= threshold:
                return age_multiplier
            ValueError(f"Age multiplier not found for {age_in_months} months")

    def update_current_tournament_scores(self, current_date: datetime):
        for tournament in self.tournament_participation_history:
            original_points = tournament["POINTS"]
            multiplier = RNLPlayer.get_age_multiplier(tournament["DATE"],current_date)

            tournament["CUR_POINTS"] = original_points*multiplier

    def update_player_rating(self):
        self.rating = 0.0

        # Sort tournaments by CUR_POINTS in descending order
        sorted_tournaments = sorted(
            self.tournament_participation_history,
            key=lambda t: t["CUR_POINTS"],
            reverse=True
        )

        # Take the top N tournaments
        top_tournaments = sorted_tournaments[:N_TOURNAMENTS]

        # Calculate total rating from top tournaments
        self.rating = sum(t["CUR_POINTS"] for t in top_tournaments)

        # Store the rating composition
        self.rating_composition = top_tournaments

    def get_player_rating_composition(self):
        return self.player_id, self.rating, self.rating_composition
    
    def save_to_database(self, conn):
        pass

    @staticmethod
    def load_from_database(conn, player_id):
        pass

