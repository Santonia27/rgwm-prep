from config import Config
import glob
from pathlib import Path
import pandas as pd
from datetime import datetime
from utils import convert_datetime, convert_m3_to_mil_m3


## Afvoer
def process_aanvoer_discharge(fn_path: str | Path, output_fn: str | Path):
    """Get the aanvoer discharge per sluis in Q in miljoen m3 per dag
        VZM include the following afvoer sluises:
        Volkerak spuisluizen gat 2 + gat 3
            - Volkerak spuisluizen gat 2 + gat 3
            - Dintelsas
            - Bovensas 10 % percentage extra op Bovensas afvoer

    Args:
        fn_path (str | Path): file path to the aanvoer discharge time series per sluises in m3 per day
        output_fn (str | Path): file path to where to store the output file

    Returns
    -------
        aanvoer_per_sluis_df: aanvoer discharge per sluis in Q in miljoen m3 per dag
    """
    for file in glob.glob(f"{fn_path}/*"):
        if file.endswith(".csv") and "IN" in file:
            fn = Path(file)
            name = fn.stem.split("discharge_")[-1]
            discharge_timeseries_df = pd.read_csv(file, sep=";")
            discharge_timeseries_df["WAARDE"] = discharge_timeseries_df[
                "WAARDE"
            ].astype(float)

            # Add 10 % to Bovensas
            if "Bovensas" in name:
                discharge_timeseries_df["WAARDE"] * 1.10

            discharge_timeseries_df = convert_datetime(discharge_timeseries_df)
            discharge_timeseries_df = convert_m3_to_mil_m3(discharge_timeseries_df)

            aanvoer_per_sluis_df = discharge_timeseries_df

            # Save .VZM input file
            output = output_fn / f"VZM_{name}_IN_discharge.VZM"

            with open(output, "w") as f:
                f.write(f"{name}\n")
                f.write("* Q in miljoen m3 per dag\n")
                f.write("* period 2010 t/m 2018\n")
                f.write("*DATUM WAARDE\n")
                aanvoer_per_sluis_df.to_csv(f, sep=" ", index=False, header=False)


def process_afvoer_discharge(fn_path: str | Path, output_fn: str | Path):
    """Get the afvoer discharge per sluis in Q in miljoen m3 per dag
        VZM include the following afvoer sluises:
            - Bathse spuisluis gecorrigeerd
            - Krammer
            - Kreekrak
    Args:
        fn_path (str | Path): file path to the afvoer discharge time series per sluises in m3 per day
        output_fn (str | Path): file path to where to store the output file

    Returns
    -------
        afvoer_per_sluis_df: avfoer discharge per sluis in Q in miljoen m3 per dag
    """
    for file in glob.glob(f"{fn_path}/*"):
        if file.endswith(".csv") and "OUT" in file:
            fn = Path(file)
            name = fn.stem.split("discharge_")[-1]
            discharge_timeseries_df = pd.read_csv(file, sep=";")
            discharge_timeseries_df["WAARDE"] = discharge_timeseries_df[
                "WAARDE"
            ].astype(float)

            for idx, row in discharge_timeseries_df.iterrows():
                # Adjust datetime format
                date_object = datetime.strptime(row["DATUM"], "%d-%m-%Y").date()
                rev_date_object = date_object.strftime("%Y-%m-%d")
                new_date = str(rev_date_object).replace("-", "")
                discharge_timeseries_df.loc[idx, "DATUM"] = new_date
                # Convert m3 to miljoen m3
                new_volume = row["WAARDE"] / 1000000
                discharge_timeseries_df.loc[idx, "WAARDE"] = round(new_volume, 4)

            afvoer_per_sluis_df = discharge_timeseries_df

            # Save .VZM input file
            output = output_fn / f"VZM_{name}_OUT_discharge.VZM"

            with open(output, "w") as f:
                f.write(f"{name}\n")
                f.write("* Q in miljoen m3 per dag\n")
                f.write("* period 2010 t/m 2018\n")
                f.write("*DATUM WAARDE\n")
                afvoer_per_sluis_df.to_csv(f, sep=" ", index=False, header=False)


def process_discharge(fn_path: str | Path):
    """Processes afvoer and aanvoer from the VZM sluises
    Args:
        fn_path (str | Path): file path to the discharge time series per sluises in m3 per day
    """
    config = Config.load()
    output_fn = config.output.output

    process_afvoer_discharge(fn_path, output_fn)
    process_aanvoer_discharge(fn_path, output_fn)
