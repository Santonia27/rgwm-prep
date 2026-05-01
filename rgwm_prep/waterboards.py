import pandas as pd


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


class seasons:
    summer_months: list = ["April", "May", "June", "July", "August", "September"]
    winter_months: list = [
        "October",
        "November",
        "December",
        "January",
        "February",
        "March",
    ]
