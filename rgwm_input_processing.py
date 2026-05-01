# Date: 29-04-2026
# Written by: Sarah Rautenbach, Deltares
# Function: Converts the csv input files to .mmr input files for the RGWM model
# --------------------------------------------------------------------------------

from discharges import process_discharge
from flushing import process_flushing
from meteo import process_meteo
from pumps import process_pumps

# Run script
if __name__ == "__main__":
    # Prepare meteo model inputs
    process_meteo(
        r"P:\11212800-002\2. Calculations\reproduction_volkerak_2018\input\meteo"
    )

    # Prepare discharge model inputs
    process_discharge(
        r"P:\11212800-002\2. Calculations\reproduction_volkerak_2018\input\discharge"
    )

    # Prepare Pumps
    process_pumps(
        r"P:\11212800-002\2. Calculations\reproduction_volkerak_2018\input\pumps"
    )  # NOTE - wait what time series we can get whether need to calculation or not
    # NOTE For now take the final sum of excel to validate model

    # Prepare flushing
    process_flushing(
        r"P:\11212800-002\2. Calculations\reproduction_volkerak_2018\input\waterboards"
    )  # can add inlaat measurements if available

    # Prepare Berging
    print("All input files were created.")
