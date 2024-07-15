import os
import json5

from enum import Enum
from dataclasses import dataclass, field


class DatabaseType(Enum):
    SQLITE = "sqlite"
    MONGODB = "mongodb"


__DB_TYPE_TO_STR = lambda type: ( 
    "  " * 5 + "DatabaseType." + type.name + f"(\"{type.value}\")\n"
)

DB_CONF_INVALID_TYPE = "Invalid DatabaseType!\n\n"
DB_CONF_INVALID_TYPE = DB_CONF_INVALID_TYPE + "databases.{0}.{1} = '{2}' {3}"
DB_CONF_INVALID_TYPE = DB_CONF_INVALID_TYPE + "\n"
DB_CONF_INVALID_TYPE = DB_CONF_INVALID_TYPE + "\nAvailable DatabaseTypes:\n"

__COMPILED_DATABASE_TYPES = [__DB_TYPE_TO_STR(type) for type in DatabaseType]

DB_CONF_INVALID_TYPE = DB_CONF_INVALID_TYPE + "".join(
    __COMPILED_DATABASE_TYPES
)

DB_CONF_INVALID_TYPE = DB_CONF_INVALID_TYPE.removesuffix("\n")

MAIN_CONF_INVALID_PATH = "Cannot load config from path: '{0}'"
MAIN_CONF_DUPE_NAME = ""


@dataclass
class Credentials:
    username: str = field(default="")
    password: str = field(default="")
    

@dataclass
class DatabaseConfig:
    url: str = field(default="")
    
    name: str = field(default="")
    type: DatabaseType = field(default="")
    
    credentials: Credentials | None = field(default=None)
    
    def __conf_invalid_database_type(self):
        raise Exception(
            DB_CONF_INVALID_TYPE.format(
                str(self.name), "type", str(self.type), str(type(self.type))
            )
        )
    
    def __post_init__(self):
        __type_class = type(self.type)
        
        if __type_class is str:
            if self.type == "":
                self.__conf_invalid_database_type()
        elif __type_class is not DatabaseType:
            self.__conf_invalid_database_type()
        
        try:
            self.type = DatabaseType(self.type)
        except:
            self.__conf_invalid_database_type()


@dataclass
class Rcon:
    host: str = field(default="")
    port: int = field(default=-1)
    
    password: str = field(default="")


@dataclass
class Databases:
    selected: str = field(default="")
    
    options: list[DatabaseConfig] = field(default_factory=list)


@dataclass
class MainConfig:
    path: str = field(default="./config.jsonc")
    
    rcon: Rcon | None = field(default=None)
    databases: Databases | None = field(default=None)
    
    def get_database_by_name(self, name: str) -> DatabaseConfig | None:
        for database in self.databases.options:
            if database.name == name:
                return database
    
    def __post_init__(self):
        assert os.path.exists(self.path), MAIN_CONF_INVALID_PATH.format(
            self.path
        )
        
        config = {}
            
        with open(self.path, "r") as file:
            config = json5.loads(file.read())
        
        self.rcon = Rcon(**config.get("rcon"))
        self.databases = Databases(config.get("databases").get("selected"))
        
        for database_dict in config.get("databases").get("options"):
            creds = database_dict.get("credentials")
            existing_database = self.get_database_by_name(
                database_dict.get("name")
            )
            
            assert existing_database is None, 
            
            if creds:
                del database_dict["credentials"]
                
                self.databases.options.append(
                    DatabaseConfig(
                        credentials=Credentials(**creds),
                        **database_dict
                    )
                )
            else:
                self.databases.options.append(DatabaseConfig(**database_dict))
        
        
            