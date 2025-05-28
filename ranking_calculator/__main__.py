import argparse
from datetime import datetime

from ranking_calculator.config import (
    AGE_MULTIPLIERS,
    RANKING_RESULT_FOLDER,
    TOURNAMENT_DATA_DIRECTORY,
)
from ranking_calculator.export import export_ranking, export_tournament_history
from ranking_calculator.ranking_system import RankingSystem
from ranking_calculator.read_tournament_data import (
    filter_tournaments_by_category,
    load_relevant_tournaments,
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process tournament rankings by category."
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        type=str,
        choices=["women", "advanced", "intermediate", "beginner"],
        default=["women", "advanced", "intermediate", "beginner"],
        help="List of categories to process. Possible categories are: women, advanced, intermediate, beginner.",
    )
    args = parser.parse_args()

    tournaments = load_relevant_tournaments(
        TOURNAMENT_DATA_DIRECTORY,
        datetime.now(),
        max(months for months in AGE_MULTIPLIERS),
    )
    for category in args.categories:
        print(f"Processing category: {category}")
        category_tournaments = filter_tournaments_by_category(tournaments, category)
        ranking_system = RankingSystem()
        for tournament in category_tournaments:
            ranking_system.add_tournament(tournament)
        export_tournament_history(
            category,
            ranking_system.tournament_history,
            RANKING_RESULT_FOLDER / f"{category}_tournament_history.csv",
        )
        export_ranking(
            ranking_system.players, RANKING_RESULT_FOLDER / f"{category}_ranking.csv"
        )
