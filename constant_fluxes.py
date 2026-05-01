from config import Config
import glob
from pathlib import Path
import pandas as pd
from datetime import datetime

def process_const_fluxes(fn_path: str | Path):
    """Processes afvoer and aanvoer from the VZM sluises
    Args:
        fn_path (str | Path): file path to the discharge time series per sluises in m3 per day
    """
    config = Config.load()
    output_fn = config.output.output
    
    const_ = config

    process_leakage(fn_path, output_fn)
    process_lock_operations(fn_path, output_fn)
    process_up_grndwater_flux(fn_path, output_fn)
    