import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
from config import RANKING_RESULT_FOLDER
from rnl_player import RNLPlayer


class RNLPlayerMgr:
    """
    Manage the players and database in the ranking system
    todo:
    - add db make, save and load
    """

    def __init__(self):
        self.player_db_file = RANKING_RESULT_FOLDER / "players.db"
        self.players: dict[str, RNLPlayer] = {}  # RNLPlayer
        self.playerbook: dict[
            str, str
        ] = {}  # dict containing player_id(key) and player_name(value)

        self.make_player_db()

    def make_player_db(self):
        """
        TODO work this out further later
        save the playerbook to the player_db_file
        """

        if not self.player_db_file.exists():
            self.player_db_file.touch()

        conn = sqlite3.connect(self.player_db_file)
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS players")
        cursor.execute("CREATE TABLE players (player_id TEXT, player_name TEXT)")
        conn.commit()

    @staticmethod
    def load_player_db(ranking_folder: Path) -> "RNLPlayerMgr":
        """
        load the playerbook/players from the player_db_file
        """
        player_mgr = RNLPlayerMgr(ranking_folder)
        return player_mgr

    def get_player_id(self, player_name: str) -> str | None:
        """
        get the player_id of a player and check if the player exists
        """
        if player_name.lower() in self.playerbook.values():
            player_id = list(self.playerbook.keys())[
                list(self.playerbook.values()).index(player_name.lower())
            ]
            return player_id
        return None

    def add_player(self, player_name):
        if self.get_player_id(player_name) is None:
            player_id = str(uuid.uuid4())
            self.playerbook[player_id] = player_name.lower()
            self.players[player_id] = RNLPlayer(player_id, player_name)
        else:
            raise ValueError(f"Player {player_name} already exists")

    def get_player(self, player_id: str) -> RNLPlayer | None:
        """
        get a player from the playerbook
        """
        if player_id in self.players:
            return self.players[player_id]
        return None

    def get_player_book(self) -> dict[str, str]:
        """
        get the playerbook, a dict containing player_id(key) and player_name(value)
        """
        return self.playerbook

    def add_tournament_points_to_players(
        self,
        tournament_points: dict[str, tuple[int, float]],
        tournament_date: datetime,
        tournament_key: str,
    ):
        """
        add points to the players
        """
        for player_id, points in tournament_points.items():
            tournament_result = {}
            tournament_result["tournament_key"] = tournament_key
            tournament_result["tournament_date"] = tournament_date
            tournament_result["team_rank"] = points[0]
            tournament_result["team_points"] = points[1]
            tournament_result["team_key"] = None
            tournament_result["team_name"] = None
            self.players[player_id].add_tournament_result(tournament_result)

    def update_players(self, current_date: datetime):
        """
        update the players
        """
        for player_id in self.players:
            self.players[player_id].update(current_date)

    def get_player_results(self) -> pd.DataFrame:
        """
        get the player ratings and composition
        """

        results = []
        for player_id in self.players:
            results.append(
                self.players[player_id].get_player_rating_composition(include_name=True)
            )

        return pd.DataFrame(
            results,
            columns=["player_id", "player_name", "rating", "rating_composition"],
        )
