import json
from pathlib import Path

RANKING_RESULT_FOLDER = Path(__file__).parent.parent / "rankings"
TOURNAMENT_RECORDS_FOLDER = Path(__file__).parent / "tournament_data"
with open(Path(__file__).parent / "rules.json") as file:
    RULES = json.load(file)
