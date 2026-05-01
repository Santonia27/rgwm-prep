from datetime import datetime
import pandas as pd
from pathlib import Path
from waterboards import get_wb_params, seasons


def process_flushing(
    fn_path: str | Path, output_fn: str | Path, inlaat_measurements: str = None
):
    """Prepare the total flushing in miljoen m3 depending on the season and water board. This calculation is based on a model and not measured in on of the waterboards.
    This may be different in your case.


    Args:
        fn_path (str): file path to the water boards parameters
        output_fn (str | Path): file path to where to store the output file
        inlaat_measurements (str) | None: file path to timeseries of inlaat measurements in m3. All waterboards in one file.
    Returns
    -------
        total_flushing: VZM total flushing volume miljoen m3 per dag
        wb_params_dict: dict with all waterboards parameters
    """
    wb_params_dict = get_wb_params(Path(fn_path) / "wb_params.csv")
    timeseries = pd.read_csv(Path(fn_path) / "date_timeseries.csv")

    # Create empty df with time series dates
    wb_flushings_df = timeseries
    flushing_df = timeseries

    # Calculate flushing per sub-area per waterboard per day
    for waterboard in wb_params_dict:
        area = wb_params_dict[waterboard]["area_in_ha"]
        summer_flushing = wb_params_dict[waterboard]["summer_flush_6_months"]
        winter_flushing = wb_params_dict[waterboard]["winter_flush_6_months"]
        days = wb_params_dict[waterboard]["days"]

        # Create zero series

        flushing_df["FLUSHING"] = pd.Series([0.0] * len(timeseries))
        for idx, row in flushing_df.iterrows():
            # Calculate flushing based on season
            date_object = datetime.strptime(row["DATUM"], "%d-%m-%Y").date()
            if date_object.strftime("%B") in seasons.summer_months:
                flushing = (
                    10 * summer_flushing * area / days
                ) / 1000000  # Calculation from Excel water boards
            elif date_object.strftime("%B") in seasons.winter_months:
                flushing = (
                    winter_flushing / 1000000
                )  # Calculation from Excel water boards
            else:
                break
            flushing_df.loc[idx, "FLUSHING"] = flushing

        wb_flushings_df[waterboard] = flushing_df["FLUSHING"]

    # aggregate flushing from all sub-areas in the waterboard
    if inlaat_measurements:
        total_flushing = (
            inlaat_measurements / 1000000
        )  # NOTE! This may need adaptation if measurements are available
    else:
        wb_flushings_df["sum"] = wb_flushings_df.sum(axis=1, numeric_only=True)

    for idx, row in wb_flushings_df.iterrows():
        # Adjust datetime format
        rev_date_object = date_object.strftime("%Y-%m-%d")
        new_date = str(rev_date_object).replace("-", "")
        wb_flushings_df.loc[idx, "DATUM"] = new_date

    # Save .VZM input file
    output = output_fn / "VZM_inlaat_flushings.VZM"

    with open(output, "w") as f:
        f.write("Afvoer Inlaat doorspoeling WBs\n")
        f.write("* VZM Afvoer Inlaat doorspoeling all WBs in miljoen m3\n")
        f.write("* period 2010 t/m 2018\n")
        f.write("*DATUM WAARDE\n")
        wb_flushings_df[["DATUM", "sum"]].to_csv(f, sep=" ", index=False, header=False)
