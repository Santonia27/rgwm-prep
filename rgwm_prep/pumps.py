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

def process_aanvoer_pump(fn_path: str | Path, output_fn: str | Path):
    """Get the pump volume in Q in miljoen m3/dag per pump
        VZM include the following pump stations:
            - Bathse spuisluis gecorrigeerd
            - Krammer
            - Kreekrak
    Args:
        fn_path (str): file path to the pump time series in XYZ per day
        output_fn (str | Path): file path to where to store the output file

    Returns
    -------
        aanvoer_per_pump_df: aanvoer per pump in Q in miljoen m3 per dag
    """
    for file in glob.glob(f"{fn_path}/*"):
        if file.endswith(".csv"):
            fn = Path(file)
            name = fn.stem.split("pump_")[-1]
            pump_timeseries_df = pd.read_csv(file, sep=";")
            #pump_timeseries_df["WAARDE"] = pump_timeseries_df["WAARDE"].astype(float)

            # Convert datetime format, convert m3 to miljoes m3
            pump_timeseries_df = convert_datetime(pump_timeseries_df)
            pump_timeseries_df = convert_m3_to_mil_m3(pump_timeseries_df) 
            
            for idx, row in pump_timeseries_df.iterrows():
                # Convert gaps to 0 values
                if row["WAARDE"] is np.nan or row["WAARDE"] == "":
                    pump_timeseries_df.loc[idx, "WAARDE"] = 0
                    
                    
                
            aanvoer_per_pump_df = pump_timeseries_df
            # Save .VZM input file
            output = output_fn / "in" / f"VZM_Gemaal_{name}.VZM"

            with open(output, "w") as f:
                f.write(f"Gemaal_{name}\n")
                f.write("* Q in miljoen m3 per dag\n")
                f.write("* period 2010 t/m 2018\n")
                f.write("*DATUM WAARDE\n")
                aanvoer_per_pump_df.to_csv(f, sep=" ", index=False, header=False)
            #with open(output, "w") as f:
            #    f.write("# Waarnemingssoort,begindatum,begintijd,tijdstap in minuten\n")
            #    f.write(f"# {name}\n")
            #    f.write("H 2010-01-01 12:00 1440\n")
            #    aanvoer_per_pump_df["WAARDE"].to_csv(f, sep=" ", index=False, header=False, float_format="%.10g")


def process_pumps(fn_path: str | Path):
    """Processes afvoer and aanvoer from the VZM pumps
    Args:
        fn_path (str: Path): file path to the pump time series in Q in miljoen m3 per day
    """
    config = Config.load()
    output_fn = config.output.output

    process_aanvoer_pump(fn_path, output_fn)
