import json
from dataclasses import dataclass, asdict, field


@dataclass
class RetentionPolicy:
    keep_last: int = 0
    keep_days: int = 0
    keep_hourly: int = 24
    keep_daily: int = 7
    keep_weekly: int = 4
    keep_monthly: int = 12

    def load(self, config: dict) -> None:
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def save(self, config: dict) -> None:
        for key, value in asdict(self).items():
            config[key] = value


@dataclass
class PluginOptions:
    output: str = "./backups"
    output_tmp: str = "./backups/.tmp"
    filename: str = "{level_name}_{timestamp}"
    extension: str = ".mcworld"
    compress: bool = True
    schedule: str = ""
    timeout: int = 60  # seconds
    worlds_path: str = "./worlds"
    retention: RetentionPolicy = field(default_factory=RetentionPolicy)

    def load(self, config: dict) -> None:
        for key, value in config.items():
            if key == "retention" and isinstance(value, dict):
                self.retention.load(value)
            elif hasattr(self, key):
                setattr(self, key, value)

    def save(self, config: dict) -> None:
        for key, value in asdict(self).items():
            config[key] = value

    def dump(self) -> str:
        return json.dumps(asdict(self))
