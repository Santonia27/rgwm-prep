from config import Config
import glob
from pathlib import Path
import pandas as pd
from utils import convert_datetime
import os
## Afvoer

def get_sluis_value(fn_path: Path | str, idx: int, sluis: str):
    for dir in glob.glob(f"{fn_path}/*"):
            for file in os.listdir(dir):
                filename = os.fsdecode(file)
                if ("Chloride") not in filename and sluis in filename and "png" not in filename:          
                    with open(os.path.join(dir, file), 'r') as f:
                        first_line = f.readline()
                        if ";" in first_line:
                            sep = ";"
                        else:
                            sep = ","
                            
                    sluise_timeseries_df = pd.read_csv(os.path.join(dir,file), sep=sep)
                    value =  sluise_timeseries_df.loc[idx, " discharge"]
                    return value
    

def calculate_sum_boven_onder(folder: str | Path):
    dict_boven_onder = {}
    for file in glob.glob(f"{folder}/*"):
        fn = Path(file)
        if "onder" in str(fn):
            location= "onder"
        else:
            location = "boven"
            
        name = fn.stem.split(f"_{location}")[0]
        if name in dict_boven_onder.keys():
            df = pd.read_csv(fn)
            sum_df = pd.DataFrame(data = {"df1": dict_boven_onder[name][0]["score"], "df2": df.iloc[2:,0]})
            sum_df["row_sum"] = sum_df.sum(axis =1)
            
            output = folder / f"{name}_sum.csv"
            with open(output, "w", newline="") as f:
                f.write("# Waarnemingssoort,begindatum,begintijd,tijdstap in minuten\n")
                f.write(f"# {name} (mg/l)\n")
                f.write("Q 2010-01-01 12:00 1440\n")
                sum_df["row_sum"].to_csv(
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
        else:
            df = pd.read_csv(fn)
            dict_boven_onder[name] = [pd.DataFrame(data = {"index": df.index[2:], "score": df.iloc[2:,0]})]        
            
    
def process_aanvoer_chloride(fn_path: str | Path, output_fn: str | Path, balance: bool):
    """Get the aanvoer chloride
    Args:
        fn_path (str | Path): file path to the aanvoer chloride time series per sluises in m3 per day
        output_fn (str | Path): file path to where to store the output file

    Returns
    -------
        aanvoer_df: aanvoer chloride
    """
    if balance:
        # read params pumps
        for dir in glob.glob(f"{fn_path}/*"):
            for file in os.listdir(dir):
                filename = os.fsdecode(file)
                if ("Chloride") in filename and "IN" in filename:
                    if "sluis" in filename:
                        type = "debieten"
                    else:
                        type = "gemaal"
                    name = filename.split("Chloride_")[-1].split(".wb")[0]
                    wb =  filename.split(".wb")[-1].split(".csv")[0]        
                    with open(os.path.join(dir, file), 'r') as f:
                        first_line = f.readline()
                        if ";" in first_line:
                            sep = ";"
                        else:
                            sep = ","
                            
                    cl_timeseries_df = pd.read_csv(os.path.join(dir,file), sep=sep)
        
                    cl_df = pd.DataFrame(data = {"DATUM": cl_timeseries_df["time"], "WAARDE": cl_timeseries_df[" salinity"]})
                    cl_df = convert_datetime(cl_df, balance, sep)
                    if type == "debieten":
                        cl_df["WAARDE"] = cl_df["WAARDE"]/1000000
                    
                    # Kreekrak has different calculation. If Sluis > 0, value = 0
                    if "Kreekrak" in name:
                        for idx, row in cl_df.iterrows():
                            value = get_sluis_value(fn_path, idx, name.split("_IN")[0])
                            if value > 0:
                                value = 0
                            else:
                                value = cl_df.loc[idx, "WAARDE"] 
                                if value < 0:
                                    value = value * -1
                                
                            cl_df.loc[idx, "WAARDE"] = value
                    
                    folder = output_fn / "in" / "cl_balance_input"
                    os.makedirs(folder, exist_ok=True)
                        
                    output = folder / f"Cl_{name}_wb{wb}.VZM"

                    with open(output, "w") as f:
                        f.write(f"{name}\n")
                        f.write(f"* {name} Cl {type}\n")
                        f.write("* Chloride in kilo tons\n")
                        f.write("* period 2010 t/m 2018\n")
                        f.write(f"* {output}\n")
                        f.write("* gap-filled TS\n")
                        f.write("*DATUM WAARDE\n")
                        cl_df.to_csv(f, sep=" ", index=False, header=False)       
    else:         
        for file in glob.glob(f"{fn_path}/*"):
            if file.endswith(".csv") and "IN" in file:
                fn = Path(file)
                name = fn.stem.split("cl_")[-1]
                if "gemaal" in name or "pump" in name:
                    type = "Gemaal"
                else:
                    type = "Debieten"
                    
                chloride_timeseries_df = pd.read_csv(file, sep=";")
                chloride_timeseries_df["WAARDE"] = chloride_timeseries_df[
                    "WAARDE"
                ].astype(float)

                # Convert datetime format
                chloride_timeseries_df = convert_datetime(chloride_timeseries_df)

                folder = output_fn / "in" / "cl_balance_input"
                os.makedirs(folder, exist_ok=True)
                    
                output = folder / f"cl_{name}.csv"

                with open(output, "w", newline="") as f:
                    f.write("# Waarnemingssoort,begindatum,begintijd,tijdstap in minuten\n")
                    f.write(f"# {type}_{name} (mg/l)\n")
                    f.write("Q 2010-01-01 12:00 1440\n")
                    chloride_timeseries_df["WAARDE"].to_csv(
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


def process_afvoer_chloride(fn_path: str | Path, output_fn: str | Path, balance: bool):
    """Get the aanvoer chloride
    Args:
        fn_path (str | Path): file path to the aanvoer chloride time series per sluises in m3 per day
        output_fn (str | Path): file path to where to store the output file

    Returns
    -------
        aanvoer_df: aanvoer chloride
    """
    if balance:
        # read params pumps
        for dir in glob.glob(f"{fn_path}/*"):
            for file in os.listdir(dir):
                filename = os.fsdecode(file)
                if ("Chloride") in filename and "OUT" in filename:
                    if "sluis" in filename:
                        type = "debieten"
                    else:
                        type = "gemaal"
                    name = filename.split("Chloride_")[-1].split(".wb")[0]                               
                    with open(os.path.join(dir, file), 'r') as f:
                        first_line = f.readline()
                        if ";" in first_line:
                            sep = ";"
                        else:
                            sep = ","
                            
                    cl_timeseries_df = pd.read_csv(os.path.join(dir,file), sep=sep)
        
                    cl_df = pd.DataFrame(data = {"DATUM": cl_timeseries_df["time"], "WAARDE": cl_timeseries_df[" salinity"]})
                    cl_df = convert_datetime(cl_df, balance, sep)
                    if type == "debieten":
                        cl_df["WAARDE"] = cl_df["WAARDE"]/1000000000
                    
                    # Bovensas and Dintelsas have different calculation. If Sluis > 0, value = 0
                    if "Bovensas" in name or "Dintelsas" in name:
                        for idx, row in cl_df.iterrows():
                            value = get_sluis_value(fn_path, idx, name.split("_OUT")[0])
                            if value > 0:
                                value = 0
                            else:
                                value = cl_df.loc[idx, "WAARDE"] 
                                if value < 0:
                                    value = value * -1
                                
                            cl_df.loc[idx, "WAARDE"] = value
                        
                    folder = output_fn / "out" / "cl_balance_input"
                    os.makedirs(folder, exist_ok=True)
                        
                    output = folder / f"Cl_{name}.VZM"

                    with open(output, "w") as f:
                        f.write(f"{name}\n")
                        f.write(f"* {name} Cl {type}\n")
                        f.write("* Chloride in kilo tons\n")
                        f.write("* period 2010 t/m 2018\n")
                        f.write(f"* {output}\n")
                        f.write("* gap-filled TS\n")
                        f.write("*DATUM WAARDE\n")
                        cl_df.to_csv(f, sep=" ", index=False, header=False) 
    else:
        for file in glob.glob(f"{fn_path}/*"):
            if file.endswith(".csv") and "OUT" in file:
                fn = Path(file)
                name = fn.stem.split("cl_")[-1]
                if "gemaal" in name or "pump" in name:
                    type = "Gemaal"
                else:
                    type = "Debieten"
                chloride_timeseries_df = pd.read_csv(file, sep=";")
                chloride_timeseries_df["WAARDE"] = chloride_timeseries_df[
                    "WAARDE"
                ].astype(float)

                folder = output_fn / "out" / "cl_balance_input"
                os.makedirs(folder, exist_ok=True)
                    
                output = folder / f"cl_{name}.csv"

                with open(output, "w", newline="") as f:
                    f.write("# Waarnemingssoort,begindatum,begintijd,tijdstap in minuten\n")
                    f.write(f"# Cl_{name} (mg/l)\n")
                    f.write("Q 2010-01-01 12:00 1440\n")
                    chloride_timeseries_df["WAARDE"].to_csv(
                        f, sep=" ", index=False, header=False, float_format="%.10g"
                    )
                    
                calculate_sum_boven_onder(folder)  

    


def process_chloride(fn_path: str | Path, balance: bool):
    """Processes afvoer and aanvoer from the VZM sluises
    Args:
        fn_path (str | Path): file path to the chloride time series per sluises in m3 per day
    """
    config = Config.load()
    output_fn = config.output.output

    #process_afvoer_chloride(fn_path, output_fn, balance)
    process_aanvoer_chloride(fn_path, output_fn, balance)
