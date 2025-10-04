import requests
import pandas as pd


# Test Coordinates & Dates
# lat, lon = 24.8, 68.0
# start, end = "20250801", "20250831" # (YYYY/MM/DD) 
base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
parameters = "PRECTOTCORR,T2M,WS2M,WS10M,RH2M,QV2M"
new_params = "T2MDEW,T2M_MAX,T2M_MIN,PS,T2MWET,WS50M"


"""
Parameters (POWER API variables):

- PRECTOTCORR : Precipitation (mm/day)
    - Daily total precipitation corrected for known biases.
    - Unit: millimeters per day (mm/day).
    - Useful for identifying rainy days and estimating rainfall totals.

- T2M : Air Temperature at 2 meters (°C)
    - Mean daily air temperature measured at 2 meters above ground.
    - Unit: degrees Celsius (°C).
    - Used for heat/cold exposure, comfort, and event planning.

- WS2M : Wind Speed at 2 meters (m/s)
    - Average wind speed at 2 meters height.
    - Unit: meters per second (m/s).
    - Captures near-surface breezes, less relevant for event disruption.

- WS10M : Wind Speed at 10 meters (m/s)
    - Average wind speed at 10 meters height.
    - Unit: meters per second (m/s).
    - Standard meteorological reference; better indicator of wind conditions for outdoor events.

- RH2M : Relative Humidity at 2 meters (%)
    - Mean relative humidity at 2 meters height.
    - Unit: percent (%).
    - Important for discomfort, mugginess, and heat index calculations.

- QV2M : Specific Humidity at 2 meters (g/kg)
    - Mass of water vapor per unit mass of moist air at 2 meters.
    - Unit: grams per kilogram (g/kg).
    - More physically accurate than RH; useful for advanced weather modeling, but less intuitive.
"""

# Constructs URL
def build_url(base_url: str, lat: float, lon: float, start: str, end: str, parameters: str) -> str:
    """
    Build a NASA POWER API or similar data request URL.
    """

    # Convert To Power API Format (YYYYMMDD)
    start, end = start.strftime("%Y%m%d"), end.strftime("%Y%m%d")
    url = (
        f"{base_url}"
        f"?parameters={parameters}"        # Parameters to fetch
        f"&community=AG"                   # Agricultural Data
        f"&longitude={lon}&latitude={lat}" # Location
        f"&start={start}&end={end}"        # Time range
        f"&format=JSON"                    # Response format
    )
    return url


# Fetches Data From API
def fetch_data(url: str) -> dict:
    """
    Fetch data from NASA API with simple error handling.
    """
    response = requests.get(url)

    if response.status_code == 200:  # Success
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        return None
    

# Processes Data Into Data Frame
def process_data(raw_data: dict) -> pd.DataFrame:
    """
    Process raw NASA API JSON response into a Pandas DataFrame.
    """
    if raw_data is None:
        return pd.DataFrame()  # return empty DataFrame if error
    
    params = raw_data["properties"]["parameter"]

    df = pd.DataFrame({
        "Date": pd.to_datetime(list(params["PRECTOTCORR"].keys()), format="%Y%m%d"),
        "Precipitation (mm/day)": list(params["PRECTOTCORR"].values()),
        "Temperature to 2m (°C)": list(params["T2M"].values()),
        "Wind speed to 2m (m/s)": list(params["WS2M"].values()),
        "Wind speed to 10m (m/s)": list(params["WS10M"].values()),
        "Relative humidity 2m (%)": list(params["RH2M"].values()),
        "Specific humidity 2m (%)": list(params["QV2M"].values())
    })

    return df

# Cleans Data If Needed
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    # Fill missing values with column mean
    for col in df.columns:
        if df[col].dtype in ["float64", "int64"]:
            df[col] = df[col].fillna(df[col].mean())
    return df


# Formats Data For Final Output
def format_data(lat, lon, start, end, base_url=base_url, parameters=parameters) -> pd.DataFrame:
    # Builds The URL
    url = build_url(base_url, lat, lon, start, end, parameters)
    # Fetches The Raw Data
    raw_data = fetch_data(url)
    # Cleans & Converts Raw Data Into Array
    return clean_data(process_data(raw_data))


