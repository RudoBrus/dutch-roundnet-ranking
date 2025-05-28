import copy
from datetime import datetime

from ranking_calculator.config import PLAYER_MULTIPLIERS
from ranking_calculator.player import Player, RankedPlayer, TournamentPlacements
from ranking_calculator.tournament import Tournament


class RankingSystem:
    def __init__(self):
        self.players: list[Player] = []
        self.tournament_history: list[Tournament] = []
        self.ranking_history: dict[datetime, list[RankedPlayer]] = {}

    @property
    def ranked_players(self) -> list[RankedPlayer]:
        sorted_players = sorted(
            self.players, key=lambda player: player.ranking_points, reverse=True
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

    def get_or_create_player(self, player_name: str) -> Player:
        player = next((p for p in self.players if p.name == player_name), None)
        if player is None:
            player = Player(name=player_name, tournament_placements=[])
            self.players.append(player)
        return player

    def add_player_tournament_placements(self, tournament: Tournament):
        for result in tournament.tournament_results:
            player = self.get_or_create_player(result.player_name)
            player.tournament_placements.append(
                TournamentPlacements(tournament=tournament, rank=result.rank)
            )

    def add_tournament(self, tournament: Tournament):
        # First we update the ranking with the new age multipliers
        self.update_age_multipliers(tournament.date)
        # Then we calculate the player multiplier for the tournament
        tournament.player_multiplier = self.calculate_tournament_player_multiplier(
            tournament
        )
        # Then we update the player's placements with the tournament results
        self.add_player_tournament_placements(tournament)
        self.tournament_history.append(tournament)
        # Finally, we store the ranking history
        self.ranking_history[tournament.date] = copy.deepcopy(self.ranked_players)
