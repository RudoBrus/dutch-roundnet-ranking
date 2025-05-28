from datetime import datetime
from unittest.mock import Mock

from ranking_calculator.player import Player
from ranking_calculator.ranking_system import RankingSystem
from ranking_calculator.tournament import Tournament, TournamentResult


def test_ranking_system_initialization():
    ranking_system = RankingSystem()
    assert len(ranking_system.players) == 0
    assert len(ranking_system.tournament_history) == 0
    assert len(ranking_system.ranking_history) == 0


def test_ranked_players():
    ranking_system = RankingSystem()

    tournament_results = [
        TournamentResult(player_name="Player1", rank=1, category="advanced"),
        TournamentResult(player_name="Player2", rank=2, category="advanced"),
    ]
    tournament = Tournament(
        name="Tournament1",
        date=datetime(2023, 1, 1),
        tournament_results=tournament_results,
        player_multiplier=1.5,
        age_multiplier=1.0,
    )

    ranking_system.players = [
        Player(name="Player1", tournament_placements=[], ranking_points=100),
        Player(name="Player2", tournament_placements=[], ranking_points=50),
    ]

    ranked_players = ranking_system.ranked_players
    assert len(ranked_players) == 2
    assert ranked_players[0].name == "Player1"
    assert ranked_players[0].rank == 1
    assert ranked_players[1].name == "Player2"
    assert ranked_players[1].rank == 2


def test_add_tournament():
    ranking_system = RankingSystem()
    ranking_system.update_age_multipliers = Mock()
    ranking_system.calculate_tournament_player_multiplier = Mock(return_value=1.0)
    ranking_system.add_player_tournament_placements = Mock()
    tournament = Tournament(
        name="Tournament1",
        date=datetime(2023, 1, 1),
        tournament_results=[
            TournamentResult("Player1", 1, "advanced"),
            TournamentResult("Player2", 2, "beginner"),
        ],
    )

    ranking_system.add_tournament(tournament)
    ranking_system.update_age_multipliers.assert_called_once_with(tournament.date)
    ranking_system.calculate_tournament_player_multiplier.assert_called_once_with(
        tournament
    )
    ranking_system.add_player_tournament_placements.assert_called_once_with(tournament)
    assert tournament.date in ranking_system.ranking_history


def test_calculate_tournament_player_multiplier():
    ranking_system = RankingSystem()

    tournament = Tournament(
        name="Tournament1",
        date=datetime(2023, 1, 1),
        tournament_results=[
            TournamentResult("Player1", 1, "advanced"),
            TournamentResult("Player2", 2, "beginner"),
        ],
    )

    ranking_system.add_tournament(tournament)

    multiplier = ranking_system.calculate_tournament_player_multiplier(tournament)
    assert multiplier > 1.0  # Depends on PLAYER_MULTIPLIERS configuration


def test_update_age_multipliers():
    ranking_system = RankingSystem()

    tournament = Tournament(
        name="Tournament1",
        date=datetime(2020, 1, 1),
        tournament_results=[
            TournamentResult("Player1", 1, "advanced"),
        ],
    )

    ranking_system.add_tournament(tournament)
    ranking_system.update_age_multipliers(datetime(2023, 1, 1))

    assert tournament.age_multiplier < 1.0  # Assuming age affects multiplier
