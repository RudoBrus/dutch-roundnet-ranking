import csv
from datetime import datetime
from pathlib import Path
from typing import Literal

from ranking_calculator.tournament import Tournament, TournamentResult


def capitalize_name(name: str) -> str:
    parts = name.split()
    if len(parts) > 1:
        return f"{' '.join(parts[:-1]).capitalize()} {parts[-1].capitalize()}"
    return name.capitalize()


def clean_name(name: str) -> str:
    capitalized_name = capitalize_name(name)
    # For people that can't spell their own names correctly
    name_corrections = {
        "Dirk van der Riet": "Dirk van de Riet",
        "Jary Koijman": "Jary Kooijman",
        "Maikel Schills": "Maikel Schils",
        "B Houweling": "Bram Houweling",
    }
    return name_corrections.get(capitalized_name, capitalized_name)


def read_tournament_file(tournament_file_path: Path) -> Tournament:
    tournament_results = []
    with tournament_file_path.open("r") as file:
        reader = csv.reader(file)
        next(reader)
        for name, rank, category in reader:
            if category not in ["women", "advanced", "intermediate", "beginner"]:
                raise ValueError(f"Invalid category: {category}")
            cleaned_name = clean_name(name)
            tournament_results.append(
                TournamentResult(cleaned_name, int(rank), category)  # type: ignore[arg-type]
            )

    tournament_date_str, tournament_name = tournament_file_path.stem.split("_")
    tournament_date = datetime.strptime(tournament_date_str, "%Y-%m-%d")
    return Tournament(tournament_name, tournament_date, tournament_results)


def get_recent_tournaments(
    tournament_record_folder: Path,
    current_date: datetime,
    maximum_age_in_months: int,
) -> list[Tournament]:
    tournaments = []
    tournament_paths = tournament_record_folder.glob("*.csv")
    for path in tournament_paths:
        tournament = read_tournament_file(path)
        age_in_months = (current_date - tournament.date).days / 30.44
        if age_in_months <= maximum_age_in_months:
            tournaments.append(read_tournament_file(path))
    return sorted(tournaments, key=lambda t: t.date)


def filter_tournaments_by_category(
    tournaments: list[Tournament],
    category: Literal["women", "advanced", "intermediate", "beginner"],
) -> list[Tournament]:
    filtered_tournaments = []
    for tournament in tournaments:
        filtered_results = [
            result
            for result in tournament.tournament_results
            if result.category == category
        ]
        if filtered_results:
            filtered_tournament = Tournament(
                name=tournament.name,
                date=tournament.date,
                tournament_results=filtered_results,
                player_multiplier=tournament.player_multiplier,
                age_multiplier=tournament.age_multiplier,
            )
            filtered_tournaments.append(filtered_tournament)
    return filtered_tournaments
