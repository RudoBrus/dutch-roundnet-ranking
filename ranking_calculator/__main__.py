import argparse

from ranking_calculator.config import RULES, TOURNAMENT_RECORDS_FOLDER
from ranking_calculator.rnl_ranking_system import RNLRankingSystem


def get_category_entries(selected_category: str) -> list[str]:
    for category_rules in RULES["categories"]:
        if category_rules["category_name"] == selected_category:
            return category_rules["category_entries"]
    raise ValueError(f"Category '{selected_category}' not found in rules.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process tournament rankings by category."
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        required=True,
        help="List of categories to process, possible categories are women, advanced, intermediate and beginner.",
    )
    parser.add_argument(
        "--test",
        type=str,
        default=None,
        help="Optional test name to include in the ranking file name.",
    )
    args = parser.parse_args()
    tournament_paths = sorted(TOURNAMENT_RECORDS_FOLDER.glob("*.csv"))
    for category in args.categories:
        print(f"Processing category: {category}")
        ranking_system = RNLRankingSystem(get_category_entries(category))
        for path in tournament_paths:
            ranking = ranking_system.update_ranking_with_tournament(path)
            print(f"Updated ranking with tournament {path}")
            print(f"Current ranking at {ranking_system.current_date}:")
            print(ranking.head(15))
            print("-" * 100)
        ranking_system.demo_function_print_stats()
        ranking_system.demo_save_ranking_csv(args.test)
