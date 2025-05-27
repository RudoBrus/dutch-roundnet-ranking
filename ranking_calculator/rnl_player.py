# from types import Tuple
from datetime import datetime

from config import RULES


class RNLPlayer:
    """
    Represents a player in the RNL ranking system.
    todo:
    - add db save and load
    """

    def __init__(
        self,
        player_id: str,
        player_name: str,
        player_team: tuple[str, str] | None = None,
    ):
        self.player_id: str = player_id
        self.player_name: str = player_name.lower()

        self.rating: float = 0.0
        self.player_teams_dict: dict[str, str] = {}

        if player_team:
            player_team_name, player_team_key = player_team
            self.player_teams_dict[player_team_key] = player_team_name

        self.tournament_participation_history: list[dict[str, str | int]] = []
        self.date_of_last_update: datetime | None = None
        self.rating_composition: list[dict[str, str | int]] = []

    def add_tournament_result(self, result: dict[str, str | int]):
        tournament_result = {}
        tournament_result["KEY"]: str = result["tournament_key"]
        tournament_result["DATE"]: datetime = result["tournament_date"]
        tournament_result["RANK"]: int = result["team_rank"]
        tournament_result["POINTS"]: int = result["team_points"]
        tournament_result["TEAM_KEY"]: str = (
            result["team_key"] if result["team_key"] else None
        )
        tournament_result["TEAM_NAME"]: str = (
            result["team_name"] if result["team_name"] else None
        )

        tournament_result["CUR_POINTS"]: int = tournament_result["POINTS"]
        tournament_result["AGE_MULTIPLIER"]: float = 1.0

        self.tournament_participation_history.append(tournament_result)

        if tournament_result["TEAM_KEY"] not in self.player_teams_dict.keys():
            self.player_teams_dict[tournament_result["TEAM_KEY"]] = tournament_result[
                "TEAM_NAME"
            ]
        else:
            # Logging team already in player log.
            pass

    @staticmethod
    def get_age_multiplier(
        tournament_date: datetime, calculation_date: datetime
    ) -> float:
        age_in_months = (calculation_date - tournament_date).days // 30
        for threshold, age_multiplier in RULES["age_multipliers"].items():
            if age_in_months <= int(threshold):
                return age_multiplier
        raise ValueError(f"Age multiplier not found for {age_in_months} months")

    def update(self, current_date: datetime):
        self.update_current_tournament_scores(current_date)
        self.update_player_rating()

    def update_current_tournament_scores(self, current_date: datetime):
        for tournament in self.tournament_participation_history:
            tournament["AGE_MULTIPLIER"]: float = RNLPlayer.get_age_multiplier(
                tournament["DATE"], current_date
            )
            tournament["CUR_POINTS"]: int = (
                tournament["POINTS"] * tournament["AGE_MULTIPLIER"]
            )

        self.date_of_last_update: datetime = current_date

    def update_player_rating(self):
        self.rating = 0.0

        # Sort tournaments by CUR_POINTS in descending order
        sorted_tournaments = sorted(
            self.tournament_participation_history,
            key=lambda t: t["CUR_POINTS"],
            reverse=True,
        )

        # Take the top N tournaments
        top_tournaments = sorted_tournaments[
            : RULES["number_of_tournaments_in_ranking_composition"]
        ]

        # Calculate total rating from top tournaments
        self.rating = round(sum(t["CUR_POINTS"] for t in top_tournaments), 1)

        # Store the rating composition
        self.rating_composition = [
            {
                # "NAME" : t["NAME"],
                "KEY": t["KEY"],
                "DATE": t["DATE"].strftime("%Y-%m-%d"),
                "RANK": t["RANK"],
                "POINTS": round(t["CUR_POINTS"], 1),
                "AGE_MULTIPLIER": t["AGE_MULTIPLIER"],
            }
            for t in top_tournaments
        ]

    def get_player_rating_composition(self, include_name: bool = False):
        if include_name:
            return (
                self.player_id,
                self.player_name,
                self.rating,
                self.rating_composition,
            )
        return self.player_id, self.rating, self.rating_composition

    def save_to_database(self, conn):
        pass

    @staticmethod
    def load_from_database(conn, player_id):
        pass
