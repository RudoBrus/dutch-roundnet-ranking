import sqlite3
import uuid
from rnl_player import RNLPlayer

class RNLPlayerMgr:
    """
    Manage the players and database in the ranking system
    todo:
    - add db make, save and load
    """
    def __init__(self, ranking_folder : Path):
        self.ranking_folder = ranking_folder
        self.player_db_file = self.ranking_folder / "players.db"

        self.players : dict[str, RNLPlayer] = {} # RNLPlayer
        self.playerbook : dict[str, str] = {} # dict containing player_id(key) and player_name(value)

        self.make_player_db()

    def make_player_db(self):
        """
        TODO work this out further later        
        save the playerbook to the player_db_file
        """		

        if not self.player_db_file.exists():
            self.player_db_file.touch()

        conn = sqlite3.connect(self.player_db_file)
        cursor = conn.cursor()

        cursor.execute("CREATE TABLE players (player_id TEXT, player_name TEXT)")
        conn.commit()

    def save_playerbook(self):
        """
        save the playerbook/players to the player_db_file
        """
        pass

    @staticmethod
    def load_player_db(self, ranking_folder : Path) -> RNLPlayerMgr:
        """
        load the playerbook/players from the player_db_file
        """
        pass

    def get_player_id(self, player_name : str) -> str | None:
        """
        get the player_id of a player and check if the player exists
        """
        if player_name in self.playerbook.values():
            player_id = list(self.playerbook.keys())[list(self.playerbook.values()).index(player_name)]
            return player_id
        else:
            return None

    def add_player(self, player_name):
        if self.get_player_id(player_name) is None:
            player_id = str(uuid.uuid4())
            self.playerbook[player_id] = player_name
            self.players[player_id] = RNLPlayer(player_id, player_name)
        else:
            raise ValueError(f"Player {player_name} already exists")

    def get_player(self, player_id : str) -> RNLPlayer | None:
        """
        get a player from the playerbook
        """
        if player_id in self.players:
            return self.players[player_id]
        else:
            return None
        
    def get_player_book(self) -> dict[str, str]:
        """
        get the playerbook, a dict containing player_id(key) and player_name(value)
        """
        return self.playerbook
        

