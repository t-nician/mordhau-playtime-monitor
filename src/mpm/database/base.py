from dataclasses import dataclass, field


from mpm.config import DatabaseConfig
from mpm.object import MordhauPlayer


@dataclass
class BaseDatabase:
    config: DatabaseConfig | None = field(default=None)

    def save_playtime_player(self, player: MordhauPlayer):
        pass
    
    def get_playtime_data(self, player: MordhauPlayer) -> dict:
        pass
    
    def establish(self):
        pass