# Date: 29-04-2026
# Written by: Sarah Rautenbach, Deltares
# Function: Converts the csv input files to .mmr input files for the RGWM model
# --------------------------------------------------------------------------------
from config import Config
from meteo import process_meteo
from pumps import process_pumps


# Run script
if __name__ == "__main__":
    config = Config.load()

    # Prepare meteo model inputs
    #process_meteo(config.timeseries.meteo, balance = True)

    # Prepare discharge model inputs
    # process_discharge(config.timeseries.discharge)

    # Prepare Pumps
    process_pumps(config.timeseries.pumps, balance = False)

    # Prepare flushing
    ## can add inlaat measurements if available
    # process_flushing(config.timeseries.params)

    # Prepare constant fluxes
    # process_const_fluxes(
    #    config.const_fluxes.leakage,
    #    config.const_fluxes.lock_operations,
    #    config.const_fluxes.up_grndwater_flux, config.timeseries.params
    # )
    # Prepare Berging
    print("All input files were created.")
