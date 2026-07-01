from config import Config
from pathlib import Path
import pandas as pd
from utils import convert_datetime


# Leakage
def process_leakage(
    fn_path: str | Path, output_fn: str | Path, fn_params: str | Path, balance: bool
) -> None:
    """
    Process leakage time series and write the result to disk.

    Args:
        fn_path (str | Path):Path to the leakage values in m3/d
        output_fn (str | Path): Path where the output file will be written
        fn_params (str | Path): Path to additional inputs

    Returns:
        None
            This function writes the processed data to disk and does not return a DataFrame.
    """
    leackage_df = pd.read_csv(fn_path, sep=";")

    # If outflow, convert to negative value so they will be subtracted when calculating the sum
    leackage_df.loc[
        leackage_df["richting"].str.contains("out", case=False, na=False), "m3/d"
    ] *= -1

    leackage_df["cl"] = (
        leackage_df["m3/d"] * leackage_df["cl_conc"] / 1000000000
    )
    timeseries_df = pd.read_csv(fn_params / "date_timeseries.csv")
    sum = leackage_df["m3/d"].sum(axis=0) / 1000000
   
    cl_sum = leackage_df["cl"].sum(axis=0)
    
    # Convert datetime
    timeseries_df = convert_datetime(timeseries_df, balance,"" )

    # Create leackage df
    leackage_df = timeseries_df.copy()
    cl_leackage= timeseries_df.copy()
    
    leackage_df["WAARDE"] = sum   

    # Save .VZM input file
    output = output_fn / "in" /"VZM_leackage.VZM"

    with open(output, "w") as f:
        f.write("Leakage\n")
        f.write("* Leakage\n")
        f.write("* Leackage miljoen m3 per dag\n")
        f.write("* period 2010 t/m 2018\n")
        f.write("* Lek\n")
        f.write("* cumulative\n")
        f.write("*DATUM WAARDE\n")
        leackage_df.to_csv(f, sep=" ", index=False, header=False)

    # Save .VZM input file
    output = output_fn / "in" /"Cl_VZM_leackage.VZM"
    
    cl_leackage["WAARDE"] = cl_sum
    
    with open(output, "w") as f:
        f.write("Chloride Leakage\n")
        f.write("* Leakage\n")
        f.write("* Leackage miljoen m3 per dag\n")
        f.write("* period 2010 t/m 2018\n")
        f.write("* Lek\n")
        f.write("* cumulative\n")
        f.write("*DATUM WAARDE\n")
        cl_leackage.to_csv(f, sep=" ", index=False, header=False)


# Lock operations
def process_lock_operations(
    fn_path: str | Path, output_fn: str | Path, fn_params: str | Path, balance: bool
) -> None:
    """
    Process process_lock_operations and write the result to disk.

    Args:
        fn_path (str | Path): Path to the lock operation values in m3/d
        output_fn (str | Path): Path where the output file will be written
        fn_params (str | Path): Path to additional inputs

    Returns:
        None
            This function writes the processed data to disk and does not return a DataFrame.
    """
    lock_operations_df = pd.read_csv(fn_path, sep=";")

    # If outflow, convert to negative value so they will be subtracted when calculating the sum
    lock_operations_df.loc[
        lock_operations_df["richting"].str.contains("UIT", case=False, na=False), "m3/d"
    ] *= -1

    
    lock_operations_df["cl"] = (
        lock_operations_df["m3/d"] * lock_operations_df["cl_conc"] / 1000000000
    )

    
    timeseries_df = pd.read_csv(fn_params / "date_timeseries.csv")
    sum = lock_operations_df["m3/d"].sum(axis=0) / 1000000
    cl_sum = lock_operations_df["cl"].sum(axis=0)

    # Convert datetime
    timeseries_df = convert_datetime(timeseries_df, balance, "")

    # Create leackage df
    lock_operations_df = timeseries_df.copy()
    cl_lock_operations_df= timeseries_df.copy()
    lock_operations_df["WAARDE"] = sum
    cl_lock_operations_df["WAARDE"] = cl_sum
    
    # Save .VZM input file
    output = output_fn / "in" /"VZM_lock_operations.VZM"

    with open(output, "w") as f:
        f.write("Chloride lock_operations\n")
        f.write("* lock_operations\n")
        f.write("* lock_operations miljoen m3 per dag\n")
        f.write("* period 2010 t/m 2018\n")
        f.write("* Schutten\n")
        f.write("* cumulative\n")
        f.write("*DATUM WAARDE\n")
        lock_operations_df.to_csv(f, sep=" ", index=False, header=False)
    
        # Save .VZM input file
    output = output_fn / "in" /"CL_VZM_lock_operations.VZM"

    with open(output, "w") as f:
        f.write("lock_operations\n")
        f.write("* lock_operations\n")
        f.write("* lock_operations miljoen m3 per dag\n")
        f.write("* period 2010 t/m 2018\n")
        f.write("* Schutten\n")
        f.write("* cumulative\n")
        f.write("*DATUM WAARDE\n")
        cl_lock_operations_df.to_csv(f, sep=" ", index=False, header=False)


