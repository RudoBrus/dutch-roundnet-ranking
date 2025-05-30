from pathlib import Path

# Where to get the tournament data from
TOURNAMENT_DATA_DIRECTORY = Path(__file__).parent / "tournament_data"

# Where to safe the ranking results
RANKING_RESULT_FOLDER = Path(__file__).parent.parent / "rankings"

# Currently supported categories
CATEGORIES = ["women", "advanced", "intermediate", "beginner"]


# Rules for the ranking system

# The best three tournament results count towards the ranking.
MAX_COUNTING_TOURNAMENTS = 3

# The base points awarded for a tournament based on team placement.
# For example, the first place team both get 700 points,
# the 6th placed team both get 420 points.
TOURNAMENT_BASE_POINTS = {
    1: 700,
    2: 630,
    3: 560,
    4: 490,
    **dict.fromkeys(range(5, 7), 420),
    **dict.fromkeys(range(7, 9), 350),
    **dict.fromkeys(range(9, 13), 280),
    **dict.fromkeys(range(13, 17), 210),
    **dict.fromkeys(range(17, 25), 140),
    **dict.fromkeys(range(25, 33), 105),
    **dict.fromkeys(range(33, 65), 70),
}


# High ranked players at a tournament increase the points awarded to
# all players at the tournament.
# The multiplier is 0.1 for ranks 1-10, 0.06 for ranks 11-20,
# 0.03 for ranks 21-30, and 0.005 for ranks 31-50.
PLAYER_MULTIPLIERS = {
    rank: 0.1 if rank <= 10 else 0.06 if rank <= 20 else 0.03 if rank <= 30 else 0.005
    for rank in range(1, 51)
}

# A tournament becomes worth less points the older it is.
# The multiplier is 1.0 for tournaments up to 12 months old, 0.8 between 12-18 months,
# 0.6 between 18-24 months, 0.4 between 24-48 months and 0 points afterwards.
AGE_MULTIPLIERS = {
    age_in_months: 1.0
    if age_in_months < 12
    else 0.8
    if age_in_months < 18
    else 0.6
    if age_in_months < 24
    else 0.4
    for age_in_months in range(0, 48)
}
