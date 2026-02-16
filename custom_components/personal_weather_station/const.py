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
    PERCENTAGE,
    UV_INDEX
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
    "baromin": {"name": "Pressure", "icon": "mdi:gauge", "unit": UnitOfPressure.INHG, "device_class": SensorDeviceClass.PRESSURE},

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
    "t1rainra": {"name": "Rain Rate", "icon": "mdi:weather-rainy", "unit": UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR, "device_class": SensorDeviceClass.PRECIPITATION_INTENSITY},
    "t1rainhr": {"name": "Hourly Rainfall", "icon": "mdi:weather-rainy", "unit": UnitOfLength.MILLIMETERS, "device_class": SensorDeviceClass.PRECIPITATION},
    "t1raindy": {"name": "Daily Rainfall", "icon": "mdi:weather-rainy", "unit": UnitOfLength.MILLIMETERS, "device_class": SensorDeviceClass.PRECIPITATION},
    "t1rainwy": {"name": "Weekly Rainfall", "icon": "mdi:weather-rainy", "unit": UnitOfLength.MILLIMETERS, "device_class": SensorDeviceClass.PRECIPITATION},
    "t1rainmth": {"name": "Monthly Rainfall", "icon": "mdi:weather-rainy", "unit": UnitOfLength.MILLIMETERS, "device_class": SensorDeviceClass.PRECIPITATION},
    "t1rainyr": {"name": "Yearly Rainfall", "icon": "mdi:weather-rainy", "unit": UnitOfLength.MILLIMETERS, "device_class": SensorDeviceClass.PRECIPITATION},

    # 7003800 Type1 (temperature / humidity)
    "t1tem": {"name": "Outdoor Temperature", "icon": "mdi:thermometer", "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "t1hum": {"name": "Outdoor Humidity", "icon": "mdi:water-percent", "unit": PERCENTAGE, "device_class": SensorDeviceClass.HUMIDITY},
    "t1feels": {"name": "Feels Like Temperature", "icon": "mdi:thermometer", "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "t1chill": {"name": "Wind Chill Temperature", "icon": "mdi:thermometer", "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "t1heat": {"name": "Heat Index Temperature", "icon": "mdi:thermometer", "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "t1dew": {"name": "Dew Point Temperature", "icon": "mdi:thermometer", "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "t1wdir": {"name": "Wind Direction", "icon": "mdi:compass", "unit": DEGREE, "device_class": SensorDeviceClass.WIND_DIRECTION},
    "t1ws": {"name": "Wind Speed", "icon": "mdi:weather-windy", "unit": UnitOfSpeed.METERS_PER_SECOND, "device_class": SensorDeviceClass.WIND_SPEED},
    "t1ws10mav": {"name": "10 Minute Average Wind Speed", "icon": "mdi:weather-windy", "unit": UnitOfSpeed.METERS_PER_SECOND, "device_class": SensorDeviceClass.WIND_SPEED},
    "t1wgust": {"name": "Wind Gust", "icon": "mdi:weather-windy", "unit": UnitOfSpeed.METERS_PER_SECOND, "device_class": SensorDeviceClass.WIND_SPEED},


    # Sun / UV
    "solarradiation": {"name": "Solar Radiation", "icon": "mdi:weather-sunny", "unit": UnitOfIrradiance.WATTS_PER_SQUARE_METER, "device_class": SensorDeviceClass.IRRADIANCE},
    "UV": {"name": "UV Index", "icon": "mdi:weather-sunny-alert", "unit": UV_INDEX, "device_class": None},
    "t1uvi": {"name": "UV Index", "icon": "mdi:weather-sunny-alert", "unit": UV_INDEX, "device_class": None},
    "t1solrad": {"name": "Light Intensity", "icon": "mdi:weather-sunny", "unit": UnitOfIrradiance.WATTS_PER_SQUARE_METER, "device_class": SensorDeviceClass.IRRADIANCE},
    "t1wbgt": {"name": "WBGT Temperature", "icon": "mdi:thermometer", "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "t1bat": {"name": "Outdoor Sensor Battery Status", "icon": "mdi:battery", "unit": None, "device_class": None},
    "t1cn": {"name": "Outdoor Sensor Connection Status", "icon": "mdi:access-point-check", "unit": None, "device_class": None},

    # 7003800 Common Console Parameters
    "rbar": {"name": "Relative Air Pressure", "icon": "mdi:gauge", "unit": UnitOfPressure.HPA, "device_class": SensorDeviceClass.PRESSURE},
    "abar": {"name": "Absolute Air Pressure", "icon": "mdi:gauge", "unit": UnitOfPressure.HPA, "device_class": SensorDeviceClass.PRESSURE},
    "intem": {"name": "Indoor Temperature", "icon": "mdi:thermometer", "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "inhum": {"name": "Indoor Humidity", "icon": "mdi:water-percent", "unit": PERCENTAGE, "device_class": SensorDeviceClass.HUMIDITY},
    "inbat": {"name": "Console Battery Level", "icon": "mdi:battery", "unit": None, "device_class": None},

    # 7003800 Type 2/3/4 Multi-Channel Sensors (CH1-CH7)
    "t234c1tem": {"name": "CH1 Temperature", "icon": "mdi:thermometer", "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "t234c1hum": {"name": "CH1 Humidity", "icon": "mdi:water-percent", "unit": PERCENTAGE, "device_class": SensorDeviceClass.HUMIDITY},
    "t234c1bat": {"name": "CH1 Battery Status", "icon": "mdi:battery", "unit": None, "device_class": None},
    "t234c1cn": {"name": "CH1 Connection Status", "icon": "mdi:access-point-check", "unit": None, "device_class": None},
    "t234c1tp": {"name": "CH1 Sensor Type", "icon": "mdi:identifier", "unit": None, "device_class": None},
    "t234c2tem": {"name": "CH2 Temperature", "icon": "mdi:thermometer", "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "t234c2hum": {"name": "CH2 Humidity", "icon": "mdi:water-percent", "unit": PERCENTAGE, "device_class": SensorDeviceClass.HUMIDITY},
    "t234c2bat": {"name": "CH2 Battery Status", "icon": "mdi:battery", "unit": None, "device_class": None},
    "t234c2cn": {"name": "CH2 Connection Status", "icon": "mdi:access-point-check", "unit": None, "device_class": None},
    "t234c2tp": {"name": "CH2 Sensor Type", "icon": "mdi:identifier", "unit": None, "device_class": None},
    "t234c3tem": {"name": "CH3 Temperature", "icon": "mdi:thermometer", "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "t234c3hum": {"name": "CH3 Humidity", "icon": "mdi:water-percent", "unit": PERCENTAGE, "device_class": SensorDeviceClass.HUMIDITY},
    "t234c3bat": {"name": "CH3 Battery Status", "icon": "mdi:battery", "unit": None, "device_class": None},
    "t234c3cn": {"name": "CH3 Connection Status", "icon": "mdi:access-point-check", "unit": None, "device_class": None},
    "t234c3tp": {"name": "CH3 Sensor Type", "icon": "mdi:identifier", "unit": None, "device_class": None},
    "t234c4tem": {"name": "CH4 Temperature", "icon": "mdi:thermometer", "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "t234c4hum": {"name": "CH4 Humidity", "icon": "mdi:water-percent", "unit": PERCENTAGE, "device_class": SensorDeviceClass.HUMIDITY},
    "t234c4bat": {"name": "CH4 Battery Status", "icon": "mdi:battery", "unit": None, "device_class": None},
    "t234c4cn": {"name": "CH4 Connection Status", "icon": "mdi:access-point-check", "unit": None, "device_class": None},
    "t234c4tp": {"name": "CH4 Sensor Type", "icon": "mdi:identifier", "unit": None, "device_class": None},
    "t234c5tem": {"name": "CH5 Temperature", "icon": "mdi:thermometer", "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "t234c5hum": {"name": "CH5 Humidity", "icon": "mdi:water-percent", "unit": PERCENTAGE, "device_class": SensorDeviceClass.HUMIDITY},
    "t234c5bat": {"name": "CH5 Battery Status", "icon": "mdi:battery", "unit": None, "device_class": None},
    "t234c5cn": {"name": "CH5 Connection Status", "icon": "mdi:access-point-check", "unit": None, "device_class": None},
    "t234c5tp": {"name": "CH5 Sensor Type", "icon": "mdi:identifier", "unit": None, "device_class": None},
    "t234c6tem": {"name": "CH6 Temperature", "icon": "mdi:thermometer", "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "t234c6hum": {"name": "CH6 Humidity", "icon": "mdi:water-percent", "unit": PERCENTAGE, "device_class": SensorDeviceClass.HUMIDITY},
    "t234c6bat": {"name": "CH6 Battery Status", "icon": "mdi:battery", "unit": None, "device_class": None},
    "t234c6cn": {"name": "CH6 Connection Status", "icon": "mdi:access-point-check", "unit": None, "device_class": None},
    "t234c6tp": {"name": "CH6 Sensor Type", "icon": "mdi:identifier", "unit": None, "device_class": None},
    "t234c7tem": {"name": "CH7 Temperature", "icon": "mdi:thermometer", "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "t234c7hum": {"name": "CH7 Humidity", "icon": "mdi:water-percent", "unit": PERCENTAGE, "device_class": SensorDeviceClass.HUMIDITY},
    "t234c7bat": {"name": "CH7 Battery Status", "icon": "mdi:battery", "unit": None, "device_class": None},
    "t234c7cn": {"name": "CH7 Connection Status", "icon": "mdi:access-point-check", "unit": None, "device_class": None},
    "t234c7tp": {"name": "CH7 Sensor Type", "icon": "mdi:identifier", "unit": None, "device_class": None},

    # 7003800 Type 5 Lightning Sensor
    "t5lst": {"name": "Last Lightning Strike Time", "icon": "mdi:weather-lightning", "unit": None, "device_class": None},
    "t5lskm": {"name": "Lightning Distance", "icon": "mdi:map-marker-distance", "unit": UnitOfLength.KILOMETERS, "device_class": SensorDeviceClass.DISTANCE},
    "t5lsf": {"name": "Lightning Strikes Last Hour", "icon": "mdi:counter", "unit": None, "device_class": None},
    "t5ls5mtc": {"name": "Lightning Strikes Last 5 Minutes", "icon": "mdi:counter", "unit": None, "device_class": None},
    "t5ls30mtc": {"name": "Lightning Strikes Last 30 Minutes", "icon": "mdi:counter", "unit": None, "device_class": None},
    "t5ls1htc": {"name": "Lightning Strikes Last 1 Hour", "icon": "mdi:counter", "unit": None, "device_class": None},
    "t5ls1dtc": {"name": "Lightning Strikes Last 1 Day", "icon": "mdi:counter", "unit": None, "device_class": None},
    "t5lsbat": {"name": "Lightning Sensor Battery Status", "icon": "mdi:battery", "unit": None, "device_class": None},
    "t5lscn": {"name": "Lightning Sensor Connection Status", "icon": "mdi:access-point-check", "unit": None, "device_class": None},

    # 7003800 Type 6 Water Leak Sensor (CH1-CH7)
    "t6c1wls": {"name": "CH1 Water Leak Status", "icon": "mdi:water-alert", "unit": None, "device_class": None},
    "t6c1bat": {"name": "CH1 Water Leak Battery Status", "icon": "mdi:battery", "unit": None, "device_class": None},
    "t6c1cn": {"name": "CH1 Water Leak Connection Status", "icon": "mdi:access-point-check", "unit": None, "device_class": None},
    "t6c2wls": {"name": "CH2 Water Leak Status", "icon": "mdi:water-alert", "unit": None, "device_class": None},
    "t6c2bat": {"name": "CH2 Water Leak Battery Status", "icon": "mdi:battery", "unit": None, "device_class": None},
    "t6c2cn": {"name": "CH2 Water Leak Connection Status", "icon": "mdi:access-point-check", "unit": None, "device_class": None},
    "t6c3wls": {"name": "CH3 Water Leak Status", "icon": "mdi:water-alert", "unit": None, "device_class": None},
    "t6c3bat": {"name": "CH3 Water Leak Battery Status", "icon": "mdi:battery", "unit": None, "device_class": None},
    "t6c3cn": {"name": "CH3 Water Leak Connection Status", "icon": "mdi:access-point-check", "unit": None, "device_class": None},
    "t6c4wls": {"name": "CH4 Water Leak Status", "icon": "mdi:water-alert", "unit": None, "device_class": None},
    "t6c4bat": {"name": "CH4 Water Leak Battery Status", "icon": "mdi:battery", "unit": None, "device_class": None},
    "t6c4cn": {"name": "CH4 Water Leak Connection Status", "icon": "mdi:access-point-check", "unit": None, "device_class": None},
    "t6c5wls": {"name": "CH5 Water Leak Status", "icon": "mdi:water-alert", "unit": None, "device_class": None},
    "t6c5bat": {"name": "CH5 Water Leak Battery Status", "icon": "mdi:battery", "unit": None, "device_class": None},
    "t6c5cn": {"name": "CH5 Water Leak Connection Status", "icon": "mdi:access-point-check", "unit": None, "device_class": None},
    "t6c6wls": {"name": "CH6 Water Leak Status", "icon": "mdi:water-alert", "unit": None, "device_class": None},
    "t6c6bat": {"name": "CH6 Water Leak Battery Status", "icon": "mdi:battery", "unit": None, "device_class": None},
    "t6c6cn": {"name": "CH6 Water Leak Connection Status", "icon": "mdi:access-point-check", "unit": None, "device_class": None},
    "t6c7wls": {"name": "CH7 Water Leak Status", "icon": "mdi:water-alert", "unit": None, "device_class": None},
    "t6c7bat": {"name": "CH7 Water Leak Battery Status", "icon": "mdi:battery", "unit": None, "device_class": None},
    "t6c7cn": {"name": "CH7 Water Leak Connection Status", "icon": "mdi:access-point-check", "unit": None, "device_class": None},

    # 7003800 Type 8 PM Sensor
    "t8pm25": {"name": "PM2.5 Concentration", "icon": "mdi:molecule", "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, "device_class": SensorDeviceClass.PM25},
    "t8pm10": {"name": "PM10 Concentration", "icon": "mdi:molecule", "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, "device_class": SensorDeviceClass.PM10},
    "t8pm25ai": {"name": "PM2.5 AQI", "icon": "mdi:chart-line", "unit": None, "device_class": None},
    "t8pm10ai": {"name": "PM10 AQI", "icon": "mdi:chart-line", "unit": None, "device_class": None},
    "t8bat": {"name": "PM Sensor Battery Level", "icon": "mdi:battery", "unit": None, "device_class": None},
    "t8cn": {"name": "PM Sensor Connection Status", "icon": "mdi:access-point-check", "unit": None, "device_class": None},

    # 7003800 Type 9 HCHO / VOC Sensor
    "t9hcho": {"name": "HCHO Concentration", "icon": "mdi:molecule", "unit": CONCENTRATION_PARTS_PER_BILLION, "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "t9voclv": {"name": "VOC Level", "icon": "mdi:molecule", "unit": None, "device_class": None},
    "t9bat": {"name": "HCHO/VOC Sensor Battery Level", "icon": "mdi:battery", "unit": None, "device_class": None},
    "t9cn": {"name": "HCHO/VOC Sensor Connection Status", "icon": "mdi:access-point-check", "unit": None, "device_class": None},

    # 7003800 Type 10 CO2 Sensor
    "t10co2": {"name": "CO2 Concentration", "icon": "mdi:molecule-co2", "unit": CONCENTRATION_PARTS_PER_MILLION, "device_class": SensorDeviceClass.CO2},
    "t10bat": {"name": "CO2 Sensor Battery Level", "icon": "mdi:battery", "unit": None, "device_class": None},
    "t10cn": {"name": "CO2 Sensor Connection Status", "icon": "mdi:access-point-check", "unit": None, "device_class": None},

    # 7003800 Type 11 CO Sensor
    "t11co": {"name": "CO Concentration", "icon": "mdi:molecule-co", "unit": CONCENTRATION_PARTS_PER_MILLION, "device_class": SensorDeviceClass.CO},
    "t11bat": {"name": "CO Sensor Battery Level", "icon": "mdi:battery", "unit": None, "device_class": None},
    "t11cn": {"name": "CO Sensor Connection Status", "icon": "mdi:access-point-check", "unit": None, "device_class": None},

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
    "AqNO3": {"name": "NO3 Ion", "icon": "mdi:molecule", "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqSO4": {"name": "SO4 Ion", "icon": "mdi:molecule", "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqSO2": {"name": "Sulfur Dioxide", "icon": "mdi:molecule", "unit": CONCENTRATION_PARTS_PER_BILLION, "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqSO2T": {"name": "Sulfur Dioxide Trace Levels", "icon": "mdi:molecule", "unit": CONCENTRATION_PARTS_PER_BILLION, "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqCO": {"name": "Carbon Monoxide", "icon": "mdi:molecule", "unit": CONCENTRATION_PARTS_PER_MILLION, "device_class": SensorDeviceClass.CO},
    "AqCOT": {"name": "Carbon Monoxide Trace Levels", "icon": "mdi:molecule", "unit": CONCENTRATION_PARTS_PER_BILLION, "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqEC": {"name": "Elemental Carbon", "icon": "mdi:molecule", "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqOC": {"name": "Organic Carbon", "icon": "mdi:molecule", "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqBC": {"name": "Black Carbon", "icon": "mdi:molecule", "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqUV-AETH": {"name": "Aethalometer Channel 2", "icon": "mdi:molecule", "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,"device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},
    "AqPM2.5": {"name": "PM2.5 Mass", "icon": "mdi:molecule", "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,"device_class": SensorDeviceClass.PM25},
    "AqPM10": {"name": "PM10 Mass", "icon": "mdi:molecule", "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, "device_class": SensorDeviceClass.PM10},
    "AqOZONE": {"name": "Ozone", "icon": "mdi:molecule", "unit": CONCENTRATION_PARTS_PER_BILLION, "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS},

    # Metadata
    #"dateutc": {"name": "Last Updated", "icon": "mdi:clock", "unit": "", "device_class": SensorDeviceClass.DATE},
    #"softwaretype": {"name": "Software Type", "icon": "mdi:alpha-s-box", "unit": ""},
    "apiver": {"name": "API Version", "icon": "mdi:api", "unit": None, "device_class": None},
    "rtfreq": {"name": "Update frequency", "icon": "mdi:timer", "unit": UnitOfTime.SECONDS , "device_class": SensorDeviceClass.DURATION},
    #"lowbatt": {"name": "Low Battery", "icon": "mdi:battery-alert", "unit": "", "device_class": ""},
    #"dateutc-datetime": {"name": "Last Updated DateTime", "icon": "mdi:clock", "unit": "", "device_class": SensorDeviceClass.DATE},
    #"last-received-datetime": {"name": "Last Received", "icon": "mdi:clock", "unit": "", "device_class": SensorDeviceClass.DATE},
    #"last-query-state": {"name": "Last Query", "icon": "mdi:clipboard-text", "unit": ""},
    #"last-query-trigger": {"name": "Last Query Trigger", "icon": "mdi:clipboard-text", "unit": ""},
}