# Upwards groundwater fluxes
def process_up_grndwater_flux(
    fn_path: str | Path, output_fn: str | Path, fn_params: str | Path, balance: bool
) -> None:
    """
    Process process_up_grndwater_fluxes and write the result to disk.

    Args:
        fn_path (str | Path): Path to the upward groundwater flux values in m3/d
        output_fn (str | Path): Path where the output file will be written
        fn_params (str | Path): Path to additional inputs

    Returns:
        None
            This function writes the processed data to disk and does not return a DataFrame.
    """
    up_grndwater_flux_df = pd.read_csv(fn_path, sep=";")

    # If outflow, convert to negative value so they will be subtracted when calculating the sum
    up_grndwater_flux_df.loc[
        up_grndwater_flux_df["richting"].str.contains("out", case=False, na=False),
        "m3/d",
    ] *= -1

    up_grndwater_flux_df["cl"] = (
        up_grndwater_flux_df["m3/d"] * up_grndwater_flux_df["cl_conc"] / 1000000000
    )
    
    timeseries_df = pd.read_csv(fn_params / "date_timeseries.csv")
    sum = up_grndwater_flux_df["m3/d"].sum(axis=0) / 1000000
    cl_sum = up_grndwater_flux_df["cl"].sum(axis=0)
    
    # Convert datetime
    timeseries_df = convert_datetime(timeseries_df, balance, "")

    # Create leackage df
    up_grndwater_flux_df = timeseries_df.copy()
    up_grndwater_flux_df["WAARDE"] = sum
    
    cl_up_grndwater_flux_df= timeseries_df.copy()
    cl_up_grndwater_flux_df["WAARDE"] = cl_sum
    
        # Save .VZM input file
    output = output_fn / "in" / "VZM_groundwater_fluxes.VZM"

    with open(output, "w") as f:
        f.write("Up groundwater fluxes\n")
        f.write("* Up groundwater fluxes\n")
        f.write("* Up groundwater fluxes miljoen m3 per dag\n")
        f.write("* period 2010 t/m 2018\n")
        f.write("* Kwell\n")
        f.write("* cumulative\n")
        f.write("*DATUM WAARDE\n")
        up_grndwater_flux_df.to_csv(f, sep=" ", index=False, header=False)

        # Save .VZM input file
    output = output_fn / "in" / "Cl_VZM_groundwater_fluxes.VZM"

    with open(output, "w") as f:
        f.write("Up groundwater fluxes\n")
        f.write("* Up groundwater fluxes\n")
        f.write("* Up groundwater fluxes miljoen m3 per dag\n")
        f.write("* period 2010 t/m 2018\n")
        f.write("* Kwell\n")
        f.write("* cumulative\n")
        f.write("*DATUM WAARDE\n")
        cl_up_grndwater_flux_df.to_csv(f, sep=" ", index=False, header=False)


def process_const_fluxes(
    fn_leackage: str | Path,
    fn_lock_operations: str | Path,
    fn_up_grndwater_flux: str | Path,
    fn_params: str | Path,
    balance: bool
) -> None:
    """Processes afvoer and aanvoer from the VZM sluises
    Args:
        fn_leackage (str | Path): Path to the leakage values in m3/d
        fn_lock_operations (str | Path): Path to the lock operation values in m3/d
        fn_up_grndwater_flux (str | Path): Path to the upward groundwater flux values in m3/d
        fn_params (str | Path): Path to additional inputs
    """
    config = Config.load()
    output_fn = config.output.output

    process_leakage(fn_leackage, output_fn, fn_params, balance)
    process_lock_operations(fn_lock_operations, output_fn, fn_params, balance)
    process_up_grndwater_flux(fn_up_grndwater_flux, output_fn, fn_params, balance)
