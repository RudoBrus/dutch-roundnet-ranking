import csv
from datetime import datetime
from pathlib import Path
from typing import Literal

from ranking_calculator.config import MAX_COUNTING_TOURNAMENTS, RANKING_RESULT_FOLDER
from ranking_calculator.player import RankedPlayer
from ranking_calculator.ranking_system import RankingSystem
from ranking_calculator.tournament import Tournament


def export_tournament_history(tournament_history: list[Tournament], output_file: Path):
    with output_file.open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Tournament Name",
                "Date",
                "Players",
                "Player multiplier",
                "Age multiplier",
                "Multiplier",
            ]
        )
        for tournament in tournament_history:
            writer.writerow(
                [
                    tournament.name,
                    tournament.date.strftime("%Y-%m-%d"),
                    len(tournament.tournament_results),
                    round(tournament.player_multiplier, 2),
                    tournament.age_multiplier,
                    round(tournament.player_multiplier * tournament.age_multiplier, 2),
                ]
            )


def get_counting_tournaments(player: RankedPlayer) -> list[str]:
    best_tournaments = sorted(
        player.tournament_placements,
        key=lambda placement: placement.points,
        reverse=True,
    )[:MAX_COUNTING_TOURNAMENTS]

    tournament_details = [
        (
            f"{placement.tournament.name} "
            f"{placement.tournament.date.strftime('%Y-%m-%d')} - "
            f"Place: {placement.rank} Points: {round(placement.points, 2)}"
        )
        for placement in best_tournaments
    ]

    while len(tournament_details) < MAX_COUNTING_TOURNAMENTS:
        tournament_details.append("")

    return tournament_details


def export_ranking(players: list[RankedPlayer], output_file: Path):
    sorted_players = sorted(players, key=lambda player: player.rank)
    with output_file.open("w", newline="") as file:
        writer = csv.writer(file)
        header = ["Player Name", "Rank", "Ranking Points"] + [
            f"{ordinal} tournament"
            for ordinal in [
                "Best",
                "Second best",
                "Third best",
                "Fourth best",
                "Fifth best",
            ][:MAX_COUNTING_TOURNAMENTS]
        ]
        writer.writerow(header)
        for player in sorted_players:
            best_tournaments = get_counting_tournaments(player)
            writer.writerow(
                [
                    player.name,
                    player.rank,
                    round(player.ranking_points),
                    *best_tournaments,
                ]
            )


def export(
    ranking_system: RankingSystem,
    category: Literal["women", "advanced", "intermediate", "beginner"],
) -> None:
    current_date = datetime.now().strftime("%Y-%m-%d")
    export_folder = RANKING_RESULT_FOLDER / current_date
    export_folder.mkdir(parents=True, exist_ok=True)

    export_tournament_history(
        ranking_system.tournament_history,
        export_folder / f"{category}_tournament_history.csv",
    )
    export_ranking(
        ranking_system.ranked_players,
        export_folder / f"{category}_ranking.csv",
    )
