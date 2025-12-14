from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    UnitOfIrradiance,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolumetricFlux,

    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_BILLION,
    CONCENTRATION_PARTS_PER_MILLION,
    DEGREE,
    PERCENTAGE
)

DOMAIN = "personal_weather_station"


SENSOR_LIST = {

    # Temperature
    "tempf": {"name": "Outdoor Temperature", "icon": "mdi:thermometer", "unit": UnitOfTemperature.FAHRENHEIT, "device_class": SensorDeviceClass.TEMPERATURE},
    "indoortempf": {"name": "Indoor Temperature", "icon": "mdi:thermometer", "unit": UnitOfTemperature.FAHRENHEIT, "device_class": SensorDeviceClass.TEMPERATURE},
    "dewptf": {"name": "Dew Point", "icon": "mdi:thermometer", "unit": UnitOfTemperature.FAHRENHEIT, "device_class": SensorDeviceClass.TEMPERATURE},
    "windchillf": {"name": "Wind Chill", "icon": "mdi:thermometer", "unit": UnitOfTemperature.FAHRENHEIT, "device_class": SensorDeviceClass.TEMPERATURE},
    "soiltempf": {"name": "Soil Temperature", "icon": "mdi:thermometer", "unit": UnitOfTemperature.FAHRENHEIT, "device_class": SensorDeviceClass.TEMPERATURE},

    # Humidity
    "humidity": {"name": "Outdoor Humidity", "icon": "mdi:water-percent", "unit": PERCENTAGE, "device_class": SensorDeviceClass.HUMIDITY},
    "indoorhumidity": {"name": "Indoor Humidity", "icon": "mdi:water-percent", "unit": PERCENTAGE, "device_class": SensorDeviceClass.HUMIDITY},
    "soilmoisture": {"name": "Soil Moisture", "icon": "mdi:water-percent", "unit": PERCENTAGE, "device_class": SensorDeviceClass.HUMIDITY},
    "leafwetness": {"name": "Leaf Wetness", "icon": "mdi:water-percent", "unit": PERCENTAGE, "device_class": SensorDeviceClass.HUMIDITY},

    # Pressure
    "baromin": {"name": "Pressure", "icon": "mdi:gauge", "unit": UnitOfPressure.MMHG, "device_class": SensorDeviceClass.PRESSURE},

    # Wind
    "winddir": {"name": "Wind Direction", "icon": "mdi:compass", "unit": DEGREE, "device_class": SensorDeviceClass.WIND_DIRECTION},
    "windspeedmph": {"name": "Wind Speed", "icon": "mdi:weather-windy", "unit": UnitOfSpeed.MILES_PER_HOUR, "device_class": SensorDeviceClass.WIND_SPEED},
    "windgustmph": {"name": "Wind Gust", "icon": "mdi:weather-windy", "unit": UnitOfSpeed.MILES_PER_HOUR, "device_class": SensorDeviceClass.WIND_SPEED},
    "windgustdir": {"name": "Gust Direction", "icon": "mdi:compass", "unit": DEGREE, "device_class": SensorDeviceClass.WIND_DIRECTION},
    "winddir_avg2m": {"name": "Wind Direction 2min Avg", "icon": "mdi:compass", "unit": DEGREE, "device_class": SensorDeviceClass.WIND_DIRECTION},
    "windspdmph_avg2m": {"name": "Wind Speed 2min Avg", "icon": "mdi:weather-windy", "unit": UnitOfSpeed.MILES_PER_HOUR, "device_class": SensorDeviceClass.WIND_SPEED},
    "windgustmph_10m": {"name": "Gust Speed 10min Avg", "icon": "mdi:weather-windy", "unit": UnitOfSpeed.MILES_PER_HOUR, "device_class": SensorDeviceClass.WIND_SPEED},
    "windgustdir_10m": {"name": "Gust Direction 10min Avg", "icon": "mdi:compass", "unit": DEGREE, "device_class": SensorDeviceClass.WIND_DIRECTION},

    # Rain
    "rainin": {"name": "Hourly Rain", "icon": "mdi:weather-rainy", "unit": UnitOfVolumetricFlux.INCHES_PER_HOUR, "device_class": SensorDeviceClass.PRECIPITATION_INTENSITY},
    "dailyrainin": {"name": "Daily Rain", "icon": "mdi:weather-rainy", "unit": UnitOfVolumetricFlux.INCHES_PER_DAY, "device_class": SensorDeviceClass.PRECIPITATION_INTENSITY},
    "weeklyrainin": {"name": "Weekly Rain", "icon": "mdi:weather-rainy", "unit": UnitOfLength.INCHES, "device_class": SensorDeviceClass.PRECIPITATION},
    "monthlyrainin": {"name": "Monthly Rain", "icon": "mdi:weather-rainy", "unit": UnitOfLength.INCHES, "device_class": SensorDeviceClass.PRECIPITATION},
    "yearlyrainin": {"name": "Yearly Rain", "icon": "mdi:weather-rainy", "unit": UnitOfLength.INCHES, "device_class": SensorDeviceClass.PRECIPITATION},

    # Sun / UV
    "solarradiation": {"name": "Solar Radiation", "icon": "mdi:weather-sunny", "unit": UnitOfIrradiance.WATTS_PER_SQUARE_METER, "device_class": SensorDeviceClass.IRRADIANCE},
    "UV": {"name": "UV Index", "icon": "mdi:weather-sunny-alert", "unit": None, "device_class": None},

    # Clouds / Visibility
    #"weather": {"name": "METAR Weather", "icon": "mdi:weather-partly-cloudy", "unit": ""},
    "clouds": {"name": "Cloud Cover", "icon": "mdi:weather-cloudy", "unit": PERCENTAGE, "device_class": None},
    "visibility": {"name": "Visibility", "icon": "mdi:eye", "unit": UnitOfLength.MILES,"device_class": SensorDeviceClass.DISTANCE},

    # Pollution
    "AqNO": {"name": "Nitric Oxide", "icon": "mdi:molecule", "unit": CONCENTRATION_PARTS_PER_MILLION, "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqNO2T": {"name": "Nitrogen Dioxide", "icon": "mdi:molecule", "unit": CONCENTRATION_PARTS_PER_BILLION, "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqNO2": {"name": "NO2 X Computed", "icon": "mdi:molecule", "unit": CONCENTRATION_PARTS_PER_BILLION, "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqNO2Y": {"name": "NO2 Y Computed", "icon": "mdi:molecule", "unit": CONCENTRATION_PARTS_PER_BILLION, "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqNOX": {"name": "Nitrogen Oxides", "icon": "mdi:molecule", "unit": CONCENTRATION_PARTS_PER_BILLION, "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqNOY": {"name": "Total Reactive Nitrogen", "icon": "mdi:molecule", "unit": CONCENTRATION_PARTS_PER_BILLION, "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqNO3": {"name": "NO3 Ion", "icon": "mdi:molecule", "unit": "µg/m³", "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqSO4": {"name": "SO4 Ion", "icon": "mdi:molecule", "unit": "µg/m³","device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqSO2": {"name": "Sulfur Dioxide", "icon": "mdi:molecule", "unit": CONCENTRATION_PARTS_PER_BILLION, "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqSO2T": {"name": "Sulfur Dioxide Trace Levels", "icon": "mdi:molecule", "unit": CONCENTRATION_PARTS_PER_BILLION, "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqCO": {"name": "Carbon Monoxide", "icon": "mdi:molecule", "unit": CONCENTRATION_PARTS_PER_MILLION, "device_class": SensorDeviceClass.CO},
    "AqCOT": {"name": "Carbon Monoxide Trace Levels", "icon": "mdi:molecule", "unit": CONCENTRATION_PARTS_PER_BILLION, "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqEC": {"name": "Elemental Carbon", "icon": "mdi:molecule", "unit": "µg/m³","device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqOC": {"name": "Organic Carbon", "icon": "mdi:molecule", "unit": "µg/m³","device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqBC": {"name": "Black Carbon", "icon": "mdi:molecule", "unit": "µg/m³","device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqUV-AETH": {"name": "Aethalometer Channel 2", "icon": "mdi:molecule", "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,"device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqPM2.5": {"name": "PM2.5 Mass", "icon": "mdi:molecule", "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,"device_class": SensorDeviceClass.PM25},
    "AqPM10": {"name": "PM10 Mass", "icon": "mdi:molecule", "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, "device_class": SensorDeviceClass.PM10},
    "AqOZONE": {"name": "Ozone", "icon": "mdi:molecule", "unit": CONCENTRATION_PARTS_PER_BILLION, "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},

    # Metadata
    #"dateutc": {"name": "Last Updated", "icon": "mdi:clock", "unit": "", "device_class": SensorDeviceClass.DATE},
    #"softwaretype": {"name": "Software Type", "icon": "mdi:alpha-s-box", "unit": ""},
    "rtfreq": {"name": "Update frequency", "icon": "mdi:timer", "unit": UnitOfTime.SECONDS , "device_class": SensorDeviceClass.DURATION},
    #"lowbatt": {"name": "Low Battery", "icon": "mdi:battery-alert", "unit": "", "device_class": ""},
    #"dateutc-datetime": {"name": "Last Updated DateTime", "icon": "mdi:clock", "unit": "", "device_class": SensorDeviceClass.DATE},
    #"last-received-datetime": {"name": "Last Received", "icon": "mdi:clock", "unit": "", "device_class": SensorDeviceClass.DATE},
    #"last-query-state": {"name": "Last Query", "icon": "mdi:clipboard-text", "unit": ""},
    #"last-query-trigger": {"name": "Last Query Trigger", "icon": "mdi:clipboard-text", "unit": ""},
}

