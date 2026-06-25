from config import Config
import glob
from pathlib import Path
import pandas as pd
import numpy as np
import os

from utils import convert_datetime

def format_value(x):
    if x == 0 or x == 0.0:
        return "0"
    return str(x)


def process_afvoer_inlaat(fn_path: str | Path, output_fn: str |Path, balance: bool):
    """Get the inlaat volume (balans:in Q in miljoen m3/dag per inlaat, wb: in m3)
    Args:
        fn_path (str): file path to the inlaat time series in XYZ per day
        output_fn (str | Path): file path to where to store the output file
        inlaat_df (pd.DataFrame): list of inlaat for balance calculation

    Returns
    -------
        afvoer_inlaat_df: aanvoer per inlaat Q in miljoen m3 per dag
    """
   
    # read params inlaats
    for dir in glob.glob(f"{fn_path}/*"):
        for file in os.listdir(dir):
            filename = os.fsdecode(file)
            name = "wb_" + dir.split("wb")[-1]
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
        folder = output_fn / "out" / "inlaat_balance_input"
        os.makedirs(folder, exist_ok=True)
            
        output = folder / f"Inlaat_{name}.VZM"

        with open(output, "w") as f:
            f.write(f"{name} inlaat {name} \n")
            f.write(f"* {name} inlaat\n")
            f.write("* Q in miljoen m3 per dag\n")
            f.write("* period 2010 t/m 2018\n")
            f.write(f"* {output}\n")
            f.write("* gap-filled TS\n")
            f.write("*DATUM WAARDE\n")
            inlaat_df.to_csv(f, sep=" ", index=False, header=False)
            
    # Sum Inlaat per WB --> used for Chloride concentration
    inlaat_dict = {"wb_1": [],"wb_2": [], "wb_5": [],"wb_6": []}  
    for file in os.listdir(folder):
        name = file.split(".VZM")[0].split("Inlaat_")[-1]
        name = name.split("_")[0] + "_" +  name.split("_")[1] 
 
        if "wb_4" not in name and "wb_3" not in name:
            inlaat_timeseries_df = pd.read_csv(os.path.join(folder,file), sep=" ", skiprows= 6)
            inlaat_dict[name].append(inlaat_timeseries_df)
            
    for key, value in inlaat_dict.items():
        df_combined = pd.concat(value, axis=1)
        df_combined["WAARDE_sum"] = df_combined.loc[:, df_combined.columns == "WAARDE"].sum(axis=1)
        inlaat_df["WAARDE"] = df_combined["WAARDE_sum"]
        
        output = folder / f"Inlaat_{key}_sum.VZM"

        with open(output, "w") as f:
            f.write(f"{key} inlaat {key} \n")
            f.write(f"* {key} inlaat\n")
            f.write("* Q in miljoen m3 per dag\n")
            f.write("* period 2010 t/m 2018\n")
            f.write(f"* {output}\n")
            f.write("* gap-filled TS\n")
            f.write("*DATUM WAARDE\n")
            inlaat_df.to_csv(f, sep=" ", index=False, header=False)
        

        
        
        
            
             


def process_inlaat(fn_path: str | Path, balance: bool):
    """Processes afvoer from inlaat. Since the Balanstool cannot gap-fill the inlaat, only the modelled inlaat as output from the waterboards is used. 
    Args:
        balance (bool): Whether to save the inlaat per waterboards or for the final balance
        fn_path (str: Path): file path to the inlaat time series in Q in miljoen m3 per day
    """
    #TODO find out if Doorspoelung is already added to the inlaat in rgwm
    
    config = Config.load()
    output_fn = config.output.output
    process_afvoer_inlaat(fn_path, output_fn, balance)
