import time

from dataclasses import dataclass, field


@dataclass
class MordhauPlayer:
    playfab: str = field(default="")
    name: str = field(default="")
    
    join_time: float = field(default_factory=time.time)
    
    def get_session_time(self):
        return int(time.time() - self.join_time)