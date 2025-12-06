

<image src="https://raw.githubusercontent.com/home-assistant/brands/refs/heads/master/custom_integrations/personal_weather_station/icon%402x.png" align="right" style="margin-top:-2em;width:150px;margin-right:2em;display:inline-block;float:right;"></image>

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration) 

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=MaxensF&repository=personal_weather_station&category=integration)




# Personal Weather Station (PWS)

This custom Home Assistant integration allows you to receive real-time data from your **Personal Weather Station** and expose it as sensors inside Home Assistant. It uses an HTTP endpoint to receive sensor updates and automatically creates or updates sensors for temperature, humidity, pressure, and more.

---

## Features

- Receive weather station data via HTTP requests.
- Automatically create new sensors for any supported data key.
- Update existing sensors in real-time.
- Fully compatible with Home Assistant sensor platform.
- No authentication required (optional to add in `PwsView` if desired).

---

## Supported Sensors

The integration relies on a predefined list of sensors in [`SENSOR_LIST`](./custom_components/personal_weather_station/const.py).  
Typical supported keys include:

- Temperature (`temperature`)
- Humidity (`humidity`)
- Pressure (`pressure`)
- Wind speed (`wind_speed`)
- Rainfall (`rainfall`)
- …and any custom keys you define.

Each sensor supports metadata such as **name**, **unit of measurement**, **icon**, and **device class**.

---

## Compatible Weather Stations

The following personal weather stations have been confirmed to work with this integration:

- **Bresser 7-in-1 Weather Station**
  - 7002586
  - 7002582

Other stations may also work if they can send HTTP GET requests with query parameters matching the keys defined in `SENSOR_LIST`.  
Feel free to try your own weather station and see if it works, and consider contributing any new compatible models to the project!

---

## Installation

### Manual Installation

1. Navigate to your Home Assistant configuration folder.
2. Create the folder `custom_components/personal_weather_station`.
3. Copy all integration files into this folder (`__init__.py`, `sensor.py`, `manifest.json`, etc.).
4. Restart Home Assistant.
5. Add the integration from  **Settings → Devices & Services → Add Integration**


### HACS Installation

This integration is compatible with HACS as a **custom repository** and can be added manually in a few steps:

1. Open HACS in Home Assistant
2. Click the menu (three dots) → **Custom repositories**
3. Add the URL of this GitHub repository
4. Choose **Integration** as the category
5. Click **Add**, then install the integration from HACS
6. Restart Home Assistant.
7. Add the integration from  **Settings → Devices & Services → Add Integration**

---

## Weather station configuration

### Manual configuration

**Important:** In your weather station configuration, make sure to set the URL to point to your Home Assistant instance:  

```
http://<home_assistant_ip>:8123
```

#### HTTP Endpoint

The integration exposes an HTTP endpoint that your weather station can call:

```
http://<home_assistant_ip>:8123/weatherstation/updateweatherstation.php
```

Query parameters format:

```
?ID=<device_id>&temperature=22.5&humidity=55
```

- `ID`: Unique device ID (required).  
- Other parameters: Sensor keys matching `SENSOR_LIST`.

### WSLink configuration

Make sure to set these parameters in the WSLink application:

- **URL**: ```http://<HOME_ASSISTANT_IP>:8123```
- **Sender ID**: `any identifier (e.g., my_station) — this will become the device ID in Home Assistant
- **Station Key**: you can leave it blank (not used)
- **Upload** Interval: any interval you want, e.g., 60 seconds

This configuration will allow WSLink to send weather data correctly to Home Assistant via the PWS integration.

### Config Flow

- This integration **does not support the UI config flow** (`config_flow: false`).  
- All setup is done automatically upon HTTP requests.

---

## Usage

1. Your weather station sends HTTP GET requests with sensor data to Home Assistant.
2. The integration checks if the device exists. If not, it creates a new device.
3. Each sensor in the request is either created (if new) or updated (if existing).
4. All sensors appear in Home Assistant under the device `Weather Station <ID>`.

### Example HTTP Request

```text
http://192.168.1.23:8123/weatherstation/updateweatherstation.php?ID=my_station&temperature=22.5&humidity=55
```

- Creates/updates sensors `temperature` and `humidity` for device `my_station`.

---

## Entity Creation

The integration automatically creates entities based on the parameters received in each HTTP request. 
When a new parameter is sent that does not yet exist as a sensor in Home Assistant, the integration will generate a new entity for it under the device corresponding to the ID of the request.

Multiple requests can be sent sequentially to create new entities. You do not need to include all parameters in a single request. Any new parameter sent in a later request will automatically create its corresponding entity.

Entities have no default values, as they are created only when a value is received from the station.
They always reflect the last received value.

### Example:

HTTP request:
```http://192.168.1.23:8123/weatherstation/updateweatherstation.php?ID=my_station&tempf=72&humidity=55&winddir=180```

Will create the `my_station` device. Following entities will be attached to this device:
- `my_station.tempf`
- `my_station.humidity`
- `my_station.winddir`

Subsequent requests with new parameters (e.g., rainin=0.1) will create additional entities automatically without manual configuration.

## Entity Update

When a value is received from the weather station, the integration automatically updates the corresponding entity:

- If the value contains a decimal point (.), it is converted to a float.
- If the value is a whole number, it is converted to an int.
- If the value cannot be converted to a number, it is stored as a string.

This ensures that each entity always reflects the last received value in the appropriate type, while preserving non-numeric values as strings.

**Note:** This integration does not perform unit conversions itself. All values are stored as received in Weather Underground format (°F, mph, inHg, inches), and Home Assistant handles any necessary conversion to metric units if your system is configured in metric mode

---

## Unloading / Cleanup

When the integration is removed:

- All device data is cleared from Home Assistant memory.
- All references to `add_entities` are removed.
- Sensor platform is unloaded cleanly.

---

## Dependencies

- Python library: `aiohttp`
- Home Assistant components: `http`, `sensor`

---

## Development

- Code is in `custom_components/personal_weather_station`.
- Main files:
  - `__init__.py`: Integration setup and HTTP endpoint.
  - `sensor.py`: Sensor and device classes (`PwsSensor` and `PwsDevice`).
  - `const.py`: `DOMAIN` and `SENSOR_LIST`.
  - `manifest.json`: Integration metadata.

---

## Contributing

Contributions are welcome! Please open issues or pull requests on GitHub.

- Add new sensors to `SENSOR_LIST` for additional weather data.
- Improve error handling or authentication for the HTTP endpoint.
- Optimize performance or add async support where possible.

---

## License
![License](https://img.shields.io/badge/license-Public%20Domain-blue)
<br>
This software is released into the **public domain** under the [Unlicense](https://unlicense.org):



