from dataclasses import dataclass, field


from mpm.config import MainConfig
from mpm.database import DatabaseInterface


@dataclass
class MordhauMonitor:
    config: MainConfig = field(default_factory=MainConfig)
    
    database: DatabaseInterface | None = field(default=None)
    
    def __post_init__(self):
        self.database = DatabaseInterface(
            self.config.databases.get_database_by_name(
                self.config.databases.selected
            )
        )
        
        