import glob
from pathlib import Path

import pandas as pd

DATA_DIRECTORY = Path(__file__).parent / "tournament_data"
POINTS_MAPPING = {
    1: 1000,
    2: 900,
    3: 800,
    4: 700,
    5: 500,
    6: 500,
    7: 400,
    8: 400,
    9: 300,
    10: 300,
    11: 300,
    12: 300,
    13: 225,
    14: 225,
    15: 225,
    16: 225,
    17: 150,
    18: 150,
    19: 150,
    20: 150,
    21: 150,
    22: 150,
    23: 150,
    24: 150,
    25: 125,
    26: 125,
    27: 125,
    28: 125,
    29: 125,
    30: 125,
    31: 125,
    32: 125,
    33: 100,
    34: 100,
    35: 100,
    36: 100,
    37: 100,
    38: 100,
    39: 100,
    40: 100,
    41: 75,
    42: 75,
    43: 75,
    44: 75,
    45: 75,
    46: 75,
    47: 75,
    48: 75,
    49: 50,
    50: 50,
    51: 50,
    52: 50,
    53: 50,
    54: 50,
    55: 50,
    56: 50,
    57: 25,
    58: 25,
    59: 25,
    60: 25,
    61: 25,
    62: 25,
    63: 25,
    64: 25,
}


def calculate_points(
    tournament_results: pd.DataFrame, ranking: pd.DataFrame
) -> pd.Series:
    multiplier = 1
    for player in tournament_results["name"]:
        rank_row = ranking[ranking["name"] == player]
        if not rank_row.empty:
            rank = rank_row["rank"].values[0]
            if rank < 10:
                multiplier += 0.06
            elif rank < 20:
                multiplier += 0.04
            elif rank < 30:
                multiplier += 0.02
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
    ranking["points"] = ranking[points_columns].apply(
        lambda row: row.nlargest(3).sum(), axis=1
    )
    ranking["rank"] = ranking["points"].rank(method="min", ascending=False).astype(int)
    return ranking


def calculate_ranking():
    ranking = pd.DataFrame(columns=["name"])
    tournament_files = sorted(glob.glob((DATA_DIRECTORY / "*.csv").as_posix()))

    # Add points for each tournament
    for tournament_file in tournament_files:
        tournament_results = pd.read_csv(tournament_file)
        tournament_results["points"] = calculate_points(tournament_results, ranking)
        ranking = add_results_to_ranking(
            Path(tournament_file).stem, tournament_results, ranking
        )
        ranking = update_current_standings(ranking)

    ranking.sort_values(by="points", ascending=False, inplace=True)
    columns_order = ["name", "rank", "points"] + [
        col for col in ranking.columns if col not in ["name", "rank", "points"]
    ]
    ranking = ranking[columns_order]
    ranking.to_csv("rankings.csv", index=False)


if __name__ == "__main__":
    calculate_ranking()
