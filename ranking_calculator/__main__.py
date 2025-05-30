import argparse
from datetime import datetime

from ranking_calculator.config import (
    AGE_MULTIPLIERS,
    CATEGORIES,
    TOURNAMENT_DATA_DIRECTORY,
)
from ranking_calculator.export import export
from ranking_calculator.ranking_system import RankingSystem
from ranking_calculator.read_tournament_data import (
    filter_tournaments_by_category,
    get_recent_tournaments,
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process tournament rankings by category."
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        type=str,
        choices=CATEGORIES,
        default=CATEGORIES,
        help="List of categories to process.",
    )
    args = parser.parse_args()

    tournaments = get_recent_tournaments(
        TOURNAMENT_DATA_DIRECTORY,
        datetime.now(),
        max(months for months in AGE_MULTIPLIERS),
    )
    for category in args.categories:
        print(f"Processing category: {category}")
        category_tournaments = filter_tournaments_by_category(tournaments, category)
        ranking_system = RankingSystem()
        for tournament in category_tournaments:
            ranking_system.update_ranking_with_tournament(tournament)
        export(ranking_system, category)
