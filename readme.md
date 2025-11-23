# Personal Weather Station (PWS) Integration for Home Assistant

![License](https://img.shields.io/badge/license-Public%20Domain-blue)

This custom Home Assistant integration allows you to receive real-time data from your **Personal Weather Station** and expose it as sensors inside Home Assistant. It uses an HTTP endpoint to receive sensor updates and automatically creates or updates sensors for temperature, humidity, pressure, and more.

---

## Features

- Receive weather station data via HTTP requests.
- Automatically create new sensors for any supported data key.
- Update existing sensors in real-time.
- Fully compatible with Home Assistant sensor platform.
- No authentication required (optional to add in `MeteoView` if desired).

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

Other stations may also work if they can send HTTP GET requests with query parameters matching the keys defined in `SENSOR_LIST`.  
Feel free to try your own weather station and see if it works, and consider contributing any new compatible models to the project!

---

## Installation

### Manual Installation

1. Navigate to your Home Assistant configuration folder.
2. Create the folder `custom_components/personal_weather_station`.
3. Copy all integration files into this folder (`__init__.py`, `sensor.py`, `manifest.json`, etc.).
4. Restart Home Assistant.


### HACS Installation

Currently, this integration is **not yet available in HACS**, but once added, it will allow users to install and update it directly through HACS with a single click.  
For now, manual installation as described above is fully supported.

---

## Configuration

**Important:** In your weather station configuration, make sure to set the URL to point to your Home Assistant instance:  

```
http://<YOUR_IP>:8123
```

### HTTP Endpoint

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

This software is released into the **public domain** under the [Unlicense](https://unlicense.org):

