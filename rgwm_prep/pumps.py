import glob
from pathlib import Path
import pandas as pd
from datetime import datetime

def process_aanvoer_pump(fn_path: str): 
    """Get the pump volume in Q in miljoen m3/dag per pump
        VZM include the following pump stations:
            - Bathse spuisluis gecorrigeerd
            - Krammer
            - Kreekrak
    Args:
        fn_path (str): file path to the pump time series in XYZ per day

    Returns
    -------
        aanvoer_per_pump_df: aanvoer per pump in Q in miljoen m3 per dag
    """         
    for file in glob.glob(f"{fn_path}/*"):    
        if file.endswith(".csv"):
            fn = Path(file)
            name = fn.stem.split("pump_")[-1]
            pump_timeseries_df = pd.read_csv(file, sep = ";")
            #pump_timeseries_df["WAARDE"] = discharge_timeseries_df["WAARDE"].astype(float)   
            
            for idx, row in pump_timeseries_df.iterrows():
            # Adjust datetime format
                date_object = datetime.strptime(row["DATUM"], '%d-%m-%Y').date()
                rev_date_object = date_object.strftime('%Y-%m-%d')
                new_date = str(rev_date_object).replace("-", "")
                pump_timeseries_df.loc[idx, "DATUM"] = new_date
            # Convert m3 to miljoen m3
            
            aanvoer_per_pump_df = pump_timeseries_df
            # Save .VZM input file
            output = f"../../output/VZM_{name}" + ".VZM"
            
            with open(output, "w") as f:
                f.write(f"{name}\n")
                f.write("* Q in miljoen m3 per dag\n")
                f.write("* periode 2010 t/m 2018\n")
                f.write("*DATUM WAARDE\n")
                aanvoer_per_pump_df.to_csv(f, sep = " ", index = False, header = False)    
    
def process_pumps(fn_path: str): 
    """Processes afvoer and aanvoer from the VZM pumps
    Args:
        fn_path (str): file path to the pump time series in Q in miljoen m3 per day
    """ 
    process_aanvoer_pump(fn_path)