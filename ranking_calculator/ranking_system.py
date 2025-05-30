import copy
from datetime import datetime

from ranking_calculator.config import PLAYER_MULTIPLIERS
from ranking_calculator.player import PlayerList, RankedPlayer
from ranking_calculator.tournament import Tournament


class RankingSystem:
    def __init__(self) -> None:
        self.player_list: PlayerList = PlayerList()
        self.tournament_history: list[Tournament] = []
        self.ranking_history: dict[datetime, list[RankedPlayer]] = {}

    @property
    def ranked_players(self) -> list[RankedPlayer]:
        sorted_players = sorted(
            self.player_list.players,
            key=lambda player: player.ranking_points,
            reverse=True,
        )
        return [
            RankedPlayer(
                name=player.name,
                tournament_placements=player.tournament_placements,
                rank=index + 1,
            )
            for index, player in enumerate(sorted_players)
        ]

    def update_age_multipliers(self, calculation_date: datetime) -> None:
        for tournament in self.tournament_history:
            tournament.update_age_multiplier(calculation_date)

    def calculate_tournament_player_multiplier(self, tournament: Tournament) -> float:
        ranked_players = {player.name: player.rank for player in self.ranked_players}
        multiplier = 1.0
        for result in tournament.tournament_results:
            player_rank = ranked_players.get(result.player_name)
            if player_rank:
                multiplier += PLAYER_MULTIPLIERS.get(player_rank, 0.0)
        return multiplier

    def update_ranking_with_tournament(self, tournament: Tournament):
        # First we update the tournament's age multiplier
        self.update_age_multipliers(tournament.date)
        # Then we calculate the player multiplier for the tournament
        tournament.player_multiplier = self.calculate_tournament_player_multiplier(
            tournament
        )
        # Then we update the player's placements with the tournament results
        self.player_list.update_playerlist_from_tournament(tournament)
        # Finally, we store the ranking history
        self.tournament_history.append(tournament)
        self.ranking_history[tournament.date] = copy.deepcopy(self.ranked_players)
