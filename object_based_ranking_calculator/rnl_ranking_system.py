import pandas as pd

PLAYER_DB = r"../ranking_db/players.db"
TOURNAMENT_RECORDS_FOLDER = r"../ranking_calculator/tournament_data"


class RNLRankingSystem:
    def __init__(self):
        self.version = 0.1
        self.ranking = pd.DataFrame()
        self.tournaments = []
        self.players = []
    

    def update_ranking(self, tournament_id):
        pass

    def calculate_points(self):
        pass

    def update_ranking(self):
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




