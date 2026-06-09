from config import Config
import glob
from pathlib import Path
import pandas as pd
import numpy as np
import os

from utils import convert_datetime, convert_m3_to_mil_m3


def format_value(x):
    if x == 0 or x == 0.0:
        return "0"
    return str(x)


def process_afvoer_inlaat(fn_path: str | Path, output_fn: str | Path, balance: bool, inlaat_df: pd.DataFrame = None):
    """Get the inlaat volume (balans:in Q in miljoen m3/dag per inlaat, wb: in m3)
    Args:
        fn_path (str): file path to the inlaat time series in XYZ per day
        output_fn (str | Path): file path to where to store the output file
        balance (bool): Whether to save the inlaat per waterboards or for the final balance
        inlaat_df (pd.DataFrame): list of inlaat for balance calculation

    Returns
    -------
        afvoer_inlaat_df: aanvoer per inlaat Q in miljoen m3 per dag
    """
    if balance:
        # read params inlaats
        for idx, row in inlaat_df.iterrows():
            name = row["Inlaat"]
            wb = row["WB"]
            balance = True
            for dir in glob.glob(f"{fn_path}/*"):
                for file in os.listdir(dir):
                    filename = os.fsdecode(file)
                    if ("Inlaat") in filename:                          
                        with open(os.path.join(dir, file), 'r') as f:
                            first_line = f.readline()
                            if ";" in first_line:
                                sep = ";"
                            else:
                                sep = ","
                                
                        inlaat_timeseries_df = pd.read_csv(os.path.join(dir,file), sep=sep)
            
            inlaat_df = pd.DataFrame(data = {"DATUM": inlaat_timeseries_df["time"], "WAARDE": inlaat_timeseries_df[" volume"]})
            inlaat_df = convert_datetime(inlaat_df, balance, sep)
            folder = output_fn / "in" / "inlaat_balance_input"
            os.makedirs(folder, exist_ok=True)
                
            output = folder / f"inlaat_{name}_wb{wb}.VZM"

            with open(output, "w") as f:
                f.write(f"{name} inlaat WB{wb}\n")
                f.write(f"* {name} inlaat\n")
                f.write("* Q in miljoen m3 per dag\n")
                f.write("* period 2010 t/m 2018\n")
                f.write(f"* {output}\n")
                f.write("* gap-filled TS\n")
                f.write("*DATUM WAARDE\n")
                inlaat_df.to_csv(f, sep=" ", index=False, header=False)
                
            
    else:
        for file in glob.glob(f"{fn_path}/*"):
            if file.endswith(".csv"):
                fn = Path(file)
                name = fn.stem.split("inlaat_")[-1]
                inlaat_timeseries_df = pd.read_csv(file, sep=";")

                for idx, row in inlaat_timeseries_df.iterrows():
                    # Convert gaps to 0 values
                    if (
                        row["WAARDE"] == 0
                        and idx > 0
                        and idx < (len(inlaat_timeseries_df) - 1)
                    ):
                        inlaat_timeseries_df.loc[idx, "WAARDE"] = np.nan

                aanvoer_per_inlaat_df = inlaat_timeseries_df

                # Save .VZM input file
                output = output_fn / "in" / f"VZM_inlaat_{name}_m3.csv"

                with open(output, "w", newline="") as f:
                    f.write("# Waarnemingssoort,begindatum,begintijd,tijdstap in minuten\n")
                    f.write(f"# inlaat_{name} (m3)\n")
                    f.write("Q 2010-01-01 12:00 1440\n")
                    aanvoer_per_inlaat_df["WAARDE"].to_csv(
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


def process_inlaat(fn_path: str | Path, balance: bool):
    """Processes afvoer from inlaat
    Args:
        balance (bool): Whether to save the inlaat per waterboards or for the final balance
        fn_path (str: Path): file path to the inlaat time series in Q in miljoen m3 per day
    """
    config = Config.load()
    output_fn = config.output.output
    inlaat_df = pd.read_csv(config.timeseries.inlaats_wb_out,sep=";")

    process_afvoer_inlaat(fn_path, output_fn, balance, inlaat_df)
