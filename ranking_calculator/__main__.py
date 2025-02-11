import glob
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from settings import AGE_MULTIPLIERS, PLAYER_MULTIPLIERS, POINTS_MAPPING

DATA_DIRECTORY = Path(__file__).parent / "tournament_data"


def calculate_points(
    tournament_results: pd.DataFrame, ranking: pd.DataFrame
) -> pd.Series:
    multiplier = 1.0
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
    tournament_results[f"{tournament_name}_points"] = tournament_results[
        f"{tournament_name}_points"
    ]
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


def get_age_multiplier(tournament_date: str, calculation_date: datetime) -> float:
    tournament_date = datetime.strptime(tournament_date, "%Y-%m-%d")
    age_in_months = (calculation_date - tournament_date).days // 30
    for threshold, age_multiplier in AGE_MULTIPLIERS.items():
        if age_in_months <= threshold:
            return age_multiplier
        ValueError(f"Age multiplier not found for {age_in_months} months")


def update_current_standings(
    ranking: pd.DataFrame, calculation_date: datetime
) -> pd.DataFrame:
    points_columns = [col for col in ranking.columns if col.endswith("_points")]
    for col in points_columns:
        tournament_date = col.split("_")[0]
        age_multiplier = get_age_multiplier(tournament_date, calculation_date)
        ranking[f"{col}_current"] = ranking[col] * age_multiplier

    top_results = ranking[[f"{col}_current" for col in points_columns]].apply(
        lambda row: row.nlargest(3).values, axis=1
    )
    ranking["Best result 1"] = top_results.apply(lambda x: x[0] if len(x) > 0 else 0)
    ranking["Best result 2"] = top_results.apply(lambda x: x[1] if len(x) > 1 else 0)
    ranking["Best result 3"] = top_results.apply(lambda x: x[2] if len(x) > 2 else 0)
    ranking["points"] = top_results.apply(lambda x: np.nansum(x))

    ranking["rank"] = ranking["points"].rank(method="min", ascending=False)
    return ranking


def calculate_ranking(calculation_date: datetime = datetime.now()):
    tournament_files = sorted(glob.glob((DATA_DIRECTORY / "*.csv").as_posix()))
    categories = ["advanced", "intermediate", "beginner", "women"]

    # Calculate ranking for each category
    for category in categories:
        ranking = pd.DataFrame(columns=["name"])
        for tournament_file in tournament_files:
            tournament_date = datetime.strptime(
                Path(tournament_file).stem.split("_")[0], "%Y-%m-%d"
            )
            if tournament_date <= calculation_date:
                tournament_results = pd.read_csv(tournament_file)
                tournament_results = tournament_results[
                    tournament_results["category"] == category
                ]
                if not tournament_results.empty:
                    # First update the standings based on the time of the now played tournament
                    ranking = update_current_standings(ranking, calculation_date)
                    tournament_results["points"] = calculate_points(
                        tournament_results, ranking
                    )
                    ranking = add_results_to_ranking(
                        Path(tournament_file).stem, tournament_results, ranking
                    )
                    # Update the standings with the newly added points
                    ranking = update_current_standings(ranking, calculation_date)

        ranking.sort_values(by="points", ascending=False, inplace=True)
        first_columns = [
            "name",
            "rank",
            "points",
            "Best result 1",
            "Best result 2",
            "Best result 3",
        ]
        columns_order = first_columns + [
            col for col in ranking.columns if col not in first_columns
        ]
        ranking = ranking[columns_order]
        ranking.to_csv(
            f"../rankings/{category}_ranking_{calculation_date.strftime('%Y-%m-%d')}.csv",
            float_format="%.0f",
            index=False,
        )


if __name__ == "__main__":
    calculate_ranking(datetime(2024, 2, 11))
