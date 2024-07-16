from dataclasses import dataclass, field

from mpm.object import MordhauPlayer
from mpm.config import DatabaseType, DatabaseConfig

from mpm.database import mongodb, peewee, base


@dataclass
class DatabaseInterface:
    config: DatabaseConfig | None = field(default=None)
    
    database: base.BaseDatabase | None = field(default=None)
    
    def save_playtime_data(self, player: MordhauPlayer):
        self.database.save_playtime_player(player)
    
    def __post_init__(self):
        if self.config is not None:
            match self.config.type:
                case DatabaseType.POSTGRES:
                    self.database = peewee.PeeweeDatabase(self.config)
                case DatabaseType.SQLITE:
                    self.database = peewee.PeeweeDatabase(self.config)
                case DatabaseType.MYSQL:
                    self.database = peewee.PeeweeDatabase(self.config)
                case DatabaseType.MONGODB:
                    self.database = mongodb.MongoDatabase(self.config)
            
            self.database.establish()
                