from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from datetime import datetime
from data_handling import get_combined_dataframe
from predict import check_humidity, check_precipitation, check_temperature, check_wind, check_heat_index


app = FastAPI()


class Data(BaseModel):
    date: str
    lat: float
    lon: float

    @validator("lat")
    def validate_lat(cls, v):
        if not -90 <= v <= 90:
            raise ValueError("Latitudinal Value should be between -90 and 90")
        return v

    @validator("lon")
    def validate_lon(cls, v):
        if not -180 <= v <= 180:
            raise ValueError("Longtidunal Value should be between -180 and 180")
        return v

    @validator("date")
    def validate_date(cls, v):
        try:
            datetime.strptime(v, "%Y/%m/%d")
        except ValueError:
            raise ValueError("Date must be in YYYY/MM/DD format")
        return v


@app.post("/")
async def analyze_weather(request: Data):
    try:
        vector_data = get_combined_dataframe(
            request.lat,
            request.lon,
            request.date
        )

        results = {
            "Temperature": check_temperature(vector_data),
            "Humidity": check_humidity(vector_data),
            "Precipitation": check_precipitation(vector_data),
            "Wind": check_wind(vector_data),
            "Heat Index": check_heat_index(vector_data),
        }

        formatted_results = {
            factor: {
                "probability": float(prob),
                "status": status,
                "distribution": dist,
            }
            for factor, (prob, status, dist) in results.items()
        }

        return results
    except Exception as e:
        import traceback
        print("⚠️ ERROR OCCURRED ⚠️")
        traceback.print_exc()   # prints full stack trace in your console
        raise HTTPException(status_code=500, detail=str(e))





""" Change Log """
"""
- Removed Coordinate Validation (Assumes Pre-Validated Coordinates)
- Converted date into datetime object, format is changed/handled separately in URL construction
- Changed format_data being called with a new function called get_combined_dataframe
- Setup new filter function filter_years(), takes target_date and years as parameters, saves years to check
- Created get_combined_dataframe(), iterates through each year from the result output from filter_years() and combines the data
- Had GPT standardise prediction functions (the pattern in each was somewhat repeated)
- Prediction functions may now output the entire result dictionary if needed
- Setup calculate_heat_index(), GPT Built as formula is complex but standard, conversions are kept in mind
- Setup check_heat_index(), similar to all other prediction functions, same format
- No manual thresholds have been set, all thresholds have been setup by GPT temporarily
- Formatted output in program file, iterates and displays each prediction model with probability & status.
"""

""" Issues """
"""
- Program slows down when years >=2
- Program can not handle exceeding max years (ex. can't check +6 years if current year is 2023)
- Heat Index formula is not universal, implementing basic heat indexing followed same format as all others hence did so
- Messing with datetime object may cause issues, heads up
- Lat/lon & Date is hardcoded, need them passed in exact formats regardless (lat,lon), & (YYYY/MM/DD)
- An API call is executed everytime data is accessed, if same data is accessed twice, have a way of storing it to avoid repeated calls
"""

""" Feedback """
"""
- Program HAS to iterate over multiple years for reliability, otherwise outliers may cause inaccuracy
- More features can be added, for now it's better not to have too many
- Final output function is required, human output which is both readable + displays the status
- Instead of hardcoding values, each prediction function can have a predefined input (ex. calm_threshold that is passed in as default)
- The output needs to be wrapped in JSON, currently is dict, has to be more detailed (geopy could be used to determine exact location for JSON)
"""