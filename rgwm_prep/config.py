from pathlib import Path
from pydantic import BaseModel
import tomllib


class ConstFluxesConfig(BaseModel):
    leakage: Path
    lock_operations: Path
    up_grndwater_flux: Path


class OutputConfig(BaseModel):
    output: Path


class SeasonConfig(BaseModel):
    summer_months: list
    winter_months: list


class TimeSeriesConfig(BaseModel):
    meteo: Path
    discharge: Path
    pumps: Path
    params: Path


class Config(BaseModel):
    timeseries: TimeSeriesConfig
    season: SeasonConfig
    output: OutputConfig
    const_fluxes: ConstFluxesConfig

    @classmethod
    def load(cls, path: Path = Path("config.toml")) -> "Config":
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return cls(**data)
