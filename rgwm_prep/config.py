from pathlib import Path
from pydantic import BaseModel
import tomllib


class TimeSeriesConfig(BaseModel):
    meteo: Path
    discharge: Path
    pumps: Path
    flushing: Path

class SeasonConfig(BaseModel):
    summer_months: list
    winter_months: list
    
class OutputConfig(BaseModel):
    output: Path

class Config(BaseModel):
    timeseries: TimeSeriesConfig
    season: SeasonConfig
    output: OutputConfig

    @classmethod
    def load(cls, path: Path = Path("config.toml")) -> "Config":
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return cls(**data)