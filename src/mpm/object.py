from dataclasses import dataclass, field


@dataclass
class MordhauPlayer:
    playfab: str = field(default="")
    name: str = field(default="")
    