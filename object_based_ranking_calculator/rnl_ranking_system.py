import pandas as pd
import os
from datetime import datetime, date
import json
from pathlib import Path
from tkinter import filedialog

from rnl_tournament import RNLTournament
from rnl_player import RNLPlayer
from rnl_tournament_mgr import RNLTournamentMgr
from rnl_player_mgr import RNLPlayerMgr

PLAYER_DB = r"../ranking_db/players.db"
TOURNAMENT_RECORDS_FOLDER = r"../ranking_calculator/tournament_data"
RULES_PATH = r"dutch-roundnet-ranking/object_based_ranking_calculator/rules.json"
RULES = json.load(open(Path(RULES_PATH).resolve()))

class RNLRankingSystem:
    """
    Represents a ranking system in the RNL ranking system.
    todo:
    - add db make, save and load
    - add ranking save and load
    - add calculate ranking
    """
    def __init__(self, name : str, start_date : datetime, debug : bool = True):
        # first check if a ranking system with this name exists
        if Path(f"../rankings/{name}").exists() and not debug:
            raise ValueError(f"Ranking system with name {name} already exists")

        self.name = name
        self.version = 0.1

        self.rankingbook : dict[datetime, pd.DataFrame] = {}   

        self.current_date : datetime = start_date

        # lets start building the setup
        self.current_ranking = pd.DataFrame(columns=["player_id", "player_name", "player_rating", "player_ranking_composition"])
        # lets make a folder for this specific ranking system
        self.ranking_folder = Path(f"../rankings/{self.name}")
        self.ranking_folder.mkdir(parents=True, exist_ok=True)

        self.player_mgr = RNLPlayerMgr(self.ranking_folder)
        self.tournament_mgr = RNLTournamentMgr(self.ranking_folder) 

    @staticmethod
    def load_ranking(self, name: str):
        pass

    def save_ranking(self):
        # save ranking
        # save tournaments
        # save player db
        # save player id
        # save ranking.json

        # all in subfolder rankings/self.name
        pass
  
    # def load_tournament_from_file(self, filename):
    #     # first check the tournament db
    #     tournament_date = datetime.strptime(
    #             Path(filename).stem.split("_")[0], "%Y-%m-%d"
    #         )
        
    #     # if tournament_date < self.current_date:
    #     #     print("Cannot calculate tournament for date before last calculation date; reset the ranking if you like to add in this tournamnet")
    #     #     return
        
    #     tournament_results = pd.read_csv(filename)
    #     tournament_key = RNLTournament.build_tournament_key(filename)

    #     tournament = RNLTournament(tournament_key, tournament_date, tournament_results)

    #     self.tournamentbook[tournament_key] = tournament_date
    #     self.tournaments[tournament_key] = tournament

    #     return tournament_key


    def update_ranking_with_tournament(self, path_to_tournament_file : Path = None):
        # if no path is provided, open window to select file
        if path_to_tournament_file is None:
            path_to_tournament_file = Path(filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")]))
        
        # first calculate the ranking on tournament day:
        self.current_date = RNLTournamentMgr.get_tournament_date(path_to_tournament_file)
        self.current_ranking = self.calculate_ranking(self.current_date)

        # TODO: figure out where to update the date. Right now something goes wrong here.

        # add players to player_mgr
        tournament_player_names = RNLTournamentMgr.get_tournament_player_names(path_to_tournament_file)
        for player_name in tournament_player_names:
            if self.player_mgr.get_player_id(player_name) is None:
                self.player_mgr.add_player(player_name)
        
        # add tournament to tournament_mgr
        playerbook = self.player_mgr.get_player_book()
        tournament_key = self.tournament_mgr.add_tournament(path_to_tournament_file, playerbook)
        # calculate points
        points = self.tournament_mgr.calculate_tournament_points(tournament_key, self.current_ranking[self.current_ranking["rating"] > 0])
        # add points to players
        self.player_mgr.add_tournament_points_to_players(points, self.current_date, tournament_key)
        self.player_mgr.update_players(self.current_date)

        # save ranking
        self.rankingbook[self.current_date] = self.current_ranking
        new_ranking = self.calculate_ranking(self.current_date)
        self.current_ranking = new_ranking

        return new_ranking

    def calculate_ranking(self, date:datetime):
        self.player_mgr.update_players(date)
        standings = self.player_mgr.get_player_results() # df with playername, id, rating and ranking composition

        ranking = standings.sort_values(by="rating", ascending=False)
        ranking = ranking.reset_index(drop=True)
        # self.current_ranking = ranking

        return ranking
        
        # # For now throw exception
        # raise NotImplementedError("Ranking calculation not implemented")
    
    def demo_function_print_stats(self, mode : str = "tournament"):
        if mode == "tournament":
            for key, tournament in self.tournament_mgr.get_tournaments().items():
                print(f"Tournament {key}:", end="\t")
                print(f"{tournament.level_multiplier:.2f}", end="\t")
                print(f"{len(tournament.tournament_data)} players")

    def demo_save_ranking_csv(self):
        filename = f"{self.current_date.strftime('%Y%m%d')}_{self.name}_{self.version}_{RULES['category_selected']}.csv"
        self.current_ranking.to_csv(self.ranking_folder / filename, index=False)

if __name__ == "__main__":
    # test the ranking system
    paths = [p for p in Path(r"D:\STZN\Files\Roundnet\RoundnetNL\DutchRoundnetRanking\dutch-roundnet-ranking\ranking_calculator\tournament_data").glob("*.csv")]
    ranking_system = RNLRankingSystem(f"test{datetime.now().strftime('%Y%m%d#%H%M%S')}", datetime(2023, 1, 1))
    try:
        for path in paths: 
            ranking = ranking_system.update_ranking_with_tournament(Path(path))
            print(f"Updated ranking with tournament {path}")
            print(f"Current ranking at {ranking_system.current_date}:")
            print(ranking.head(15))
            print("-"*100)
        # print(ranking_system.current_ranking)
    except KeyboardInterrupt:
        pass

    ranking_system.demo_function_print_stats()
    ranking_system.demo_save_ranking_csv()
    # print("hold")

# Initialize ranking, 
# load in a player base file (matching player id's and names) (starting empty)
# load in a tournament result (starting earliest)
# based on the date of the tournament -> update players ratings and tournament results, update ranking.
# first for every tournament; assign id;s to new players
# then build the object for every player in the ranking
# fetch current ranking and assign tournament participation multiplier
# for every player, add tournament results
# for every player, calculate current rating
# save every player in DB
# save ranking after tournament in DB

# once we are up and running:
# load in player base;
# load in tournament result;
# -> add all new players
# fetch last ranking -> calculate todays ranking
# -> determine tournament participation multiplier
# assign new points to all participating players

# update ranking after tournament in DB




