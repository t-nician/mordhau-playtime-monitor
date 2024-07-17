from pymongo import MongoClient, timeout

from pymongo.errors import OperationFailure
from pymongo.database import Database
from pymongo.collection import Collection

from dataclasses import dataclass, field

from mpm.config import DatabaseType
from mpm.object import MordhauPlayer

from mpm.database.base import BaseDatabase


@dataclass
class MongoDatabase(BaseDatabase):
    connection: None | MongoClient = field(default=None)
    
    mordhau_database: None | Database = field(default=None)
    playtime_collection: None | Collection = field(default=None)
    
    def get_playtime_data(self, player: str | MordhauPlayer) -> dict:
        playfab = type(player) is MordhauPlayer and player.playfab or player
        
        try:
            return self.playtime_collection.find({
                    "playfab": playfab
            })[0]
        except Exception as _:
            if str(_) != "no such item for Cursor instance":
                raise _
                
            return {
                "playfab": playfab,
                "one_week": 0,
                "two_weeks": 0,
                "one_month": 0,
                "total_playtime": 0
            }
    
    def save_playtime_player(self, player: MordhauPlayer):
            session = player.get_session_time()
            existing_data = self.get_playtime_data(player.playfab)
            
            if existing_data:
                self.playtime_collection.insert_one({
                    "playfab": player.playfab,
                    "one_week": session,
                    "two_weeks": session,
                    "one_month": session,
                    "total_playtime": session
                })
            else:
                self.playtime_collection.update_one(
                    {"playfab": player.playfab},
                    {"$set": {
                        "one_week": existing_data["one_week"] + session,
                        "two_weeks": existing_data["two_weeks"] + session,
                        "one_month": existing_data["one_month"] + session,
                        "total_playtime": existing_data["total_playtime"] + session
                    }}
                )
    
    def establish(self):
        self.connection = MongoClient(
            host=self.config.url,
            username=self.config.credentials.username,
            password=self.config.credentials.password
        )
                    
        self.mordhau_database = self.connection[
            self.config.credentials.database
        ]
        
        self.playtime_collection = self.mordhau_database["playtime"]