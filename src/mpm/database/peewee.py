import peewee

from dataclasses import dataclass, field


from mpm.config import DatabaseType
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
            
                
                