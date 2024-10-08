import time

from dataclasses import dataclass, field

from rcon.source import Client

from mpm.config import MainConfig

from mpm.object import MordhauPlayer
from mpm.database import DatabaseInterface


@dataclass
class MordhauMonitor:
    config: MainConfig = field(default_factory=MainConfig)

    database: DatabaseInterface | None = field(default=None)
    playerlist: list[MordhauPlayer] = field(default_factory=list)
    
    __on_join_listeners: list[(MordhauPlayer)] = field(default_factory=list)
    __on_leave_listeners: list[(MordhauPlayer)] = field(default_factory=list)
        
    def __post_init__(self):
        self.database = DatabaseInterface(
            self.config.databases.get_database_by_name(
                self.config.databases.selected
            )
        )
    
    def __remove_player_from_playerlist(self, playfab: str):
        player = None
        
        for c_player in self.playerlist:
            if c_player.playfab == playfab:
                player = c_player
                break
        
        if player is not None:
            self.playerlist.remove(player)
    
    def __emit(self, func_list: list[(any)], *args):
        for func in func_list:
            func(*args)
    
    def on_join(self, func):
        self.__on_join_listeners.append(func)
        def wrapper(*arg, **kwargs):
            return func(*arg, **kwargs)
        return wrapper
    
    def on_leave(self, func):
        self.__on_leave_listeners.append(func)
        def wrapper(*arg, **kwargs):
            return func(*arg, **kwargs)
        return wrapper
    
    def save_player_playtime(self, player: MordhauPlayer):
        self.database.save_playtime_data(player)
    
    def get_player_by_playfab(self, playfab: str) -> MordhauPlayer | None:
        for player in self.playerlist:
            if player.playfab == playfab:
                return player
        
    def start_playtime_monitor(self):
        with Client(
            self.config.rcon.host, 
            self.config.rcon.port, 
            passwd=self.config.rcon.password
        ) as client:
            client.timeout = 5
            failures = 0
            
            while time.sleep(1) or True:
                str_playerlist = ""
                
                try:
                    str_playerlist = client.run("playerlist")
                except Exception as exc:
                    exc_str = str(exc)
                    failures += 1
                    
                    if failures >= 5:
                        raise Exception("more than 5 failures restart time!")
                    
                    if exc_str != "timed out" and exc_str != "packet ID mismatch":
                        raise Exception("failed to get playerlist!")
                
                str_playerlist = str_playerlist.split("\n")
                
                if len(str_playerlist) == 0:
                    continue
                
                str_playerlist.pop()
                
                dict_playerlist: dict[str, MordhauPlayer] = {}
                
                if len(str_playerlist) == 0:
                    pass
                    
                for player_str in str_playerlist:
                    playfab, *remaining = player_str.split(", ")
                    
                    remaining.pop()
                    remaining.pop()
                    
                    name = ', '.join(remaining)
                    
                    player = self.get_player_by_playfab(playfab)
                    
                    if not player:
                        player = MordhauPlayer(playfab, name)
                        self.playerlist.append(player)
                        self.__emit(self.__on_join_listeners, player)
                    
                    dict_playerlist[playfab] = player
                
                for player in self.playerlist:
                    if not dict_playerlist.get(player.playfab):
                        self.__remove_player_from_playerlist(player.playfab)
                        self.__emit(self.__on_leave_listeners, player)