from config import Config
import glob
from pathlib import Path
import pandas as pd
from utils import convert_datetime, convert_m3_to_mil_m3
import os
## Afvoer
def process_aanvoer_chloride(fn_path: str | Path, output_fn: str | Path):
    """Get the aanvoer chloride
    Args:
        fn_path (str | Path): file path to the aanvoer chloride time series per sluises in m3 per day
        output_fn (str | Path): file path to where to store the output file

    Returns
    -------
        aanvoer_df: aanvoer chloride
    """
    for file in glob.glob(f"{fn_path}/*"):
        if file.endswith(".csv") and "IN" in file:
            fn = Path(file)
            name = fn.stem.split("cl_")[-1]
            chloride_timeseries_df = pd.read_csv(file, sep=";")
            chloride_timeseries_df["WAARDE"] = chloride_timeseries_df[
                "WAARDE"
            ].astype(float)

            # Convert datetime format
            chloride_timeseries_df = convert_datetime(chloride_timeseries_df)

            folder = output_fn / "in" / "cl_balance_input"
            os.makedirs(folder, exist_ok=True)
                
            output = folder / f"cl_{name}.csv"

            with open(output, "w", newline="") as f:
                f.write("# Waarnemingssoort,begindatum,begintijd,tijdstap in minuten\n")
                f.write(f"# Gemaal_{name} (mg/l)\n")
                f.write("Q 2010-01-01 12:00 1440\n")
                chloride_timeseries_df["WAARDE"].to_csv(
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


def process_afvoer_chloride(fn_path: str | Path, output_fn: str | Path):
    """Get the aanvoer chloride
    Args:
        fn_path (str | Path): file path to the aanvoer chloride time series per sluises in m3 per day
        output_fn (str | Path): file path to where to store the output file

    Returns
    -------
        aanvoer_df: aanvoer chloride
    """
    for file in glob.glob(f"{fn_path}/*"):
        if file.endswith(".csv") and "OUT" in file:
            fn = Path(file)
            name = fn.stem.split("cl_")[-1]
            chloride_timeseries_df = pd.read_csv(file, sep=";")
            chloride_timeseries_df["WAARDE"] = chloride_timeseries_df[
                "WAARDE"
            ].astype(float)

            folder = output_fn / "out" / "cl_balance_input"
            os.makedirs(folder, exist_ok=True)
                
            output = folder / f"cl_{name}.csv"

            with open(output, "w", newline="") as f:
                f.write("# Waarnemingssoort,begindatum,begintijd,tijdstap in minuten\n")
                f.write(f"# Cl_{name} (mg/l)\n")
                f.write("Q 2010-01-01 12:00 1440\n")
                chloride_timeseries_df["WAARDE"].to_csv(
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


def process_chloride(fn_path: str | Path):
    """Processes afvoer and aanvoer from the VZM sluises
    Args:
        fn_path (str | Path): file path to the chloride time series per sluises in m3 per day
    """
    config = Config.load()
    output_fn = config.output.output

    #process_afvoer_chloride(fn_path, output_fn)
    process_aanvoer_chloride(fn_path, output_fn)
