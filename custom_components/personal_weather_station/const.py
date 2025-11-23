DOMAIN = "personal_weather_station"


SENSOR_LIST = {
    # Temperature
    "tempf": {"name": "Outdoor Temperature", "icon": "mdi:thermometer", "unit": "°F", "device_class": "temperature"},
    "indoortempf": {"name": "Indoor Temperature", "icon": "mdi:thermometer", "unit": "°F", "device_class": "temperature"},
    "dewptf": {"name": "Dew Point", "icon": "mdi:thermometer", "unit": "°F", "device_class": "temperature"},
    "windchillf": {"name": "Wind Chill", "icon": "mdi:thermometer", "unit": "°F", "device_class": "temperature"},
    "soiltempf": {"name": "Soil Temperature", "icon": "mdi:thermometer", "unit": "°F", "device_class": "temperature"},

    # Humidity
    "humidity": {"name": "Outdoor Humidity", "icon": "mdi:water-percent", "unit": "%", "device_class": "humidity"},
    "indoorhumidity": {"name": "Indoor Humidity", "icon": "mdi:water-percent", "unit": "%", "device_class": "humidity"},
    "soilmoisture": {"name": "Soil Moisture", "icon": "mdi:water-percent", "unit": "%", "device_class": "humidity"},
    "leafwetness": {"name": "Leaf Wetness", "icon": "mdi:water-percent", "unit": "%", "device_class": "humidity"},

    # Pressure
    "baromin": {"name": "Pressure", "icon": "mdi:gauge", "unit": "inHg", "device_class": "pressure"},

    # Wind
    "winddir": {"name": "Wind Direction", "icon": "mdi:compass", "unit": "°", "device_class": "wind_direction"},
    "windspeedmph": {"name": "Wind Speed", "icon": "mdi:weather-windy", "unit": "mph", "device_class": "wind_speed"},
    "windgustmph": {"name": "Wind Gust", "icon": "mdi:weather-windy", "unit": "mph", "device_class": "wind_speed"},
    "windgustdir": {"name": "Gust Direction", "icon": "mdi:compass", "unit": "°", "device_class": "wind_direction"},
    "winddir_avg2m": {"name": "Wind Direction 2min Avg", "icon": "mdi:compass", "unit": "°", "device_class": "wind_direction"},
    "windspdmph_avg2m": {"name": "Wind Speed 2min Avg", "icon": "mdi:weather-windy", "unit": "mph", "device_class": "wind_speed"},
    "windgustmph_10m": {"name": "Gust Speed 10min Avg", "icon": "mdi:weather-windy", "unit": "mph", "device_class": "wind_speed"},
    "windgustdir_10m": {"name": "Gust Direction 10min Avg", "icon": "mdi:compass", "unit": "°", "device_class": "wind_direction"},

    # Rain
    "rainin": {"name": "Hourly Rain", "icon": "mdi:weather-rainy", "unit": "in/h", "device_class": "precipitation_intensity"},
    "dailyrainin": {"name": "Daily Rain", "icon": "mdi:weather-rainy", "unit": "in/d", "device_class": "precipitation_intensity"},
    "weeklyrainin": {"name": "Weekly Rain", "icon": "mdi:weather-rainy", "unit": "in", "device_class": "precipitation"},
    "monthlyrainin": {"name": "Monthly Rain", "icon": "mdi:weather-rainy", "unit": "in", "device_class": "precipitation"},
    "yearlyrainin": {"name": "Yearly Rain", "icon": "mdi:weather-rainy", "unit": "in", "device_class": "precipitation"},

    # Sun / UV
    "solarradiation": {"name": "Solar Radiation", "icon": "mdi:weather-sunny", "unit": "W/m²", "device_class": "irradiance"},
    "UV": {"name": "UV Index", "icon": "mdi:weather-sunny-alert", "unit": "", "device_class": "None"},

    # Clouds / Visibility
    #"weather": {"name": "METAR Weather", "icon": "mdi:weather-partly-cloudy", "unit": ""},
    "clouds": {"name": "Cloud Cover", "icon": "mdi:weather-cloudy", "unit": "%", "device_class": "None"},
    "visibility": {"name": "Visibility", "icon": "mdi:eye", "unit": "mi","device_class": "distance"},

    # Pollution
    "AqNO": {"name": "Nitric Oxide", "icon": "mdi:molecule", "unit": "ppm", "device_class": "volatile_organic_compounds_parts"},
    "AqNO2T": {"name": "Nitrogen Dioxide", "icon": "mdi:molecule", "unit": "ppb", "device_class": "volatile_organic_compounds_parts"},
    "AqNO2": {"name": "NO2 X Computed", "icon": "mdi:molecule", "unit": "ppb", "device_class": "volatile_organic_compounds_parts"},
    "AqNO2Y": {"name": "NO2 Y Computed", "icon": "mdi:molecule", "unit": "ppb", "device_class": "volatile_organic_compounds_parts"},
    "AqNOX": {"name": "Nitrogen Oxides", "icon": "mdi:molecule", "unit": "ppb", "device_class": "volatile_organic_compounds_parts"},
    "AqNOY": {"name": "Total Reactive Nitrogen", "icon": "mdi:molecule", "unit": "ppb", "device_class": "volatile_organic_compounds_parts"},
    "AqNO3": {"name": "NO3 Ion", "icon": "mdi:molecule", "unit": "µg/m³", "device_class": "volatile_organic_compounds_parts"},
    "AqSO4": {"name": "SO4 Ion", "icon": "mdi:molecule", "unit": "µg/m³","device_class": "volatile_organic_compounds_parts"},
    "AqSO2": {"name": "Sulfur Dioxide", "icon": "mdi:molecule", "unit": "ppb", "device_class": "volatile_organic_compounds_parts"},
    "AqSO2T": {"name": "Sulfur Dioxide Trace Levels", "icon": "mdi:molecule", "unit": "ppb", "device_class": "volatile_organic_compounds_parts"},
    "AqCO": {"name": "Carbon Monoxide", "icon": "mdi:molecule", "unit": "ppm", "device_class": "carbon_monoxide"},
    "AqCOT": {"name": "Carbon Monoxide Trace Levels", "icon": "mdi:molecule", "unit": "ppb", "device_class": "volatile_organic_compounds_parts"},
    "AqEC": {"name": "Elemental Carbon", "icon": "mdi:molecule", "unit": "µg/m³","device_class": "volatile_organic_compounds_parts"},
    "AqOC": {"name": "Organic Carbon", "icon": "mdi:molecule", "unit": "µg/m³","device_class": "volatile_organic_compounds_parts"},
    "AqBC": {"name": "Black Carbon", "icon": "mdi:molecule", "unit": "µg/m³","device_class": "volatile_organic_compounds_parts"},
    "AqUV-AETH": {"name": "Aethalometer Channel 2", "icon": "mdi:molecule", "unit": "µg/m³","device_class": "volatile_organic_compounds_parts"},
    "AqPM2.5": {"name": "PM2.5 Mass", "icon": "mdi:molecule", "unit": "µg/m³","device_class": "pm25"},
    "AqPM10": {"name": "PM10 Mass", "icon": "mdi:molecule", "unit": "µg/m³", "device_class": "pm10"},
    "AqOZONE": {"name": "Ozone", "icon": "mdi:molecule", "unit": "ppb", "device_class": "volatile_organic_compounds_parts"},

    # Metadata
    #"dateutc": {"name": "Last Updated", "icon": "mdi:clock", "unit": ""},
    #"softwaretype": {"name": "Software Type", "icon": "mdi:alpha-s-box", "unit": ""},
    #"rtfreq": {"name": "Realtime Frequency", "icon": "mdi:timer", "unit": "s"},
    #"lowbatt": {"name": "Low Battery", "icon": "mdi:battery-alert", "unit": ""},
    #"dateutc-datetime": {"name": "Last Updated DateTime", "icon": "mdi:clock", "unit": ""},
    #"last-received-datetime": {"name": "Last Received", "icon": "mdi:clock", "unit": ""},
    #"last-query-state": {"name": "Last Query", "icon": "mdi:clipboard-text", "unit": ""},
    #"last-query-trigger": {"name": "Last Query Trigger", "icon": "mdi:clipboard-text", "unit": ""},
}

