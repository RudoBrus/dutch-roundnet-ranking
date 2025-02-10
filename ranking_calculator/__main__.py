import glob
from datetime import datetime
from pathlib import Path

import pandas as pd

from ranking_calculator.settings import (
    AGE_MULTIPLIERS,
    PLAYER_MULTIPLIERS,
    POINTS_MAPPING,
)

DATA_DIRECTORY = Path(__file__).parent / "tournament_data"


def get_age_multiplier(tournament_date: str) -> float:
    tournament_date = datetime.strptime(tournament_date, "%Y-%m-%d")
    age_in_months = (datetime.now() - tournament_date).days // 30
    for threshold, age_multiplier in AGE_MULTIPLIERS.items():
        if age_in_months <= threshold:
            return age_multiplier
    return 1.0


def calculate_points(
    tournament_results: pd.DataFrame, ranking: pd.DataFrame
) -> pd.Series:
    multiplier = 1
    for player in tournament_results["name"]:
        rank_row = ranking[ranking["name"] == player]
        if not rank_row.empty:
            rank = rank_row["rank"].values[0]
            for threshold, player_multiplier in PLAYER_MULTIPLIERS.items():
                if rank <= threshold:
                    multiplier += player_multiplier
    base_points = tournament_results["rank"].map(POINTS_MAPPING)
    return base_points * multiplier


def add_results_to_ranking(
    tournament_name: str, tournament_results: pd.DataFrame, ranking: pd.DataFrame
) -> pd.DataFrame:
    tournament_results = tournament_results.rename(
        columns={
            "rank": f"{tournament_name}_rank",
            "points": f"{tournament_name}_points",
        }
    )
    tournament_results[f"{tournament_name}_points"] = (
        tournament_results[f"{tournament_name}_points"].round().astype(int)
    )
    if ranking.empty:
        ranking = tournament_results[
            ["name", f"{tournament_name}_rank", f"{tournament_name}_points"]
        ]
    else:
        ranking = pd.merge(
            ranking,
            tournament_results[
                ["name", f"{tournament_name}_rank", f"{tournament_name}_points"]
            ],
            on="name",
            how="outer",
        )
    return ranking


def update_current_standings(ranking: pd.DataFrame) -> pd.DataFrame:
    points_columns = [col for col in ranking.columns if col.endswith("_points")]
    for col in points_columns:
        tournament_date = col.split("_")[0]
        age_multiplier = get_age_multiplier(tournament_date)
        ranking[f"{col}_current"] = ranking[col] * age_multiplier

    ranking["points"] = (
        ranking[[f"{col}_current" for col in points_columns]]
        .apply(lambda row: row.nlargest(3).sum(), axis=1)
        .round()
        .astype(int)
    )
    ranking["rank"] = ranking["points"].rank(method="min", ascending=False).astype(int)
    return ranking


def calculate_ranking():
    tournament_files = sorted(glob.glob((DATA_DIRECTORY / "*.csv").as_posix()))
    categories = ["advanced", "intermediate", "beginner", "women"]

    # Calculate ranking for each category
    for category in categories:
        ranking = pd.DataFrame(columns=["name"])
        for tournament_file in tournament_files:
            tournament_results = pd.read_csv(tournament_file)
            tournament_results = tournament_results[
                tournament_results["category"] == category
            ]
            if not tournament_results.empty:
                ranking = update_current_standings(ranking)
                tournament_results["points"] = calculate_points(
                    tournament_results, ranking
                )
                ranking = add_results_to_ranking(
                    Path(tournament_file).stem, tournament_results, ranking
                )
                ranking = update_current_standings(ranking)

        ranking.sort_values(by="points", ascending=False, inplace=True)
        columns_order = ["name", "rank", "points"] + [
            col for col in ranking.columns if col not in ["name", "rank", "points"]
        ]
        ranking = ranking[columns_order]
        ranking.to_csv(f"../rankings/{category}_ranking.csv", index=False)


if __name__ == "__main__":
    calculate_ranking()
