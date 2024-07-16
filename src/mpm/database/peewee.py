import peewee

from dataclasses import dataclass, field

from mpm.config import DatabaseType
from mpm.object import MordhauPlayer

from mpm.database.base import BaseDatabase


database_connection = peewee.Proxy()

class Playtime(peewee.Model):
    playfab = peewee.TextField(index=True, primary_key=True, unique=True)
    
    total_playtime = peewee.BigIntegerField(default=0)
    
    one_week = peewee.BigIntegerField(default=0)
    two_weeks = peewee.BigIntegerField(default=0)
    one_month = peewee.BigIntegerField(default=0)
    
    class Meta:
        database = database_connection


@dataclass
class PeeweeDatabase(BaseDatabase):
    connection: None | peewee.MySQLDatabase | peewee.SqliteDatabase | peewee.PostgresqlDatabase = field(
        default=None
    )
    
    def __get_playtime_model(self, playfab: str) -> Playtime:
        try:
            return Playtime.get(
                Playtime.playfab==playfab
            )
        except peewee.DoesNotExist: 
            return Playtime.create(
                playfab=playfab,
                one_week=0,
                two_weeks=0,
                one_month=0,
                total_playtime=0
            )
    
    def get_playtime_data(self, player: str | MordhauPlayer) -> dict:
        playfab = type(player) is MordhauPlayer and player.playfab or player
        result = self.__get_playtime_model(playfab)
        
        return {
            "playfab": playfab,
            "one_week": result.one_week,
            "two_weeks": result.two_weeks,
            "one_month": result.one_month,
            "total_playtime": result.total_playtime
        }
        
    def save_playtime_player(self, player: MordhauPlayer) -> dict:
        session = player.get_session_time()
        playtime_model = self.__get_playtime_model(player.playfab)
        
        playtime_model.total_playtime += session
        playtime_model.one_week += session
        playtime_model.two_weeks += session
        playtime_model.one_month += session
        
        playtime_model.save()
        
    def establish(self):
        match self.config.type:
            case DatabaseType.SQLITE:
                self.connection = peewee.SqliteDatabase(self.config.url)
            case DatabaseType.POSTGRES:
                self.connection = peewee.PostgresqlDatabase(
                    self.config.credentials.database,
                    user=self.config.credentials.username,
                    password=self.config.credentials.password,
                    host=self.config.host,
                    port=self.config.port
                )
            case DatabaseType.MYSQL:
                self.connection = peewee.MySQLDatabase(
                    self.config.credentials.database,
                    user=self.config.credentials.username,
                    password=self.config.credentials.password,
                    host=self.config.host,
                    port=self.config.port
                )
        
        database_connection.initialize(self.connection)
        self.connection.connect()
        
        if not self.connection.table_exists(Playtime):
            self.connection.create_tables([Playtime])
            self.connection.commit()
            
                
                