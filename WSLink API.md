# WSLink data upload API

> For custom weather server with WSLink device
> **VERSION: 0.6**

A faithful transcription of the vendor document *WSLink data upload API*, handed
out by the station's mobile application behind the **WSLink API ⤓** button on the
custom-server screen. It is reproduced here in Markdown so it can be read,
searched and diffed from the repository — the original PDF was opaque to every
one of those.

Every parameter below is covered by this integration; `tests/test_api_document.py`
parses the tables on this page and fails the build if one is ever dropped from
`const.py`, so the document and the code cannot drift apart.

## Feature

WSLink data upload API is for end user to develop their own web-based weather
data server which collecting the weather station data of the WSLink compatible
device(s).

## General information

| | |
| --- | --- |
| Protocol | http or https |
| Port | Default 80 |
| Request method | GET |
| Data format | UTF8 |

## URL formats

| Parameter | Description |
| --- | --- |
| `https://xxxxx.xxx/data/upload.php` | xxxxx.xxx is user define domain name |
| `https://xxxxx.xxx:443/data/upload.php` | URL with define port (example: 443) |

## Upload parameters

The upload parameters depend on the device type. The first parameter carries a
`?`, every following one a `&`.

### General

| Parameter | Description | Data type | Unit |
| --- | --- | --- | --- |
| `&wsid=` | Device ID (user define) | string |  |
| `&wspw=` | Device password (user define) | string |  |
| `&datetime=` | `YYYY-MM-DD+hh%3Amm%3Ass` — e.g. `2000-01-01 10:32:25`, sent as `2000-01-01+10%3A32%3A25`. Can be ignored if the server uses its own time. | string |  |
| `&rbar=` | Relative air pressure | float | hPa |
| `&abar=` | Absolute air pressure | float | hPa |
| `&intem=` | Indoor temperature | float | °C |
| `&inhum=` | Indoor humidity | integer | % |
| `&inbat=` | Console battery level | integer |  |

### Type 1 — outdoor array

| Parameter | Description | Data type | Unit |
| --- | --- | --- | --- |
| `&t1tem=` | Outdoor temperature | float | °C |
| `&t1hum=` | Outdoor humidity | integer | % |
| `&t1feels=` | Feels like temperature | float | °C |
| `&t1chill=` | Wind chill temperature | float | °C |
| `&t1heat=` | Heat index temperature | float | °C |
| `&t1dew=` | Dew point temperature | float | °C |
| `&t1wdir=` | Wind direction | integer | deg |
| `&t1ws=` | Wind speed | float | m/s |
| `&t1ws10mav=` | 10 minutes average wind speed | float | m/s |
| `&t1wgust=` | Wind gust | float | m/s |
| `&t1rainra=` | Rain rate | float | mm/h |
| `&t1rainhr=` | Hourly rainfall | float | mm |
| `&t1raindy=` | Daily rainfall | float | mm |
| `&t1rainwy=` | Weekly rainfall | float | mm |
| `&t1rainmth=` | Monthly rainfall | float | mm |
| `&t1rainyr=` | Yearly rainfall | float | mm |
| `&t1uvi=` | UVI | float |  |
| `&t1solrad=` | Light intensity | float | W/m² |
| `&t1wbgt=` | WBGT temperature | float | °C |
| `&t1bat=` | Outdoor wireless sensor battery level (Normal=1, Low battery=0) | integer |  |
| `&t1cn=` | Outdoor wireless sensor connection status (Connected=1, No connect=0) | integer |  |

### Type 2, 3, 4 — CH1~CH7

