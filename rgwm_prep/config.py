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
    pumps_wb: Path
    pumps_balance: Path
    inlaat_balance: Path
    pumps_wb_out: Path
    inlaat_wb_out: Path
    params: Path

class BalanceConfig(BaseModel):
    balance: bool
    
class Config(BaseModel):
    timeseries: TimeSeriesConfig
    season: SeasonConfig
    output: OutputConfig
    const_fluxes: ConstFluxesConfig
    balance: BalanceConfig

    @classmethod
    def load(cls, path: Path = Path("config.toml")) -> "Config":
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return cls(**data)
