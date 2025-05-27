from datetime import datetime
from pathlib import Path

import pandas as pd
from config import RANKING_RESULT_FOLDER
from rnl_player_mgr import RNLPlayerMgr
from rnl_tournament_mgr import RNLTournamentMgr


def get_tournament_date(tournament_file: Path):
    tournament_date = tournament_file.stem.split("_")[0]
    return datetime.strptime(tournament_date, "%Y-%m-%d")


class RNLRankingSystem:
    """
    Represents a ranking system in the RNL ranking system.
    todo:
    - add db make, save and load
    - add ranking save and load
    - add calculate ranking
    """

    def __init__(self, categories_entries: list[str]):
        self.category = categories_entries[0]
        self.rankingbook: dict[datetime, pd.DataFrame] = {}
        self.current_ranking = pd.DataFrame(
            columns=[
                "player_id",
                "player_name",
                "player_rating",
                "player_ranking_composition",
            ]
        )
        self.current_date: datetime | None = None
        self.player_mgr = RNLPlayerMgr()
        self.tournament_mgr = RNLTournamentMgr(categories_entries)

    def update_ranking_with_tournament(self, tournament_file: Path):
        self.current_date = get_tournament_date(tournament_file)
        self.current_ranking = self.calculate_ranking(self.current_date)

        # TODO: figure out where to update the date. Right now something goes wrong here.

        # add players to player_mgr
        tournament_player_names = self.tournament_mgr.get_tournament_player_names(
            tournament_file
        )
        for player_name in tournament_player_names:
            if self.player_mgr.get_player_id(player_name) is None:
                self.player_mgr.add_player(player_name)

        # add tournament to tournament_mgr
        playerbook = self.player_mgr.get_player_book()
        tournament_key = self.tournament_mgr.add_tournament(tournament_file, playerbook)
        # calculate points
        points = self.tournament_mgr.calculate_tournament_points(
            tournament_key, self.current_ranking[self.current_ranking["rating"] > 0]
        )
        # add points to players
        self.player_mgr.add_tournament_points_to_players(
            points, self.current_date, tournament_key
        )
        self.player_mgr.update_players(self.current_date)

        # save ranking
        self.rankingbook[self.current_date] = self.current_ranking
        new_ranking = self.calculate_ranking(self.current_date)
        self.current_ranking = new_ranking

        return new_ranking

    def calculate_ranking(self, date: datetime):
        self.player_mgr.update_players(date)
        standings = (
            self.player_mgr.get_player_results()
        )  # df with playername, id, rating and ranking composition
        ranking = standings.sort_values(by="rating", ascending=False)
        ranking = ranking.reset_index(drop=True)
        return ranking

    def demo_function_print_stats(self, mode: str = "tournament"):
        if mode == "tournament":
            for key, tournament in self.tournament_mgr.get_tournaments().items():
                print(f"Tournament {key}:", end="\t")
                print(f"{tournament.level_multiplier:.2f}", end="\t")
                print(f"{len(tournament.tournament_data)} players")

    def demo_save_ranking_csv(self, test_name: str | None = None):
        filename = (
            f"{self.category}_{test_name}.csv" if test_name else f"{self.category}.csv"
        )
        self.current_ranking.to_csv(RANKING_RESULT_FOLDER / filename, index=False)
