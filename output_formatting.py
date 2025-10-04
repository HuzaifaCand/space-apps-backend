from data_fetching import *
from data_handling import *
from predict import *
import json
import pandas as pd

def get_predictions(df):
    """
    Runs prediction models on a DataFrame and returns a dictionary of prediction results 
    (probability, status, distribution) for each weather factor.
    ------
    Parameters:
        df: pd.DataFrame
            DataFrame containing weather data
    Returns:
        dict: Prediction results per factor
              {factor: {"Probability": float, "Status": str, "Distribution": dict}}
    """
    factor_functions = {
        "Precipitation": check_precipitation,
        "Temperature": check_temperature,
        "Wind_Speed": check_wind,
        "Relative_Humidity": check_humidity,
        "Heat_Index": check_heat_index
    }
    stats = {}
    for factor, func in factor_functions.items():
        prob, status, dist = func(df)
        stats[factor] = {
            "Probability": round(float(prob), 2),
            "Status": status,
            "Distribution": {k: round(float(v), 2) for k, v in dist.items()}
        }

    return stats


def get_column_statistics(data):
    """
    Calculates descriptive statistics for a pandas Series.
    ------
    Parameters:
        data: pd.Series
            Numeric data to calculate statistics for.
    Returns:
        dict: Summary statistics (mean, std, min, 25%, 50%, 75%, max, range)
    """
    if not isinstance(data, pd.Series):
        raise TypeError("Input must be a pandas Series")
    
    stats = data.describe().round(2).to_dict()
    stats["range"] = round(stats["max"] - stats["min"], 2)
    # Convert all to plain floats
    return {k: float(v) for k, v in stats.items()}


def get_dataframe_statistics(df):
    """
    Calculates descriptive statistics for a pandas DataFrame.
    ------
    Parameters:
        df: pd.DataFrame
            Numeric data to calculate statistics for.
    Returns:
        dict: Each numeric column maps to its summary statistics.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    
    return {col: get_column_statistics(df[col])
            for col in df.columns if pd.api.types.is_numeric_dtype(df[col])}


def get_final_statistics(vector_data):
    """
    Computes final statistics for a combined dataset.
    Includes descriptive statistics and prediction results.
    ------
    Parameters:
        vector_data: pd.DataFrame
            Combined weather data from all years
    Returns:
        dict: {
            "Statistics": {column: {mean, std, min, ..., range}},
            "Predictions": {factor: {Probability, Status, Distribution}}
        }
    """
    return {
        "Statistics": get_dataframe_statistics(vector_data),
        "Predictions": get_predictions(vector_data)
    }


def construct_json(full_df, yearly_data, full_stats, include_raw=False):
    """
    Returns two JSON strings: full dataset output and yearly dataset output.
    """
    full_output = {
        "Statistics": full_stats["Statistics"],
        "Predictions": full_stats["Predictions"],
        "DataFrame": full_df.to_dict(orient="records") if include_raw else None
    }
    full_json = json.dumps(full_output, indent=4, default=str)

    yearly_output = []
    for year_dict in yearly_data:
        yearly_entry = {
            "Year": year_dict["Year"],
            "Date": year_dict["Date"],
            "Start": year_dict["Start"],
            "End": year_dict["End"],
            "Precipitation": year_dict["Precipitation"],
            "Temperature": year_dict["Temperature"],
            "Wind_Speed": year_dict["Wind_Speed"],
            "Relative_Humidity": year_dict["Relative_Humidity"],
            "Heat_Index": year_dict["Heat_Index"],
            "DataFrame": year_dict["DataFrame"].to_dict(orient="records") if include_raw else None
        }
        yearly_output.append(yearly_entry)

    yearly_json = json.dumps(yearly_output, indent=4, default=str)

    return full_json, yearly_json


def return_to_mainframe(stats):
    """
    Prepares final JSON output to return to frontend or mainframe.
    ------
    Parameters:
        stats: dict
            Dictionary of final statistics
    Returns:
        str: JSON-formatted string ready to send
    """
    stats = json.dumps(stats, indent=4)
    return stats
