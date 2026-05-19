# Load packages
from config import Config
import glob
from pathlib import Path
import pandas as pd
from utils import convert_datetime

## Precipitation
# NOTE! Precipitation must be adjusted to the sub-area and an average is taken from all stations/sub-areas


def process_precipitation(
    fn_path: str | Path, output_fn: str | Path, total_area: int = 6000, balance=False
):
    """Get the precipitation per station and calculate average daily precipitation for the VZM in XY. #NOTE STILL writ here
        VZM sub-areas include the following stations:
            sub-area 1 stations: 447, 450, 744, 837. Area-factor: 6217 #NOTE! Not sure if this is area or something else
            sub-area 2 stations: 744, 757, 837. Area-factor: 882 #NOTE! Not sure if this is area or something else
            sub-area 3 stations: 832. Area-factor: 1122 #NOTE! Not sure if this is area or something else
            sub-area 4 stations: 750, 839. Area-factor: 96 #NOTE! Not sure if this is area or something else
    Args:
        fn_path (str | Path): file path to the precipitation time series files per station in mm per day
        output_fn (str | Path): file path to where to store the output file
        total_area (int): total area of VZM in ha. Default set to 6000 ha
        balance (boolean): If True write output in Balance format. If false write output in gap-fill/model format,. Default is set to False.

    Returns
    -------
        total_prec: sub-area averaged daily precipitation volume for total VZM in miljoen m3
    """

    stations_dict = {}
    for file in glob.glob(f"{fn_path}/*"):
        if file.endswith(".csv") and "precipitation" in file:
            fn = Path(file)
            name = fn.stem.split("station")[-1]
            station_timeseries = pd.read_csv(file, sep=";")
            stations_dict[name] = station_timeseries

    if balance is True:
        # Calculate average precipitation per sub-area
        sa1 = 6217 * (
            (
                stations_dict["447"]["WAARDE"]
                + stations_dict["450"]["WAARDE"]
                + stations_dict["744"]["WAARDE"]
                + stations_dict["837"]["WAARDE"]
            )
            / 4
        )
        sa2 = (
            882
            * (
                stations_dict["744"]["WAARDE"]
                + stations_dict["757"]["WAARDE"]
                + stations_dict["837"]["WAARDE"]
            )
            / 3
        )
        sa3 = 1122 * (stations_dict["832"]["WAARDE"])
        sa4 = 96 * (stations_dict["750"]["WAARDE"] + stations_dict["839"]["WAARDE"]) / 2

        total_prec = round((sa1 + sa2 + sa3 + sa4) / (6217 + 882 + 1122 + 96), 3)
        total_prec_df = pd.DataFrame(
            {"DATUM": stations_dict["447"]["DATUM"], "WAARDE": total_prec}
        )
        total_prec_df = total_prec_df.dropna()

        # Convert datetime format
        total_prec_df = convert_datetime(total_prec_df)

        # Adjust format to model input
        for idx, row in total_prec_df.iterrows():
            # Convert mm/d to miljoen m3
            volume = total_area * row["WAARDE"] * 0.00001
            total_prec_df.loc[idx, "WAARDE"] = round(volume, 4)

        # Save .VZM input file
        output = output_fn / "in" / "VZM_total_precipitation_milm3.VZM"

        with open(output, "w") as f:
            f.write("Neerslag\n")
            f.write("* VZM neerslag in miljoen m3\n")
            f.write("* KNMI te De Built. gew. gem. neerslagsom VZM lokaties\n")
            f.write("* neerslag in miljoen m3\n")
            f.write("* period 2010 t/m 2018\n")
            f.write("* VZM_total_precipitation.VZM\n")
            f.write("*DATUM WAARDE\n")
            total_prec_df.to_csv(f, sep="\t", index=False, header=False)
    else:
        # Convert datetime format
        for station_df_entry in stations_dict:
            station_df = stations_dict[station_df_entry]

            # Save .VZM input file
            output = output_fn / "in" / f"VZM_{station_df_entry}_precipitation_mm.csv"

            with open(output, "w", newline="") as f:
                f.write("# Waarnemingssoort,begindatum,begintijd,tijdstap in minuten\n")
                f.write(f"# neerslag_{output.stem} (mm)\n")
                f.write("H 2010-01-01 12:00 1440\n")
                station_df["WAARDE"].to_csv(f, sep=",", index=False, header=False)


## Evaporation
def process_evaporation(
    fn_path: str | Path, output_fn: str | Path, total_area: int = 6000, balance=False
):
    """Get the evaporation per station and calculate the open water evaporation using factor 1.25
        VZM include the following stations:
            area 1 stations: 310
    Args:
        fn_path (str | Path): file path to the evaporation time series files per station in mm per day
        output_fn (str | Path): file path to where to store the output file
        total_area (int): total area of VZM in ha. Default set to 6000 ha
        balance (boolean): If True write output in Balance format. If false write output in gap-fill/model format,. Default is set to False.

    Returns
    -------
        ow_evap: evaporation for total VZM in miljoen m3 or mm
    """

    stations_dict = {}

    for file in glob.glob(f"{fn_path}/*"):
        if file.endswith(".csv") and "evaporation" in file:
            fn = Path(file)
            name = fn.stem.split("station")[-1]
            station_timeseries = pd.read_csv(file, sep=";")
            stations_dict[name] = station_timeseries

    # Calculate open water evaporation
    ow_evap_df = pd.DataFrame(
        {
            "DATUM": stations_dict["310"]["DATUM"],
            "WAARDE": stations_dict["310"]["WAARDE"],
        }
    )
    ow_evap_df = ow_evap_df.dropna()

    if balance:
        # Convert datetime format
        ow_evap_df = convert_datetime(ow_evap_df)

        for idx, row in ow_evap_df.iterrows():
            # Convert mm/d to miljoen m3
            volume = total_area * row["WAARDE"] * 0.00001
            ow_evap_df.loc[idx, "WAARDE"] = round(volume, 4)

        # Save .VZM input file
        output = output_fn / "out" / "VZM_ow_evaporation_milm3.VZM"

        with open(output, "w") as f:
            f.write("Verdamping\n")
            f.write("* VZM verdamping in miljoen m3\n")
            f.write("* KNMI te De Built. gew. gem. verdmaping VZM lokaties\n")
            f.write("* verdamping in miljoen m3\n")
            f.write("* period 2010 t/m 2018\n")
            f.write("* VZM_ow_evaporation.VZM\n")
            f.write("*DATUM WAARDE\n")
            ow_evap_df.to_csv(f, sep="\t", index=False, header=False)
    else:
        # Save .VZM input file
        output = output_fn / "out" / "VZM_ow_evaporation_mm.csv"
        with open(output, "w", newline="") as f:
            f.write("# Waarnemingssoort,begindatum,begintijd,tijdstap in minuten\n")
            f.write("# E_Makkink (mm)\n")
            f.write("H 2010-01-01 12:00 1440\n")
            ow_evap_df["WAARDE"].to_csv(f, sep=",", index=False, header=False)


def process_meteo(fn_path: str, total_area: int = 6000, balance=False):
    """Processes precipitation and evaporation from the VZM stations.
    Args:
        fn_path (str | Path): file path to the meteo time series files per station in mm per day
        total_area (int): total area of VZM in ha. Default set to 6000 ha
        balance (boolean): If True write output in Balance format. If false write output in gap-fill/model format,. Default is set to False.
    """
    config = Config.load()
    output_fn = config.output.output
    process_precipitation(fn_path, output_fn, total_area, balance)
    process_evaporation(fn_path, output_fn, total_area, balance)
