import pandas as pd
from data_fetching import format_data_cached
from output_formatting import get_column_statistics, get_predictions

def calculate_heat_index(temp_c, rel_humid):
    """
    Calculates the Heat Index (apparent temperature) using temperature and relative humidity.
    ------
    Parameters:
        temp_c: pd.Series or float, air temperature in Celsius
        rel_humid: pd.Series or float, relative humidity in percent
    Returns:
        pd.Series or float: Heat Index in Celsius
    """
    T = temp_c * 9/5 + 32
    R = rel_humid
    HI = (-42.379 + 2.04901523*T + 10.14333127*R - 0.22475541*T*R
          - 6.83783e-3*T**2 - 5.481717e-2*R**2
          + 1.22874e-3*T**2*R + 8.5282e-4*T*R**2
          - 1.99e-6*T**2*R**2)
    HI_Celsius = (HI - 32) * 5/9
    return HI_Celsius


def filter_date(target_date, days):
    """
    Generates a start and end date range around the target date.
    ------
    Parameters:
        target_date: str, date in "YYYY/MM/DD" format
        days: int, number of days before and after target date
    Returns:
        tuple: (start_date, end_date) as pandas Timestamps
    """
    target_date = pd.to_datetime(target_date, format="%Y/%m/%d")
    delta = pd.Timedelta(days=days)
    start = target_date - delta
    end = target_date + delta
    return start, end


def filter_years(target_date, years):
    """
    Creates a list of past years for the given target date.
    ------
    Parameters:
        target_date: str, date in "YYYY/MM/DD" format
        years: int, number of previous years to include
    Returns:
        list: Timestamps for equivalent dates in past years
    """
    target_date = pd.to_datetime(target_date, format="%Y/%m/%d")
    return [target_date.replace(year=target_date.year - i) for i in range(1, years + 1)]


def get_combined_dataframe(lat, lon, target_date, days, years):
    """
    Fetches and combines weather data for multiple past years,
    adding a calculated Heat Index column and merging predictions with descriptive statistics.
    ------
    Parameters:
        lat: float, latitude
        lon: float, longitude
        target_date: str, date in "YYYY/MM/DD" format
        days: int, number of days around the target date
        years: int, number of years before the target year
    Returns:
        tuple:
            - final_df: pd.DataFrame containing all combined years
            - yearly_data: list of dicts for each year, containing:
                {
                    "Year": int,
                    "Date": str,
                    "Start": str,
                    "End": str,
                    "Precipitation": dict (stats + predictions),
                    "Temperature": dict (stats + predictions),
                    "Wind_Speed": dict (stats + predictions),
                    "Relative_Humidity": dict (stats + predictions),
                    "Heat_Index": dict (stats + predictions),
                    "DataFrame": pd.DataFrame for that year
                }
    """
    combined_data = []
    yearly_data = []

    for date in filter_years(target_date, years):
        start, end = filter_date(date, days)
        df = format_data_cached(lat, lon, start, end)
        df["Heat Index (°C)"] = calculate_heat_index(
            df["Temperature to 2m (°C)"],
            df["Relative humidity 2m (%)"]
        )

        stats = get_predictions(df)
        yearly_data.append({
            "Year": date.year,
            "Date": date.strftime("%Y/%m/%d"),
            "Start": start.strftime("%Y/%m/%d"),
            "End": end.strftime("%Y/%m/%d"),
            "Precipitation": {**get_column_statistics(df["Precipitation (mm/day)"]), **stats["Precipitation"]},
            "Temperature": {**get_column_statistics(df["Temperature to 2m (°C)"]), **stats["Temperature"]},
            "Wind_Speed": {**get_column_statistics(df["Wind speed to 2m (m/s)"]), **stats["Wind_Speed"]},
            "Relative_Humidity": {**get_column_statistics(df["Relative humidity 2m (%)"]), **stats["Relative_Humidity"]},
            "Heat_Index": {**get_column_statistics(df["Heat Index (°C)"]), **stats["Heat_Index"]},
            "DataFrame": df
        })

        combined_data.append(df)

    final_df = pd.concat(combined_data, ignore_index=True)
    return final_df, yearly_data
