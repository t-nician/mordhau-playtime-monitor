from dataclasses import dataclass, field


from mpm.config import DatabaseConfig


@dataclass
class BaseDatabase:
    config: DatabaseConfig | None = field(default=None)

    def establish(self):
        pass