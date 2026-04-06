

<image src="https://raw.githubusercontent.com/home-assistant/brands/refs/heads/master/custom_integrations/personal_weather_station/icon%402x.png" alt="image" align="right" height="177"></image>

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration) 

[![GH-downloads](https://img.shields.io/github/downloads/MaxensF/personal_weather_station/total?style=flat-square)](https://github.com/MaxensF/personal_weather_station/releases)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=MaxensF&repository=personal_weather_station&category=integration)




# Personal Weather Station (PWS)

This custom Home Assistant integration allows you to receive real-time data from your **Personal Weather Station** and expose it as sensors inside Home Assistant. It uses an HTTP endpoint to receive sensor updates and automatically creates or updates sensors for temperature, humidity, pressure, and more.

---

## Features

- Receive weather station data via HTTP requests.
- Automatically create new sensors for any supported data key.
- Update existing sensors in real-time.
- Fully compatible with Home Assistant sensor platform.
- Authentication (optional)

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
  - 7002620 
  - 7003300
  - 7003400
  - 7004406

Other stations may also work if they can send HTTP/HTTPS GET requests with query parameters matching the keys defined in `SENSOR_LIST`.  
Feel free to try your own weather station and see if it works, and consider contributing any new compatible models to the project!

### Advanced workaround

Some weather stations do not support natively custom URLs. A workaround is possible, see detailed setup here: [Intercepting Wunderground traffic (issue #20)](../../issues/20)

---

## Quick Start Guide for Bresser Stations with WSLink App

1.  **Install the Integration:** Follow the HACS or Manual installation steps below.
2.  **Add the Integration in Home Assistant:** Go to **Settings → Devices & Services → Add Integration** and search for "Personal Weather Station".
3.  **Configure the Integration:** Enter a **Station Key** (like a password). You will need this for the WSLink app.
4.  **Configure the WSLink App:**
    *   **URL**: Your Home Assistant URL (e.g., `https://my-home-assistant.duckdns.org` or `http://192.168.1.100:8123`).
    *   **Sender ID**: A unique name for your station (e.g., `bresser_station`).
    *   **Station Key**: The same key you entered in the Home Assistant integration.
    *   **API Type**: Select **"WUnderground API"**.
    *   **Upload Interval**: Set your desired update frequency (e.g., 60 seconds).
5.  **Done!** Your weather station data should now appear as a new device in Home Assistant.

> [!IMPORTANT]  
> Bresser stations support either HTTP or HTTPS. If your connection fails, switch to the alternative protocol and update your URL in the WSLink App accordingly.
---

## Installation

### HACS Installation (Recommended)

This integration is available in the default HACS store. You do not need to add a custom repository anymore!

1. Open HACS in Home Assistant
2. Search for **"Personal Weather Station"**
3. Click **Download**, then install the integration
4. Restart Home Assistant
5. Add the integration from **Settings → Devices & Services → Add Integration**


### Manual Installation

1. Navigate to your Home Assistant configuration folder.
2. Create the folder `custom_components/personal_weather_station`.
3. Copy all integration files into this folder (`__init__.py`, `sensor.py`, `manifest.json`, etc.).
4. Restart Home Assistant.
5. Add the integration from  **Settings → Devices & Services → Add Integration**

---

## Weather station configuration

### Manual configuration for any Weather Station supporting the PWS protocol

Set at least these parameters :

- **URL**: ```http://<HOME_ASSISTANT_IP>:8123```
- **ID**: `any identifier (e.g., my_station) — this will become the device ID in Home Assistant
- **Station Key**: a password known only to you.

**Important** : In your weather station configuration, make sure to set the URL to point to your Home Assistant instance

#### HTTP Endpoint

The integration exposes an HTTP endpoint that your weather station can call:

```
http://<home_assistant_ip>:8123/weatherstation/updateweatherstation.php
```

Query parameters format:

```
?ID=<device_id>&PASSWORD=<password>&temperature=22.5&humidity=55
```

- `ID`: Unique device ID (required).
- `PASSWORD`: a password known only to you (this is the station key).
- Other parameters: Sensor keys matching `SENSOR_LIST`.

### Configuration for Weather Stations with WSLink App

Make sure to set these parameters in the WSLink application:

- **URL**: ```http://<HOME_ASSISTANT_IP>:8123``` (for http) or ```<HOME_ASSISTANT_DOMAIN>``` (for https) (depending on weather your Weather Station only supports http or https)
- **Sender ID**: any identifier (e.g., my_station) — this will become the device ID in Home Assistant
- **Station Key**: a password known only to you
- **Upload** Interval: any interval you want, e.g., 60 seconds
- **API Type**: Note that some stations have this field. In that case, make sure to select "WUnderground API".

This configuration will allow your Weather Station to send weather data correctly to Home Assistant via the PWS integration. As this integration only allows you to configure one station key, all of your Weather Stations should use the same.

> [!IMPORTANT]  
> Bresser weather stations running firmware version **3.02** or later require SSL.
> With these versions, using HTTP will cause a silent failure, meaning no data will be transmitted.
> Note: There might be versions prior to 3.02 that also require SSL, but 3.02 is the first known version that definitively needs it.
> Home Assistant must therefore be configured with SSL enabled, and the URL configured in WSLink must use https instead of http.

### Config Flow
- Add a new weather station using its station key. Ensure that this key matches the one configured in the weather station settings or leave it blank to accept any station key.
- All setup is done automatically upon HTTP(S) requests.

---

## Usage

1. Your weather station sends HTTP GET requests with sensor data to Home Assistant.
2. The integration checks if the device exists. If not, it creates a new device.
3. Each sensor in the request is either created (if new) or updated (if existing).
4. All sensors appear in Home Assistant under the device `Weather Station <ID>`.

### Example HTTP Request

```text
http://192.168.1.23:8123/weatherstation/updateweatherstation.php?ID=my_station&PASSWORD=<password>&temperature=22.5&humidity=55
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

> [!NOTE] 
> This integration does not perform unit conversions itself. All values are stored as received in Weather Underground format (°F, mph, inHg, inches), and Home Assistant handles any necessary conversion to metric units if your system is configured in metric mode

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
- Improve error handling
- Optimize performance or add async support where possible.

---

## License
![License](https://img.shields.io/badge/license-Public%20Domain-blue)
<br>
This software is released into the **public domain** under the [Unlicense](https://unlicense.org):
