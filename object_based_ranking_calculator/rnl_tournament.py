import pandas as pd
import numpy as np

class RNLTournament:
    def __init__(self, tournament_key : str, tournament_data:pd.DataFrame):
        self.tournament_key = tournament_key
        self.tournament_data = tournament_data

        # test function, and potentially do a lot of validation beforehand, so I do not need to do a lot of checks here.
        self.players = np.concatenate(self.tournament_data["player1"].to_numpy().T,self.tournament_data["player2"].to_numpy().T)

        self.level_multiplier = 1.0
        self.player_multiplier = 1.0 # count players in tournament_data
        
        pass

    def update_tournament_level_multiplier(self, ranking):
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

    def get_multipliers(self):
        return self.level_multiplier, self.player_multiplier

