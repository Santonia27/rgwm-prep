from config import Config
import glob
from pathlib import Path
import pandas as pd
from utils import convert_datetime, convert_m3_to_mil_m3
import numpy as np


def format_value(x):
    if x == 0 or x == 0.0:
        return "0"
    return str(x)


def process_aanvoer_pump(fn_path: str | Path, output_fn: str | Path, balance: bool = False):
    """Get the pump volume in Q in miljoen m3/dag per pump
        VZM include the following pump stations:
            - Bathse spuisluis gecorrigeerd
            - Krammer
            - Kreekrak
    Args:
        fn_path (str): file path to the pump time series in XYZ per day
        output_fn (str | Path): file path to where to store the output file
        balance (boolean): If True write output in Balance format. If false write output in gap-fill/model format,. Default is set to False.

    Returns
    -------
        aanvoer_per_pump_df: aanvoer per pump in Q in miljoen m3 per dag
    """
    for file in glob.glob(f"{fn_path}/*"):
        if file.endswith(".csv"):
            fn = Path(file)
            name = fn.stem.split("pump_")[-1]
            pump_timeseries_df = pd.read_csv(file, sep=";")

            for idx, row in pump_timeseries_df.iterrows():
                # Convert gaps to 0 values
                if row["WAARDE"] == 0 and idx > 0 and idx < (len(pump_timeseries_df)-1):
                    pump_timeseries_df.loc[idx, "WAARDE"] = np.nan


            # wb = get_waterboard(name, fn_path) # Still need to implement this. The path sholud be th epath to the waterboard

            aanvoer_per_pump_df = pump_timeseries_df
            
            if balance:
                # Convert datetime format, convert m3 to miljoes m3
                aanvoer_per_pump_df = convert_datetime(aanvoer_per_pump_df)
                aanvoer_per_pump_df = convert_m3_to_mil_m3(aanvoer_per_pump_df) #NOTE This may not be needed as outputs may already be in mil3
                # Save .VZM input file
                output = output_fn / "in" / f"VZM_Gemaal_{name}_mil3.VZM"

                with open(output, "w") as f:
                    f.write(f"Gemaal_{name}\n")
                    f.write(f"* {name} Gemaal TS\n")
                    f.write("* Q in miljoen m3 per dag\n")
                    f.write("* period 2010 t/m 2018\n")
                    f.write(f"* VZM_Gemaal_{name}.VZM\n")
                    f.write("* waterboard_ \n") #Still needs to be implement
                    f.write("*DATUM WAARDE\n")
                    aanvoer_per_pump_df.to_csv(f, sep=" ", index=False, header=False)
            else:
                # Save .VZM input file
                output = output_fn / "in" / f"VZM_Gemaal_{name}_m3.csv"
                
                with open(output, "w", newline="") as f:
                    f.write("# Waarnemingssoort,begindatum,begintijd,tijdstap in minuten\n")
                    f.write(f"# {name} (m3)\n")
                    f.write("Q 2010-01-01 12:00 1440\n")
                    aanvoer_per_pump_df["WAARDE"].to_csv(
                        f, sep=" ", index=False, header=False, float_format="%.10g"
                    )


def process_pumps(fn_path: str | Path, balance: bool = False):
    """Processes afvoer and aanvoer from the VZM pumps
    Args:
        fn_path (str: Path): file path to the pump time series in Q in miljoen m3 per day
        balance (boolean): If True write output in Balance format. If false write output in gap-fill/model format,. Default is set to False.
    """
    config = Config.load()
    output_fn = config.output.output

    process_aanvoer_pump(fn_path, output_fn, balance)
