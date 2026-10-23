<img src="https://raw.githubusercontent.com/home-assistant/brands/refs/heads/master/custom_integrations/personal_weather_station/icon%402x.png" alt="" align="right" height="177">

# Personal Weather Station (PWS)

**🇬🇧 English** · [🇫🇷 Français](docs/readme.fr.md)

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=flat-square)](https://github.com/hacs/integration)
[![GH-downloads](https://img.shields.io/github/downloads/MaxensF/personal_weather_station/total?style=flat-square)](https://github.com/MaxensF/personal_weather_station/releases)
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=MaxensF&repository=personal_weather_station&category=integration)

Turn Home Assistant into the server your weather station uploads to. No cloud, no
account, no polling: the station posts straight to your instance, and its
devices and sensors appear on their own.

---

## How it works, in one paragraph

Most integrations go and fetch data. This one does the opposite: it opens two
HTTP endpoints and waits. Your station — configured to upload to your Home
Assistant address instead of Weather Underground — posts its readings every
minute or so, and the integration creates a device for it and a sensor for every
value it recognises. **That is why there is no "add device" button:** the station
creates its own.

Both protocols are supported and can be mixed on the same instance:

| Protocol | Endpoint | Units |
|---|---|---|
| Weather Underground | `/weatherstation/updateweatherstation.php` | imperial (°F, mph, inHg, in) |
| WSLink | `/data/upload.php` | metric (°C, m/s, hPa, mm) |

Each key is declared with the unit its protocol uses, so Home Assistant converts
to whatever your system is set to. A WSLink wind speed sent in m/s shows up in
km/h on a metric system — that is correct, not a bug.

---

## Features

- **Guided setup.** Adding the integration ends on the exact settings to enter in
  your station, your Home Assistant address included. Until a station has posted,
  a prompt waits with you for its first upload.
- **170 sensors** across both protocols: temperature, humidity, pressure, wind,
  rain, lightning, air quality, multi-channel sensors, batteries.
- **North calibration.** Realign a vane that was not mounted precisely, without
  touching the hardware.
- **A station that stops reporting is marked unavailable** instead of showing a
  frozen reading forever.
- **A `Last update` diagnostic** per station, readable precisely when the station
  has gone quiet.
- **Water leak and connection readings as binary sensors**, usable with the
  standard leak cards and alerts.
- **Entities and values survive a restart** — no waiting for the next upload.
- **Rejected stations are reported** in Repairs rather than failing silently.
- **Available in all 64 languages Home Assistant supports.**
- Optional station key.

---

## Requirements

> [!IMPORTANT]
> **Home Assistant 2025.3.0 or later.**

Upgrading from an earlier release of this integration is safe: nothing is renamed
or removed on its own. See the [changelog](CHANGELOG.md).

---

## Installation

### HACS

This integration is in the default HACS store.

1. Open HACS, search for **Personal Weather Station**, download it.
2. Restart Home Assistant.
3. **Settings → Devices & Services → Add Integration**, search for it.
4. Set a **station key** if you want one, or leave it blank to accept any station.

The last screen tells you exactly what to enter in your station. The same
instructions stay available afterwards from the integration's ⚙️ →
*How to point a station at Home Assistant*.

### Manual

Copy `custom_components/personal_weather_station/` into your Home Assistant
`config/custom_components/`, restart, then add the integration as above.

---

## Pointing your station at Home Assistant

### Bresser stations, with the WSLink app

Your station must already be set up in the app and running an up-to-date
firmware.

> [!WARNING]
> **Have the values ready before you open the app, and do not linger on these
> screens.** The station tends to drop its WiFi connection if you spend too long
> entering the server settings — and all the more so if you sit in the menu
> waiting for the data to turn up in Home Assistant.
>
> Copy the URL, station ID and key first, fill the form in one go, and press
> **Confirm & Exit** straight away. Watch for the data on the Home Assistant side
> afterwards, not from the app.

**1. Open your station's settings**

<img src="custom_components/personal_weather_station/images/wslink-1-your-device.jpeg" width="260" alt="The WSLink device list, with the settings gear on the station">

**2. Weather server**

<img src="custom_components/personal_weather_station/images/wslink-2-settings.jpeg" width="260" alt="The station settings, with Weather server highlighted">

**3. Other Server**

<img src="custom_components/personal_weather_station/images/wslink-3-weather-server.jpeg" width="260" alt="The weather service list, with Other Server highlighted">

Weather Underground and Weathercloud upload to those services. **Other Server**
is the one that lets you point the station at your own Home Assistant.

**4. Fill in the server**

<img src="custom_components/personal_weather_station/images/wslink-4-other-server.jpeg" width="260" alt="The Other Server form, filled in">

| Field | What to enter |
|---|---|
| **URL** | Your Home Assistant address and port, **without `http://` or `https://`** — for example `192.168.1.100:8123`. Use an address your station can reach **on your own network**; there is no reason to open a port to the internet so a weather station can upload. If your station cannot resolve names, use the IP. |
| **Station ID** | Anything you like. It becomes the device name in Home Assistant. |
| **Station key** | The key you set in the integration. Leave it empty if you left that blank. |
| **Upload interval** | 1 minute is a good default. |
| **API type** | **WSLink** — see below. |
| **Upload** | Enabled by default — leave it on. |

> [!TIP]
> **Prefer WSLink over WUnderground API if your station offers both.** Weather
> Underground is an older protocol with only **4 slots** for extra sensors, and
> Bresser stations squeeze every extra channel — even a pool thermometer — into
> those soil fields. A station with 5 or more extra sensors simply cannot express
> them: the surplus never reaches Home Assistant, silently.
>
> | | Weather Underground | WSLink |
> |---|---|---|
> | Recognised parameters | 55 | 108 |
> | Extra sensor channels | 4 | 7 |
> | Water leak detectors | — | 7 |
> | Lightning, PM, HCHO/VOC, CO₂, CO | — | yes |
>
> Both work, and both are supported here. WUnderground API is the right choice
> only when your station does not offer WSLink.

The **WSLink API ⤓** button below hands you the protocol documentation, if you
want to know exactly what your station sends. It is transcribed in
[WSLink API.md](WSLink%20API.md) too, down to the last parameter.

Then press **Save**.

**5. Confirm & Exit**

<img src="custom_components/personal_weather_station/images/wslink-5-confirm-and-exit.jpeg" width="260" alt="The station settings, with Confirm and Exit highlighted">

> [!IMPORTANT]
> **This is the step that actually writes the settings to the station.** Pressing
> *Save* on the previous screen changes nothing on its own. Once you press
> **Confirm & Exit**, Home Assistant receives data within seconds and your sensors
> appear.

> [!NOTE]
> Some Bresser firmwares from **3.02** onwards refuse plain HTTP. Home Assistant
> then has to serve HTTPS on an address your station can reach.

### Any station supporting the PWS protocol

Point it at your Home Assistant address and set:

- **ID** — any identifier; it becomes the device name.
- **Password / station key** — the one you set in the integration, or nothing.

The endpoint accepts a plain GET:

```
http://<home_assistant>:8123/weatherstation/updateweatherstation.php?ID=my_station&PASSWORD=<key>&tempf=72&humidity=55
```

- `ID` (or `wsid`) is **required** — a request without it is answered `400`.
- `PASSWORD` (or `wspw`) is checked only if you set a key; a wrong one gets `401`
  and raises a repair.
- Unknown keys are ignored. A key sent with an **empty value** simply leaves its
  sensor `unknown` — the rest of the request is processed normally.

### Stations that cannot change their upload URL

Some stations only ever talk to Weather Underground. Two ways around it:

- **The WSLink add-on** by @schizza, which intercepts that traffic and forwards
  it to Home Assistant: [wslink-addon](https://github.com/schizza/wslink-addon).
- **By hand**, by intercepting the traffic yourself — see
  [issue #20](https://github.com/MaxensF/personal_weather_station/issues/20).

> [!NOTE]
> Version **0.0.7** of the add-on broke the upload flow. It was fixed in **0.0.8**
> and the add-on has moved on since, so simply use a current version. Running a
> fork is no longer necessary.

---

## Calibrating true north

A weather station has to be oriented when it is installed. If the vane could not
be aligned precisely, every wind direction is off by a fixed amount — and there
is no need to climb back up to fix it.

Once a station has reported a wind direction, three controls appear on its device
page:

| Entity | What it does |
|---|---|
| `number.<station>_wind_direction_offset` | The rotation applied to every direction, 0-359°. Adjust it by hand at any time. |
| `button.<station>_set_north_from_current` | Takes the direction being reported right now as north. |
| `button.<station>_reset_wind_offset` | Drops the calibration. |

**Procedure:** hold the vane pointing at **geographic** north — not magnetic
north; check your local declination — wait for the station to upload, then press
*Set north from current*. The offset appears in the number entity and every
direction sensor follows.

A diagnostic sensor `Wind direction (raw)` keeps showing the uncorrected reading,
so you can always check a calibration or redo one. The offset is stored in the
integration's options, not as a restored state, so a recorder purge cannot lose
it.

> [!NOTE]
> The offset applies to values as they arrive. History already recorded is not
> rewritten.

Buttons have no confirmation step in Home Assistant. If you would rather be asked
first, add one in your dashboard:

```yaml
type: button
entity: button.my_station_set_north_from_current
confirmation:
  text: Is the vane pointing north?
```

---

## Knowing whether a station is alive

Because the integration only ever receives data, it has no other way to notice a
station that stopped reporting.

- Every station gets a **`Last update`** diagnostic showing when it last posted.
  It stays readable even when the station is offline, which is exactly when you
  need it. It uses the timestamp from the payload when the station clock looks
  trustworthy, and the server time otherwise.
- After a configurable delay — **Mark as unavailable after**, 15 minutes by
  default, `0` to disable — the station's sensors switch to *unavailable* instead
  of showing a frozen reading.

That second point matters more than it looks: an automation acting on a
temperature has no way of telling a real value from one frozen three days ago.

---

## Status readings

Water leak and connection readings arrive as `1` or `0`. They are exposed as
**binary sensors**, so a leak detector reads *Wet* / *Dry* and works with the
standard leak cards and alerts, and a connection status reads *Connected* /
*Disconnected*.

Battery levels are deliberately **not** binary sensors. Even the ones the
protocol reports as `Normal=1 / Low=0` stay percentages, because that is what
Home Assistant's low-battery alerts and long-term statistics work on.

---

## When nothing shows up

A station that is misconfigured looks exactly like a station that has not posted
yet: an empty page. To tell them apart, rejected requests raise a repair in
**Settings → System → Repairs**:

| Repair | Meaning |
|---|---|
| **Wrong station key** | The key in the station does not match the one set here. Names the station and the source address. |
| **No station identifier** | The station posted without an `ID` / `wsid`. |

A repair disappears on its own once that station is accepted.

If nothing appears at all — not even a repair — the requests are not reaching
Home Assistant. Check the URL, the port, and whether your firmware requires
HTTPS. And check you pressed **Confirm & Exit**.

Turning on **Log every incoming request** in the options writes the full content
of each request to the log while you are setting a station up.

> [!NOTE]
> Behind the WSLink add-on, every station reaches Home Assistant through the
> proxy, so the address shown in a repair is the proxy's unless you enable
> `forward_real_ip` in the add-on and set `trusted_proxies` in Home Assistant. The
> station identifier is reliable either way.

---

## Upgrading an older installation

Two things changed for new stations that would move entities for existing ones.
Neither happens on its own: each is offered as a repair you can ignore.

| Repair | What it does | What it costs |
|---|---|---|
| **Shorten the entity IDs** | Renames `sensor.x_x_outdoor_temperature` to `sensor.x_outdoor_temperature` | History and long-term statistics follow the rename. **Automations, scripts, scenes and dashboards do not** — update them yourself. |
| **Convert status readings** | Turns the 27 connection and leak sensors into binary sensors | Changing platform is not a rename: the old entities are removed and rebuilt, and **their raw history is lost**. These readings carry no long-term statistics. Anything pointing at them must be updated. |

Up to version 1.0.8 the station name appeared **twice** in every entity ID, as in
`sensor.my_station_my_station_outdoor_temperature`. Stations already known to
Home Assistant keep those IDs — including for sensors that appear later, so one
station never mixes two naming styles.

Entity IDs are built from the **English** sensor name whatever your language, so a
dashboard survives being shared between users of different languages, even though
the displayed names follow each user's language.

---

## Removing a station

A station appears on its own the first time it posts, so a typo in the station ID
creates a device you did not want. Such a device can be deleted from its page
(**⋮ → Delete**); it comes back automatically if that station posts again.

---

## Compatible weather stations

Confirmed working:

- **Bresser** — 7002586, 7002582, 7002620, 7003300, 7003400, 7004406
- **YOUSHIKO** — YC9471

Any station able to send HTTP GET requests with parameters matching
[`SENSOR_LIST`](./custom_components/personal_weather_station/const.py) should
work. If yours does, a pull request adding it to this list is welcome.

---

## Development

```bash
pip install -r requirements_test.txt
pytest tests/ -v
```

| Path | What it holds |
|---|---|
| `__init__.py` | Setup and the HTTP endpoints |
| `models.py` | `PwsDevice` and the shared runtime |
| `entity.py` | Base entity: naming, availability, state writing |
| `sensor.py` `binary_sensor.py` `number.py` `button.py` | The four platforms |
| `registry.py` | Rebuilding entities from the registries on startup |
| `migration.py` `repairs.py` | The two opt-in migrations |
| `instructions.py` | The setup instructions, worked out for this instance |
| `normalizer.py` | Value parsing, battery scaling, wind offset |
| `const.py` | `DOMAIN` and `SENSOR_LIST` |
| `strings.json` + `translations/` | Every user-visible string |

See [CONTRIBUTING.md](CONTRIBUTING.md) — in particular for adding a sensor or
improving a translation, neither of which is edited by hand.

---

## License

Released into the **public domain** under the [Unlicense](https://unlicense.org).
