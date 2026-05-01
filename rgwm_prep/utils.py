import pandas as pd
from datetime import datetime

def get_wb_params(fn_path: str):
    """Get waterboard parameters
    Args:
        fn_path (str): file path to the water boards parameters
    Returns
    -------
        wb_params_dict: dict with all waterboards parameters
    """
    wb_params_df = pd.read_csv(fn_path, sep=";")
    wb_params_dict = {}
    for idx, row in wb_params_df.iterrows():
        wb = row["waterboard"]
        # Create dict with all waterboard params
        wb_dict = row
        wb_params_dict[wb] = wb_dict

    return wb_params_dict

def convert_datetime(parameter_df: pd.DataFrame) -> pd.DataFrame: 
    """Convert the excel datetime format to the required format for the RGWM tool
    Args:
        parameter_df (pd.DataFrame): Dataframe of the parameter including the "DATUM" (date) and "WAARDE" (param value) column
    Returns
    -------
        parameter_df (pd.DataFrame): Dataframe of the parameter with the updated format for the "DATUM" (date) column
    """
    for idx, row in parameter_df.iterrows():
        # Adjust datetime format
        date_object = datetime.strptime(row["DATUM"], "%d-%m-%Y").date()
        rev_date_object = date_object.strftime("%Y-%m-%d")
        new_date = str(rev_date_object).replace("-", "")
        parameter_df.loc[idx, "DATUM"] = new_date
    
    return parameter_df

def convert_m3_to_mil_m3(parameter_df: pd.DataFrame) -> pd.DataFrame: 
    """Converts the volume in m3 to miljoes m3
    Args:
        parameter_df (pd.DataFrame): Dataframe of the parameter including the "DATUM" (date) and "WAARDE" (param value) column
    Returns
    -------
        parameter_df (pd.DataFrame): Dataframe of the parameter with value in miljoes m3 in "WAARDE" column
    """
    # Convert m3 to miljoen m3
    for idx, row in parameter_df.iterrows():
                new_volume = row["WAARDE"] / 1000000
                parameter_df.loc[idx, "WAARDE"] = round(new_volume, 4)
    
    return parameter_df