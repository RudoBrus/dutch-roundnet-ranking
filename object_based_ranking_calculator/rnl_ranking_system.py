import pandas as pd
import os
from datetime import datetime

from pathlib import Path

from rnl_tournament import RNLTournament
from rnl_player import RNLPlayer

PLAYER_DB = r"../ranking_db/players.db"
TOURNAMENT_RECORDS_FOLDER = r"../ranking_calculator/tournament_data"


class RNLRankingSystem:
    def __init__(self, name : str, start_date : datetime.date, baseranking : pd.DataFrame = None):
        self.name = name
        self.version = 0.1

        self.rankingbook : dict[pd.DataFrame] = {}
        self.tournamentbook : dict[datetime.date] = {}
        self.tournaments : dict[RNLTournament] = {}

        self.player_ids = []
        self.players = set()

        self.add_base_ranking(baseranking=baseranking)

        self.current_date = start_date
        self.current_ranking = pd.DataFrame(columns=["player_id", "player_name", "player_rating"])

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

    def add_base_ranking(self, baseranking : pd.DataFrame = None):
        # temp not operational solution
        if baseranking:
            self.rankingbook["base"] = baseranking
            self.tournamentbook["base"] = start_date - 1
            
            for player in baseranking["player_id"]:
                self.player_ids.append(player)
        pass
    
    def load_tournament_from_file(self, filename):
        # first check the tournament db
        tournament_date = datetime.strptime(
                Path(filename).stem.split("_")[0], "%Y-%m-%d"
            )
        
        # if tournament_date < self.current_date:
        #     print("Cannot calculate tournament for date before last calculation date; reset the ranking if you like to add in this tournamnet")
        #     return
        
        tournament_results = pd.read_csv(filename)
        tournament_key = RNLTournament.build_tournament_key(filename)

        tournament = RNLTournament(tournament_key, tournament_date, tournament_results)

        self.tournamentbook[tournament_key] = tournament_date
        self.tournaments[tournament_key] = tournament

        return tournament_key


    def update_ranking_with_tournament(self, tournament_id):
        tournament = self.tournaments[tournament_id]

        if tournament.tournament_date < self.current_date:
            print("WRONG")

        players = tournament.return_players()
        _, player_ids = self.update_player_base(players)

        self.player_rating_db = [] # load 

        for player_id in player_ids:
            if player_id in self.player_rating_db:
                player_entity = RNLPlayer.load_player(player_id)
            else:
                player_entity = RNLPlayer(player_id, self.playerbase[player_id])
            if player_entity not in self.players:
                self.players.add(player_entity)
        
        self.current_ranking = self.calculate_ranking(tournament.tournament_date)
        tournament.update_tournament_level_multiplier()
        tournament.update_tournament_player_multiplier(self.current_ranking)

        tournament.distribute_points(self.players)



        pass

    def update_player_base(self, players) -> tuple[list, list]:
        # load player base
        # if new player, add, make ID
        # return [(all players ID's), (ids from players in func)]
        self.playerbase = {}
        return [],[]

    def add_new_player(self):
        pass

    def calculate_points(self):
        pass

    def calculate_ranking(self, date:datetime.date):
        pass

if __name__ == "__main__":
    pass

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




