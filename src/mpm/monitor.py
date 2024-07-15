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
            while time.sleep(1) or True:
                str_playerlist = client.run("playerlist")
                
                str_playerlist = str_playerlist.split("\n")
                str_playerlist.pop()
                
                dict_playerlist: dict[str, MordhauPlayer] = {}
                
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
                        #print(playfab, name, "joined!")
                        # TODO emit that a player has joined!
                    
                    dict_playerlist[playfab] = player
                
                for player in self.playerlist:
                    if not dict_playerlist.get(player.playfab):
                        self.__remove_player_from_playerlist(player.playfab)
                        self.__emit(self.__on_leave_listeners, player)
                        #print(player.playfab, player.name, "left!")
                        
                        # TODO emit player left!
                    #playerlist[index] = self.get_player_by_playfab(playfab) or MordhauPlayer(playfab, name)