| Parameter | Description | Data type | Unit |
| --- | --- | --- | --- |
| `&t234c1tem=` | CH1 temperature | float | °C |
| `&t234c1hum=` | CH1 humidity | integer | % |
| `&t234c1bat=` | CH1 sensor battery level (Normal=1, Low battery=0) | integer |  |
| `&t234c1cn=` | CH1 sensor connection status (Connected=1, No connect=0) | integer |  |
| `&t234c1tp=` | CH1 sensor type | integer |  |
| `&t234c2tem=` | CH2 temperature | float | °C |
| `&t234c2hum=` | CH2 humidity | integer | % |
| `&t234c2bat=` | CH2 sensor battery level (Normal=1, Low battery=0) | integer |  |
| `&t234c2cn=` | CH2 sensor connection status (Connected=1, No connect=0) | integer |  |
| `&t234c2tp=` | CH2 sensor type | integer |  |
| `&t234c3tem=` | CH3 temperature | float | °C |
| `&t234c3hum=` | CH3 humidity | integer | % |
| `&t234c3bat=` | CH3 sensor battery level (Normal=1, Low battery=0) | integer |  |
| `&t234c3cn=` | CH3 sensor connection status (Connected=1, No connect=0) | integer |  |
| `&t234c3tp=` | CH3 sensor type | integer |  |
| `&t234c4tem=` | CH4 temperature | float | °C |
| `&t234c4hum=` | CH4 humidity | integer | % |
| `&t234c4bat=` | CH4 sensor battery level (Normal=1, Low battery=0) | integer |  |
| `&t234c4cn=` | CH4 sensor connection status (Connected=1, No connect=0) | integer |  |
| `&t234c4tp=` | CH4 sensor type | integer |  |
| `&t234c5tem=` | CH5 temperature | float | °C |
| `&t234c5hum=` | CH5 humidity | integer | % |
| `&t234c5bat=` | CH5 sensor battery level (Normal=1, Low battery=0) | integer |  |
| `&t234c5cn=` | CH5 sensor connection status (Connected=1, No connect=0) | integer |  |
| `&t234c5tp=` | CH5 sensor type | integer |  |
| `&t234c6tem=` | CH6 temperature | float | °C |
| `&t234c6hum=` | CH6 humidity | integer | % |
| `&t234c6bat=` | CH6 sensor battery level (Normal=1, Low battery=0) | integer |  |
| `&t234c6cn=` | CH6 sensor connection status (Connected=1, No connect=0) | integer |  |
| `&t234c6tp=` | CH6 sensor type | integer |  |
| `&t234c7tem=` | CH7 temperature | float | °C |
| `&t234c7hum=` | CH7 humidity | integer | % |
| `&t234c7bat=` | CH7 sensor battery level (Normal=1, Low battery=0) | integer |  |
| `&t234c7cn=` | CH7 sensor connection status (Connected=1, No connect=0) | integer |  |
| `&t234c7tp=` | CH7 sensor type | integer |  |

### Type 5 — lightning

| Parameter | Description | Data type | Unit |
| --- | --- | --- | --- |
| `&t5lst=` | Last Lightning strike time | integer |  |
| `&t5lskm=` | Lightning distance | integer | km |
| `&t5lsf=` | Lightning strike count last 1 hours | integer |  |
| `&t5ls5mtc=` | Lightning count total of during 5 minutes | integer |  |
| `&t5ls30mtc=` | Lightning count total of during 30 minutes | integer |  |
| `&t5ls1htc=` | Lightning count total of during 1 Hour | integer |  |
| `&t5ls1dtc=` | Lightning count total of during 1 day | integer |  |
| `&t5lsbat=` | Lightning sensor battery (Normal=1, Low battery=0) | integer |  |
| `&t5lscn=` | Lightning sensor connection (Connected=1, No connect=0) | integer |  |

### Type 6 — water leak, CH1~CH7

