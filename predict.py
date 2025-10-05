
def classify_event(series, categories):
    """
    Classifies data in a pandas Series into categories and calculates their probabilities.
    ------
    Parameters:
        series: pandas Series (e.g., df["Temperature"])
        categories: dict {label: condition} where condition is a boolean mask
    Returns:
        probability: float (probability of the dominant category)
        status: str (label of the dominant category)
        events: dict (full mapping of category probabilities)
    """
    total = len(series)
    events = {}

    for label, condition in categories.items():
        count = series[condition].count()
        probability = count / total
        events[label] = probability

    status = max(events, key=events.get)
    probability = events[status]

    return probability, status, events


def check_temperature(df):
    """
    Classifies temperature readings into hot/cold categories.
    ------
    Parameters:
        df: pandas DataFrame with column "Temperature to 2m (°C)"
    Returns:
        probability, status, events from classify_event()
    """
    temp = df["Temperature to 2m (°C)"]
    categories = {
        "Very Hot": (temp >= 40),
        "Hot": (temp >= 35) & (temp < 40),
        "Warm": (temp >= 30) & (temp < 35),
        "Moderate": (temp >= 20) & (temp <= 29),
        "Cool": (temp >= 11) & (temp <= 19),
        "Cold": (temp <= 10) & (temp > 5),
        "Very Cold": (temp <= 5)
    }

    return classify_event(temp, categories)


def check_humidity(df):
    """
    Classifies humidity levels based on comfort ranges.
    ------
    Parameters:
        df: pandas DataFrame with column "Relative humidity 2m (%)"
    Returns:
        probability, status, events from classify_event()
    """
    rh = df["Relative humidity 2m (%)"]
    categories = {
        "Comfortable": (rh < 60),
        "Humid": (rh >= 60) & (rh < 80),
        "Very Uncomfortable": (rh >= 80)
    }
    return classify_event(rh, categories)


def check_precipitation(df):
    """
    Classifies precipitation intensity.
    ------
    Parameters:
        df: pandas DataFrame with column "Precipitation (mm/day)"
    Returns:
        probability, status, events from classify_event()
    """
    precip = df["Precipitation (mm/day)"]

    if (precip == 0).all():
        return 0.0, "None", {"None": 1.0}

    categories = {
        "Low": (precip > 0) & (precip <= 2),
        "Moderate": (precip > 2) & (precip <= 10),
        "High": (precip > 10)
    }
    return classify_event(precip, categories)


def check_wind(df):
    """
    Classifies wind speeds into descriptive categories.
    ------
    Parameters:
        df: pandas DataFrame with column "Wind speed to 2m (m/s)"
    Returns:
        probability, status, events from classify_event()
    """
    wind = df["Wind speed to 2m (m/s)"]
    categories = {
        "Calm": (wind < 3),
        "Breezy": (wind >= 3) & (wind < 6),
        "Windy": (wind >= 6) & (wind < 10),
        "Very Windy": (wind >= 10)
    }
    return classify_event(wind, categories)


def check_heat_index(df):
    """
    Classifies heat index values into safety/danger levels.
    ------
    Parameters:
        df: pandas DataFrame with column "Heat Index (°C)"
    Returns:
        probability, status, events from classify_event()
    """
    series = df["Heat Index (°C)"]
    categories = {
        "Safe": (series < 27),
        "Caution": (series >= 27) & (series < 32),
        "Extreme Caution": (series >= 32) & (series < 41),
        "Danger": (series >= 41) & (series < 54),
        "Extreme Danger": (series >= 54)
    }
    return classify_event(series, categories)
