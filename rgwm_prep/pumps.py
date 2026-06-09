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


def process_aanvoer_pump(fn_path: str | Path, output_fn: str | Path, balance: bool, pumps_df: pd.DataFrame = None):
    """Get the pump volume (balans:in Q in miljoen m3/dag per pump, wb: in m3)
    Args:
        fn_path (str): file path to the pump time series in XYZ per day
        output_fn (str | Path): file path to where to store the output file
        balance (bool): Whether to save the pump per waterboards or for the final balance
        pumps_df (pd.DataFrame): list of pumps for balance calculation

    Returns
    -------
        aanvoer_per_pump_df: aanvoer per pump in Q in miljoen m3 per dag
    """
    if balance:
        # read params pumps
        for idx, row in pumps_df.iterrows():
            name = row["Gemaal"]
            wb = row["WB"]
            balance = True
            for dir in glob.glob(f"{fn_path}/*"):
                for file in os.listdir(dir):
                    filename = os.fsdecode(file)
                    if (name + "_bemaling") in filename:                          
                        with open(os.path.join(dir, file), 'r') as f:
                            first_line = f.readline()
                            if ";" in first_line:
                                sep = ";"
                            else:
                                sep = ","
                                
                        pump_timeseries_df = pd.read_csv(os.path.join(dir,file), sep=sep)
            
            gemaal_df = pd.DataFrame(data = {"DATUM": pump_timeseries_df["time"], "WAARDE": pump_timeseries_df[" volume"]})
            gemaal_df = convert_datetime(gemaal_df, balance, sep)
            folder = output_fn / "in" / "pump_balance_input"
            os.makedirs(folder, exist_ok=True)
                
            output = folder / f"Gemaal_{name}_wb{wb}.VZM"

            with open(output, "w") as f:
                f.write(f"{name} Gemaal WB{wb}\n")
                f.write(f"* {name} Gemaal\n")
                f.write("* Q in miljoen m3 per dag\n")
                f.write("* period 2010 t/m 2018\n")
                f.write(f"* {output}\n")
                f.write("* gap-filled TS\n")
                f.write("*DATUM WAARDE\n")
                gemaal_df.to_csv(f, sep=" ", index=False, header=False)
                
            
    else:
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

                aanvoer_per_pump_df = pump_timeseries_df

                # Save .VZM input file
                folder = output_fn / "in" / "pump_wb_input"
                os.makedirs(folder, exist_ok=True)
                output = folder  / f"VZM_Gemaal_{name}_m3.csv"

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


def process_pumps(fn_path: str | Path, balance: bool):
    """Processes afvoer and aanvoer from the VZM pumps
    Args:
        balance (bool): Whether to save the pump per waterboards or for the final balance
        fn_path (str: Path): file path to the pump time series in Q in miljoen m3 per day
    """
    config = Config.load()
    output_fn = config.output.output
    pumps_df = pd.read_csv(config.timeseries.pumps_wb_out,sep=";")

    process_aanvoer_pump(fn_path, output_fn, balance, pumps_df)
