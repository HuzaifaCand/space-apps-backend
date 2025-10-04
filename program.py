from data_fetching import get_from_mainframe
from data_handling import get_combined_dataframe
from output_formatting import get_final_statistics, construct_json, return_to_mainframe


def main():
    """
    Main entry point for the weather analysis program.
    ------
    Steps:
        1. Gets target lat/lon/date from get_from_mainframe()
        2. Generates combined weather data across years
        3. Computes heat index and descriptive statistics
        4. Outputs results as JSON
    """
    lat, lon, target_date, days, years = get_from_mainframe()
    vector_data, yearly_data = get_combined_dataframe(lat, lon, target_date, days, years)
    final_stats = get_final_statistics(vector_data)
    full_json, yearly_json = construct_json(vector_data, yearly_data, final_stats)

    print(yearly_json)
    print(return_to_mainframe(final_stats))



if __name__ == "__main__":
    main()


""" Change Log [2nd October 2025] """
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


""" Change Log [4th October 2025] """
"""
- Updated docstring documentation for all functions, removed comments
- Moved all input extraction to data_fetching.py, data fetched directly from front-end
- Setup get_from_mainframe(), all front-backend data handling can be sorted within the function, which itself returns the inputs
- Function get_from_mainframe() expects string with lat,lon,date,days,years though if day and years not specified it takes a default value
- Removed hardcoded values from filter_date() and filter_year() functions, as default values are handled in get_from_mainframe()
- Main function now takes data as an argument, which is all the data wrapped into one string separated by "," to be handled within the backend program
- Removed WS10m & QV2M from parameters to extract, both were unrequired
- Setup get_column_statistics in predict.py, calculates measures of central tendency (mean, median, std etc..) for columns
- Implemented get_column_statistics() into yearly data extraction, provides more insights for each year in JSON, made sure output is rounded to 2sf
- Made sure get_column_statistics() and get_dataframe_statistics() don't show np.float datatypes, converted them into basic floats.
- Fixed get_dataframe_statistics() to work on entire dataset without failing at range calculation
- Created a new file, output_formatting.py, Moved both get_dataframe_statistics() and get_column_statistics() to it
- Setup get_predictions(), which returns a dictionary of the predictions from the data set (works on both yearly and final dataset)
- Created get_final_statistics() to merge both the normal statistics (measures of central tendency) for the final data with our specific statistics
- Implemented get_statistics() directly into get_combined_dataframe() so all meaning statistics are added directly into the list of yearly dicts.
- Setup construct_json, takes full data and yearly data, converts it into JSON objects to be sent
- Setup return_to_mainframe(), takes the final statistics and sends the final data to the front-end in JSON format for use.
"""
