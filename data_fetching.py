import requests
import pandas as pd
from functools import lru_cache

base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
parameters = "PRECTOTCORR,T2M,WS2M,RH2M"
new_params = "T2MDEW,T2M_MAX,T2M_MIN,PS,T2MWET,WS50M,QV2M,WS10M"


def get_from_mainframe():
    """
    Handles input from the front-end or provides test/default values.
    ------
    Returns:
        tuple: (lat: float, lon: float, date: str, days: int, years: int)
    """
    # For testing / default
    lat, lon = 24.8, 68.0
    date = "2019/08/30"
    days, years = 2, 5
    return lat, lon, date, days, years


def build_url(base_url: str, lat: float, lon: float, start, end, parameters: str) -> str:
    """
    Builds a NASA POWER API request URL.
    ------
    Parameters:
        base_url: str
        lat: float
        lon: float
        start: datetime
        end: datetime
        parameters: str, comma-separated API variables
    Returns:
        str: Complete API URL
    """
    start_str, end_str = start.strftime("%Y%m%d"), end.strftime("%Y%m%d")
    url = (
        f"{base_url}"
        f"?parameters={parameters}"
        f"&community=AG"
        f"&longitude={lon}&latitude={lat}"
        f"&start={start_str}&end={end_str}"
        f"&format=JSON"
    )
    return url


def fetch_data(url: str) -> dict:
    """
    Fetches data from NASA POWER API.
    ------
    Parameters:
        url: str
    Returns:
        dict: JSON response if successful, None otherwise
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    print("Error:", response.status_code, response.text)
    return None


def process_data(raw_data: dict) -> pd.DataFrame:
    """
    Converts NASA POWER JSON data to a pandas DataFrame.
    ------
    Parameters:
        raw_data: dict
    Returns:
        pd.DataFrame
    """
    if not raw_data:
        return pd.DataFrame()
    
    params = raw_data["properties"]["parameter"]
    df = pd.DataFrame({
        "Date": pd.to_datetime(list(params["PRECTOTCORR"].keys()), format="%Y%m%d"),
        "Precipitation (mm/day)": list(params["PRECTOTCORR"].values()),
        "Temperature to 2m (°C)": list(params["T2M"].values()),
        "Wind speed to 2m (m/s)": list(params["WS2M"].values()),
        "Relative humidity 2m (%)": list(params["RH2M"].values())
    })
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fills missing numeric values with column mean.
    ------
    Parameters:
        df: pd.DataFrame
    Returns:
        pd.DataFrame
    """
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].mean())
    return df


def format_data(lat, lon, start, end, base_url=base_url, parameters=parameters) -> pd.DataFrame:
    """
    Fetches, processes, and cleans NASA POWER weather data.
    ------
    Parameters:
        lat: float
        lon: float
        start: datetime
        end: datetime
        base_url: str
        parameters: str
    Returns:
        pd.DataFrame
    """
    url = build_url(base_url, lat, lon, start, end, parameters)
    raw_data = fetch_data(url)
    df = process_data(raw_data)
    return clean_data(df)

@lru_cache(maxsize=32)
def format_data_cached(lat, lon, start, end):
    """
    Cached version of format_data to avoid repeated API calls.
    Works if the user re-enters previous input. Good for testing.
    ------
    Parameters:
        lat: float
        lon: float
        start: datetime
        end: datetime
    Returns:
        pd.DataFrame
    """
    return format_data(lat, lon, start, end)
