# Load packages 
import glob
from pathlib import Path
import pandas as pd
from datetime import datetime

## Precipitation
#NOTE! Precipitation must be adjusted to the sub-area and an average is taken from all stations/sub-areas

def process_precipitation(fn_path: str, total_area: int = 6000): 
    """Get the precipitation per station and calculate average daily precipitation for the VZM in XY. #NOTE STILL writ here
        VZM sub-areas include the following stations:
            sub-area 1 stations: 447, 450, 744, 837. Area-factor: 6217 #NOTE! Not sure if this is area or someting else
            sub-area 2 stations: 744, 757, 837. Area-factor: 882 #NOTE! Not sure if this is area or someting else
            sub-area 3 stations: 832. Area-factor: 1122 #NOTE! Not sure if this is area or someting else
            sub-area 4 stations: 750, 839. Area-factor: 96 #NOTE! Not sure if this is area or someting else
    Args:
        fn_path (str): file path to the precipitation time series files per station in mm per day
        total_area (int): total area of VZM in ha. Default set to 6000 ha

    Returns
    -------
        total_prec: sub-area averaged daily precipitation volume for total VZM in miljoen m3
    """ 
    stations_dict = {}
    for file in glob.glob(f"{fn_path}/*"):    
        if file.endswith(".csv") and 'precipitation' in file:
            fn = Path(file)
            name = fn.stem.split("station")[-1]
            station_timeseries = pd.read_csv(file, sep = ";")
            stations_dict[name] = station_timeseries
    # Calculate average precipitation per sub-area
    sa1 = 6217*((stations_dict["447"]["WAARDE"] + stations_dict["450"]["WAARDE"] + stations_dict["744"]["WAARDE"] + stations_dict["837"]["WAARDE"])/4)
    sa2 = 882*(stations_dict["744"]["WAARDE"] + stations_dict["757"]["WAARDE"] + stations_dict["837"]["WAARDE"])/3
    sa3 = 1122*(stations_dict["832"]["WAARDE"])
    sa4 = 96*(stations_dict["750"]["WAARDE"] + stations_dict["839"]["WAARDE"])/2

    total_prec = round((sa1 + sa2 + sa3 + sa4)/(6217+882+1122+96),3)
    total_prec_df = pd.DataFrame({"DATUM": stations_dict["447"]["DATUM"], "WAARDE": total_prec})
    total_prec_df = total_prec_df.dropna()
 
    # Adjust format to model input
    for idx, row in total_prec_df.iterrows():
    # Adjust datetime format
        date_object = datetime.strptime(row["DATUM"], '%d-%m-%Y').date()
        rev_date_object = date_object.strftime('%Y-%m-%d')
        new_date = str(rev_date_object).replace("-", "")
        total_prec_df.loc[idx, "DATUM"] = new_date
    # Convert mm/d to miljoen m3
        volume = total_area * row["WAARDE"] * 0.00001
        total_prec_df.loc[idx, "WAARDE"] = round(volume,4)
    
    # Save .VZM input file
    output = "../../output/VZM_total_precipitation" + ".VZM"
    
    with open(output, "w") as f:
        f.write("Neerslag\n")
        f.write("* VZM neerslag in miljoen m3\n")
        f.write("* periode 2010 t/m 2018\n")
        f.write("*DATUM WAARDE\n")
        total_prec_df.to_csv(f, sep = " ", index = False, header = False)


## Evaporation
def process_evaporation(fn_path: str, total_area: int = 6000, ow_factor: float = 1.25): 
    """Get the evaporation per station and calculate the open water evaporation using factor 1.25
        VZM include the following stations:
            area 1 stations: 310
    Args:
        fn_path (str): file path to the evaporation time series files per station in mm per day
        total_area (int): total area of VZM in ha. Default set to 6000 ha
        ow_factor (float): Conversion factor from station evaporation to open water evaporation. Default set to 1.25

    Returns
    -------
        ow_evap: open water evaporation for total VZM in miljoen m3
    """ 
    stations_dict = {}
    
    for file in glob.glob(f"{fn_path}/*"):    
        if file.endswith(".csv") and 'evaporation' in file:
            fn = Path(file)
            name = fn.stem.split("station")[-1]
            station_timeseries = pd.read_csv(file, sep = ";")
            stations_dict[name] = station_timeseries
    
    # Calculate open water evaporation
    ow_evap = ow_factor*(stations_dict["310"]["WAARDE"])
    ow_evap_df = pd.DataFrame({"DATUM": stations_dict["310"]["DATUM"], "WAARDE": ow_evap})
    ow_evap_df = ow_evap_df.dropna()
    
    for idx, row in ow_evap_df.iterrows():
    # Adjust datetime format
        date_object = datetime.strptime(row["DATUM"], '%d-%m-%Y').date()
        rev_date_object = date_object.strftime('%Y-%m-%d')
        new_date = str(rev_date_object).replace("-", "")
        ow_evap_df.loc[idx, "DATUM"] = new_date
    # Convert mm/d to miljoen m3
        volume = total_area * row["WAARDE"] * 0.00001
        ow_evap_df.loc[idx, "WAARDE"] = round(volume,4)
        
    # Save .VZM input file
    output = "../../output/VZM_ow_evaporation" + ".VZM"
    
    with open(output, "w") as f:
        f.write("Verdamping\n")
        f.write("* VZM verdamping in miljoen m3 per dag\n")
        f.write("* periode 2010 t/m 2018\n")
        f.write("*DATUM WAARDE\n")
        ow_evap_df.to_csv(f, sep = " ", index = False, header = False)
        
def process_meteo(fn_path: str, total_area: int = 6000, ow_factor: float = 1.25): 
    """Processes precipitation and evaporation from the VZM stations. 
    Args:
        fn_path (str): file path to the meteo time series files per station in mm per day
        total_area (int): total area of VZM in ha. Default set to 6000 ha
        ow_factor (float): Conversion factor from station evaporation to open water evaporation. Default set to 1.25
    """ 
    process_precipitation(fn_path, total_area)
    process_evaporation(fn_path, total_area, ow_factor)