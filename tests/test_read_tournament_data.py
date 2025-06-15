from datetime import datetime
from pathlib import Path

from ranking_calculator.read_tournament_data import (
    filter_tournaments_by_category,
    get_recent_tournaments,
    read_tournament_file,
)
from ranking_calculator.tournament import Tournament, TournamentResult


def test_read_tournament_file(tmp_path: Path) -> None:
    tournament_file = tmp_path / "2023-01-01_Test.csv"
    with tournament_file.open("w") as f:
        f.write("player_name,rank,category\n")
        f.write("Player1,1,advanced\n")
        f.write("Player2,2,beginner\n")

    tournament = read_tournament_file(tournament_file)

    assert tournament.name == "Test"
    assert tournament.date == datetime(2023, 1, 1)
    assert len(tournament.tournament_results) == 2
    assert tournament.tournament_results[0].player_name == "Player1"
    assert tournament.tournament_results[0].rank == 1
    assert tournament.tournament_results[0].category == "advanced"
    assert tournament.tournament_results[1].player_name == "Player2"
    assert tournament.tournament_results[1].rank == 2
    assert tournament.tournament_results[1].category == "beginner"


def test_get_recent_tournaments(tmp_path: Path) -> None:
    tournament_1 = tmp_path / "2020-01-01_Tournament1.csv"
    tournament_2 = tmp_path / "2022-01-01_Tournament2.csv"
    tournament_3 = tmp_path / "2023-01-01_Tournament3.csv"
    for tournament_file in [tournament_1, tournament_2, tournament_3]:
        with tournament_file.open("w") as f:
            f.write("player_name,rank,category\n")
            f.write("Player1,1,advanced\n")
            f.write("Player2,2,advanced\n")
    current_date = datetime(2024, 1, 1)
    maximum_age_in_months = 24

    tournaments = get_recent_tournaments(tmp_path, current_date, maximum_age_in_months)

    assert len(tournaments) == 2
    assert tournaments[0].name == "Tournament2"
    assert tournaments[1].name == "Tournament3"
    assert tournaments[0].date < tournaments[1].date


def test_filter_tournaments_by_category() -> None:
    tournaments = [
        Tournament(
            name="Tournament1",
            date=datetime(2023, 1, 1),
            tournament_results=[
                TournamentResult("Player1", 1, "advanced"),
                TournamentResult("Player2", 2, "beginner"),
                TournamentResult("Player3", 3, "advanced"),
            ],
        ),
        Tournament(
            name="Tournament2",
            date=datetime(2023, 2, 1),
            tournament_results=[
                TournamentResult("Player3", 3, "women"),
                TournamentResult("Player4", 4, "advanced"),
            ],
        ),
    ]

    filtered_tournaments = filter_tournaments_by_category(tournaments, "advanced")
    assert len(filtered_tournaments) == 2
    assert filtered_tournaments[0].name == "Tournament1"
    assert len(filtered_tournaments[0].tournament_results) == 2
    assert filtered_tournaments[0].tournament_results[0].player_name == "Player1"
    assert filtered_tournaments[0].tournament_results[1].player_name == "Player3"
    assert filtered_tournaments[1].name == "Tournament2"
    assert len(filtered_tournaments[1].tournament_results) == 1
    assert filtered_tournaments[1].tournament_results[0].player_name == "Player4"

    filtered_tournaments = filter_tournaments_by_category(tournaments, "women")
    assert len(filtered_tournaments) == 1
    assert filtered_tournaments[0].name == "Tournament2"
    assert len(filtered_tournaments[0].tournament_results) == 1
    assert filtered_tournaments[0].tournament_results[0].player_name == "Player3"
