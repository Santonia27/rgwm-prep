# Date: 29-04-2026
# Written by: Sarah Rautenbach, Deltares
# Function: Converts the csv input files to .mmr input files for the RGWM model
# --------------------------------------------------------------------------------
from config import Config
from pumps import process_pumps
from discharges import process_discharge
from constant_fluxes import process_const_fluxes
from inlaat import process_inlaat
from chloride import process_chloride


# Run script
if __name__ == "__main__":
    config = Config.load()
    balance = config.balance.balance
    
    # Prepare meteo model inputs
    # process_meteo(config.timeseries.meteo, balance = True)

    # Prepare discharge model inputs
    #process_discharge(config.timeseries.discharge, balance)

    # Prepare Pumps and Inlaat
    #if balance: 
        #process_pumps(config.timeseries.pumps_balance, balance)
    #    process_inlaat(config.timeseries.inlaat_balance)
    #else:
    #    process_pumps(config.timeseries.pumps_wb, balance)  
        

    # Prepare flushing relationsfile #NOTE here I could create a text snippet for the relationship yaml and eventually write the whole yaml
    ## can add inlaat measurements if available
    # process_flushing(config.timeseries.params)

    # Prepare constant fluxes
    #process_const_fluxes(
    #    config.const_fluxes.leakage,
    #    config.const_fluxes.lock_operations,
    #    config.const_fluxes.up_grndwater_flux, config.timeseries.params,
    #    balance
    # )
    
    # Prepare chloride 
    if balance: 
        process_chloride(config.timeseries.pumps_balance, balance)
    else:
        process_chloride(config.timeseries.chloride, balance)
    
    
    # Prepare Berging
    print("All input files were created.")
