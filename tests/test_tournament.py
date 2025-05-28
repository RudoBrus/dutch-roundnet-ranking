from datetime import datetime

from ranking_calculator.read_tournament_data import load_relevant_tournaments


def test_read_relevant_tournaments(tmp_path):
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

    tournaments = load_relevant_tournaments(
        tmp_path, current_date, maximum_age_in_months
    )

    assert len(tournaments) == 2
    assert tournaments[0].name == "Tournament2"
    assert tournaments[1].name == "Tournament3"
    assert tournaments[0].date < tournaments[1].date