| Parameter | Description | Data type | Unit |
| --- | --- | --- | --- |
| `&t6c1wls=` | Water leak sensor CH1 (Leak=1, No leak=0) | integer |  |
| `&t6c1bat=` | Water leak sensor CH1 battery (Normal=1, Low battery=0) | integer |  |
| `&t6c1cn=` | Water leak sensor CH1 connection (Connected=1, No connect=0) | integer |  |
| `&t6c2wls=` | Water leak sensor CH2 (Leak=1, No leak=0) | integer |  |
| `&t6c2bat=` | Water leak sensor CH2 battery (Normal=1, Low battery=0) | integer |  |
| `&t6c2cn=` | Water leak sensor CH2 connection (Connected=1, No connect=0) | integer |  |
| `&t6c3wls=` | Water leak sensor CH3 (Leak=1, No leak=0) | integer |  |
| `&t6c3bat=` | Water leak sensor CH3 battery (Normal=1, Low battery=0) | integer |  |
| `&t6c3cn=` | Water leak sensor CH3 connection (Connected=1, No connect=0) | integer |  |
| `&t6c4wls=` | Water leak sensor CH4 (Leak=1, No leak=0) | integer |  |
| `&t6c4bat=` | Water leak sensor CH4 battery (Normal=1, Low battery=0) | integer |  |
| `&t6c4cn=` | Water leak sensor CH4 connection (Connected=1, No connect=0) | integer |  |
| `&t6c5wls=` | Water leak sensor CH5 (Leak=1, No leak=0) | integer |  |
| `&t6c5bat=` | Water leak sensor CH5 battery (Normal=1, Low battery=0) | integer |  |
| `&t6c5cn=` | Water leak sensor CH5 connection (Connected=1, No connect=0) | integer |  |
| `&t6c6wls=` | Water leak sensor CH6 (Leak=1, No leak=0) | integer |  |
| `&t6c6bat=` | Water leak sensor CH6 battery (Normal=1, Low battery=0) | integer |  |
| `&t6c6cn=` | Water leak sensor CH6 connection (Connected=1, No connect=0) | integer |  |
| `&t6c7wls=` | Water leak sensor CH7 (Leak=1, No leak=0) | integer |  |
| `&t6c7bat=` | Water leak sensor CH7 battery (Normal=1, Low battery=0) | integer |  |
| `&t6c7cn=` | Water leak sensor CH7 connection (Connected=1, No connect=0) | integer |  |

### Type 8 — PM2.5 / PM10

| Parameter | Description | Data type | Unit |
| --- | --- | --- | --- |
| `&t8pm25=` | PM2.5 concentration | integer | ug/m³ |
| `&t8pm10=` | PM10 concentration | integer | ug/m³ |
| `&t8pm25ai=` | PM2.5 AQI | integer |  |
| `&t8pm10ai=` | PM10 AQI | integer |  |
| `&t8bat=` | PM sensor battery level (0~5) remark: 5 is full | integer |  |
| `&t8cn=` | PM sensor connection (Connected=1, No connect=0) | integer |  |

### Type 9 — HCHO / VOC

| Parameter | Description | Data type | Unit |
| --- | --- | --- | --- |
| `&t9hcho=` | HCHO concentration | integer | ppb |
| `&t9voclv=` | VOC level (1~5) 1 is the highest level, 5 is the lowest VOC level | integer |  |
| `&t9bat=` | HCHO / VOC sensor battery level (0~5) remark: 5 is full | integer |  |
| `&t9cn=` | HCHO / VOC sensor connection (Connected=1, No connect=0) | integer |  |

### Type 10 — CO₂

| Parameter | Description | Data type | Unit |
| --- | --- | --- | --- |
| `&t10co2=` | CO₂ concentration | integer | ppm |
| `&t10bat=` | CO₂ sensor battery level (0~5) remark: 5 is full | integer |  |
| `&t10cn=` | CO₂ sensor connection (Connected=1, No connect=0) | integer |  |

### Type 11 — CO

| Parameter | Description | Data type | Unit |
| --- | --- | --- | --- |
| `&t11co=` | CO concentration | integer | ppm |
| `&t11bat=` | CO sensor battery level (0~5) remark: 5 is full | integer |  |
| `&t11cn=` | CO sensor connection (Connected=1, No connect=0) | integer |  |

### API version

| Parameter | Description | Data type | Unit |
| --- | --- | --- | --- |
| `&apiver=` | API version | float |  |
## Compatible sensor list

| Sensor type | Channel | Compatible sensors types |
| --- | --- | --- |
| Type 1 | | 3-in-1 raingauge<br>3-in-1 wind speed sensor<br>5-in-1 Outdoor sensor<br>7-in-1 Outdoor sensor<br>8-in-1 Outdoor WBGT sensor |
| Type 2, 3, 4 | Ch1~7 | Thermo-hygrometer sensor<br>Pool sensor<br>Soil moisture & temperature |
| Type 5 | | Lightning sensor |
| Type 6 | Ch1~7 | Water leak sensor |
| Type 8 | | PM2.5 / 10 sensor |
| Type 9 | | HCHO with VOC sensor |
| Type 10 | | CO₂ sensor |
| Type 11 | | CO sensor |

