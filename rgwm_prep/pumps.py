from config import Config
import glob
from pathlib import Path
import pandas as pd
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

            for idx, row in pump_timeseries_df.iterrows():
                # Convert gaps to 0 values
                if (
                    row["WAARDE"] == 0
                    and idx > 0
                    and idx < (len(pump_timeseries_df) - 1)
                ):
                    pump_timeseries_df.loc[idx, "WAARDE"] = np.nan

            # wb = get_waterboard(name, fn_path) # Still need to implement this. The path sholud be th epath to the waterboard

            aanvoer_per_pump_df = pump_timeseries_df

            # Save .VZM input file
            output = output_fn / "in" / f"VZM_Gemaal_{name}_m3.csv"

            with open(output, "w", newline="") as f:
                f.write("# Waarnemingssoort,begindatum,begintijd,tijdstap in minuten\n")
                f.write(f"# Gemaal_{name} (m3)\n")
                f.write("Q 2010-01-01 12:00 1440\n")
                aanvoer_per_pump_df["WAARDE"].to_csv(
                    f, sep=" ", index=False, header=False, float_format="%.10g"
                )

            with open(output, "r") as f:
                lines = f.readlines()

            with open(output, "w") as f:
                for line in lines:
                    stripped = line.strip()

                    # cases that produce ""
                    if stripped == '""' or stripped == "":
                        f.write("\n")

                    else:
                        f.write(line)


def process_pumps(fn_path: str | Path):
    """Processes afvoer and aanvoer from the VZM pumps
    Args:
        fn_path (str: Path): file path to the pump time series in Q in miljoen m3 per day
    """
    config = Config.load()
    output_fn = config.output.output

    process_aanvoer_pump(fn_path, output_fn)
