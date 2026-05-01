from config import Config
import glob
from pathlib import Path
import pandas as pd
from utils import convert_m3_to_mil_m3

# Leakage
def process_leakage(fn_path: str | Path, output_fn: str | Path) -> None:
    """
    Process leakage time series and write the result to disk.

    Args:
        fn_path (str | Path): Path to the input leakage  
        output_fn (str | Path): Path where the output file will be written.

    Returns:
        None
            This function writes the processed data to disk and does not return a DataFrame.
    """

# Lock operations 
def process_lock_operations(fn_path: str | Path, output_fn: str | Path) -> None:
    """
    Process process_lock_operations and write the result to disk.

    Args:
        fn_path (str | Path): 
        output_fn (str | Path): Path where the output file will be written.

    Returns:
        None
            This function writes the processed data to disk and does not return a DataFrame.
    """

# Upwards groundwater fluxes
def process_up_grndwater_flux(fn_path: str | Path, output_fn: str | Path) -> None:
    """
    Process process_up_grndwater_fluxes and write the result to disk.

    Args:
        fn_path (str | Path): Path to the 
        output_fn (str | Path): Path where the output file will be written.

    Returns:
        None
            This function writes the processed data to disk and does not return a DataFrame.
    """
    
def process_const_fluxes(fn_leackage: str | Path, fn_lock_operations: str | Path, fn_up_grndwater_flux: str | Path) -> None:
    """Processes afvoer and aanvoer from the VZM sluises
    Args:
        fn_leackage (str | Path): file path to the
        fn_lock_operations (str | Path): file path to the
        fn_up_grndwater_flux (str | Path): file path to the
    """
    config = Config.load()
    output_fn = config.output.output
    
    process_leakage(fn_leackage, output_fn)
    process_lock_operations(fn_lock_operations, output_fn)
    process_up_grndwater_flux(fn_up_grndwater_flux, output_fn)
    