## Upload data example

```
https://xxxxx.xxx/data/upload.php?wsid=wsabcde123&wspw=a123456789&datetime=2000-01-01+10%3A32%3A25&rbar=1008.8&abar=990.5&intem=25.8&inhum=22&inbat=1&t1tem=38&t1hum=88&t1wdir=359&t1ws=40.1&t1ws10mav=20.9&t1wgust=49.9&t1rainra=20.8&t1rainhr=10&t1raindy=33.5&t1rainwy=15&t1rainmth=30.8&t1rainyr=40.5&t1uvi=8.8&t1solrad=679&t1bat=1&t1cn=1&t234c1tem=35.9&t234c1hum=56&t1feels=&t1chill=38&t1heat=&t1dew=33.9&t1wbgt=42.1&t234c1bat=0&t234c1cn=0&t234c1tp=2&t234c2tem=35.9&t234c2hum=56&t234c2bat=2&t234c2cn=0&t234c2tp=2&t234c3tem=35.9&t234c3hum=56&t234c3bat=1&t234c3cn=0&t234c3tp=2&t234c4tem=40.1&t234c4hum=39&t234c4bat=1&t234c4cn=0&t234c4tp=3&t234c5tem=23.6&t234c5hum=33&t234c5bat=0&t234c5cn=0&t234c5tp=3&t234c6tem=35.9&t234c6hum=57&t234c6bat=1&t234c6cn=0&t234c6tp=4&t234c7tem=18.1&t234c7hum=19&t234c7bat=2&t234c7cn=0&t234c7tp=4&t5lst=9999&t5lskm=40.1&t5lsf=30&t5ls5mtc=65536&t5ls30mtc=65536&t5ls1htc=6553336&t5ls1dtc=65536&t5lsbat=1&t5lscn=1&t6c1wls=1&t6c1bat=0&t6c1cn=0&t6c2wls=1&t6c2bat=0&t6c2cn=0&t6c3wls=1&t6c3bat=0&t6c3cn=0&t6c4wls=1&t6c4bat=0&t6c4cn=0&t6c5wls=1&t6c5bat=0&t6c5cn=0&t6c6wls=1&t6c6bat=0&t6c6cn=0&t6c7wls=1&t6c7bat=0&t6c7cn=0&t8pm25=450.5&t8pm10=300.5&t8pm25ai=999&t8pm10ai=88&t8bat=0&t8cn=0&t9hcho=1000&t9voclv=3&t9bat=0&t9cn=0&t10co2=400&t10bat=0&t10cn=0&t11co=500.0&t11bat=5&t11cn=1&apiver=1.00
```

Note the two parameters sent **with an empty value** — `&t1feels=&` and
`&t1heat=&`. A station reports a sensor it cannot compute this way, so a server
must accept an empty value rather than fail on it. The same string is kept
verbatim in `tests/wslink_example_payload.txt` and replayed by the test suite.

## Server response codes

| Code | Description |
| --- | --- |
| 200 | Success |
| 400 | Bad request |
| 401 | Incorrect device id or device password |
| 404 | Too many request |
| 405 | Incorrect data format |

All five are implemented. 404 is answered to a station posting more than
`RATE_LIMIT_REQUESTS` times within `RATE_LIMIT_WINDOW` seconds, which sits well
above the shortest upload interval these stations offer. 405 is answered only
when every recognised parameter in a payload failed to be read — a station
sending parameters this document does not list is answered 200, because a newer
API version is not a malformed request.

## Revision history

| Version | Description | Date |
| --- | --- | --- |
| 0.1 | Draft release | 28 Apr 2023 |
| 0.2 | Change time parameter name and format<br>Add feels like, heat index, wind chill and dewpoint parameter<br>Updated the API example<br>Adjust the document format | 12 May 2023 |
| 0.3 | Add description for the sensor connection | 13 Jun 2023 |
| 0.4 | Add compatible sensor list | 4 Jul 2023 |
| 0.5 | Add leak status description for the leak sensors<br>Add VOC level description | 15 Sep 2023 |
| 0.6 | Add WBGT temperature parameter<br>Add compatible sensor types | 7 Nov 2023 |
