# Changelog

## 1.2.0

### Fixed

- **A `0~5` battery level no longer reads as 0%.** The six levels were spread
  evenly over 0-100, so a sensor merely in its lowest band reported a flat
  battery — and stayed there for months while working perfectly well. Each
  level is now reported as the middle of the band it stands for: 5, 20, 40, 60,
  80, 95. Only the PM2.5/10, HCHO/VOC, CO₂ and CO sensors use that scale; the
  other batteries are binary and unchanged.

- **The batteries had no unit, so they read as a bare number.** `Console
  battery level 0` could mean empty or fine, and Home Assistant logs a warning
  for a `battery` sensor without `%`. The readings were already normalised to
  0-100; the unit was simply never declared. All 21 of them now say `0 %`.
  Nothing about the values changes, but Home Assistant will offer to relabel
  the recorded statistics of an existing installation, since it stored them
  without a unit.
- **PM2.5 and PM10 AQI are declared as AQI.** Home Assistant has a device class
  for the index, which gives them the right icon and grouping instead of
  leaving two more unlabelled numbers on the dashboard.
- **The VOC level says what it means.** The API defines it as `1~5` with **1
  the highest** concentration and 5 the lowest — so the scale runs backwards,
  and a bare `3` told you neither how far it went nor which end was bad.
  Reporting `3 / 5` would have read the wrong way round just as easily. It is
  now one of *Very low* to *Very high*, translated into all 64 languages, and
  a code outside the documented range reads as unknown rather than being
  guessed at. The sensor changes from a number to a named state, so its
  recorded history does not carry over.
- A test pinned a literal date. The integration ignores a station clock more
  than a day out, so `test_dateutc_is_used_as_last_seen` passed on the day it
  was written and failed every day after. It builds its timestamp relative to
  now.
- **The setup wizard was telling you to pick the wrong API.** It said
  *WUnderground API* while the readme and the repairs recommend *WSLink API*,
  which carries roughly twice as many readings and seven channels instead of
  four. All 64 languages are corrected.
- **`strings.json` failed Home Assistant's own validation.** hassfest rejects a
  literal URL in a translated string; the link to the issue tracker in the
  dropped-parameters repair is now a placeholder, and the repair also carries a
  proper *Learn more* link.
- The integration declares a `CONFIG_SCHEMA`, which hassfest asks of anything
  defining `async_setup`.
- The test workflow could never run: `cache: pip` looked for a `requirements.txt`
  that does not exist here and failed the job before the first test.
- The HACS validation workflow no longer runs on forks. Its two failures there —
  no repository topics, issues not enabled — are properties of the fork rather
  than of the code, so it could never pass and only mailed the fork's owner on
  every push. The daily stale run is skipped on forks for the same reason.

### Added

- **The Normal/Low batteries are binary sensors now.** Seventeen of them —
  outdoor array, console, each channel, lightning, leak detectors — report
  nothing but "Normal" or "Low battery", which a percentage could only render
  as 100% or 0%. New stations get a plain on/off `binary_sensor`, on meaning the
  battery is fine; existing stations keep their numeric sensors until they
  accept the repair. The 0~5 levels of the air quality sensors stay percentages,
  where six steps are worth expressing.
- Batteries and the API version sit with the diagnostics now, rather than among
  the readings about the weather.
- **A `Station online` binary sensor**, one per station. Every other connection
  status comes from the station itself, which says nothing about the console —
  the console is what does the posting, so when it stops there is nobody left to
  report it. This one is derived from the availability timeout instead, and
  stays available precisely when the station is not.
- **The setup wizard is now a walkthrough, with the screenshots.** Five screens
  matching the station app's own, one picture each, ending on Home Assistant
  waiting with you for the first upload — and saying so explicitly when nothing
  arrives, rather than dropping you on an empty page.
- The endpoints start listening from the wizard's first screen, not from the
  moment it starts waiting. These stations drop off Wi-Fi if you linger in their
  settings, so people configure them quickly; an upload that lands while you are
  still reading now counts instead of being thrown away.
- If a station reaches Home Assistant during the wizard with the wrong station
  key, the closing screen says so. That is the single most common setup mistake,
  and it used to look exactly like nothing having arrived at all.
- The station's response codes now follow the vendor specification in full:
  **404** for a station posting more than 60 times a minute, counted per station,
  and **405** when every recognised parameter in a payload fails to be read.
  Parameters the integration does not know deliberately do not count as a format
  error — a station speaking a newer API version is newer, not broken.

### Changed

- `WSLink API.pdf` is replaced by `WSLink API.md`, a full transcription. A test
  parses its tables and fails the build if a documented parameter is dropped from
  the code, or given a unit or battery scale the specification does not state.
  All 108 data parameters are covered.

- **The walkthrough is also reachable from the integration's options**, for
  pointing a second station at Home Assistant. Both flows show the same five
  screens, translated once and shown in both places.
- The walkthrough is translated into all 64 languages Home Assistant ships,
  like the rest of the interface.


## 1.1.0

**Upgrading is safe: no entity is renamed or removed on its own.** The two
changes that would move things are offered in
**Settings → System → Repairs** and only happen if you accept them. Ignore them
to keep everything exactly as it is.

### Fixed

- **A parameter sent with an empty value no longer breaks the whole request.**
  Both protocols send a key with no value when the matching sensor has nothing
  to report — the WSLink API document does it in its own upload example, for
  `t1feels` and `t1heat`. Those raised inside the update loop, which aborted the
  request, lost every parameter that came after them and answered HTTP 500. An
  empty value now simply leaves its sensor `unknown`.
- A single unusable parameter is logged and skipped instead of costing you the
  others; the response reports how many were skipped.
- A request without a station identifier now answers **HTTP 400**. It answered
  200 while the log claimed otherwise.
- A payload arriving while an entity was still being added no longer raises.
- The integration no longer forces its logger to `DEBUG`, which overrode the
  `logger:` configuration.
- The HTTP endpoints are registered once per Home Assistant run instead of
  stacking a new route on every reload.
- The station key is compared with `hmac.compare_digest`, and `PASSWORD` /
  `wspw` are matched case-insensitively like every other parameter.
- Repairs for a rejected request are keyed on the station identifier rather than
  the source address. Behind a proxy such as the WSLink add-on every station
  shares one address, so a station getting through cleared the warning raised for
  another one.
- Replaced the `CONCENTRATION_*` constants deprecated for removal in Home
  Assistant 2027.8. Same values, so nothing changes for existing statistics.

### Added

- **North calibration.** Once a station reports a wind direction, its device page
  gains a `Wind direction offset` number and two buttons,
  *Set north from current* and *Reset wind offset*. Hold the vane at geographic
  north, press, done. A `Wind direction (raw)` diagnostic keeps the uncorrected
  reading so a calibration can be checked or redone. The offset is stored in the
  config entry, not as a restored state, so a recorder purge cannot lose it.
- **Entities and values survive a restart.** They are rebuilt from the registries
  at startup instead of waiting for the station's next upload.
- **A silent station is marked unavailable** instead of showing a frozen reading
  forever. The delay is configurable in the options (15 minutes by default, `0`
  to disable).
- **A `Last update` diagnostic** per station, which stays readable precisely when
  the station has gone quiet. It uses the payload timestamp (`dateutc` or
  `datetime`) when the station clock looks trustworthy.
- **A setup flow that says what to do next.** The integration has no "add device"
  button — the station creates its own device when it posts — so adding it now
  ends on the exact settings to enter, including this instance's address. Until a
  station has posted, a repair brings those instructions back and waits with you
  for the first upload, telling you what to check if nothing arrives. The same
  instructions stay reachable from the integration's own settings, for whenever a
  second station is added.
- **Rejected requests are reported in Repairs**, with the source IP address. A
  wrong station key used to be invisible unless debug logging was on, while
  being the most likely reason for a station never showing up. Rejections are
  also logged at `WARNING` now.
- **A station can be deleted** from its device page. It comes back if it posts
  again.
- **Translations in all 64 languages Home Assistant supports**, sensor names
  included. Eight are reviewed (`de`, `en-GB`, `es`, `es-419`, `fr`, `it`, `pt`,
  `pt-BR`); the rest are complete but await proofreading — corrections welcome,
  see [CONTRIBUTING.md](CONTRIBUTING.md).
- A test suite driving a real Home Assistant instance, run in CI.
- The WSLink walkthrough in the readme is now illustrated, and says the two
  things that were missing: the URL takes no `http://`, and **Confirm & Exit** is
  what actually writes the settings to the station.

### Changed

- **Requires Home Assistant 2025.3.0 or later**, now declared. Earlier releases
  already needed it without saying so.
- Declared as a single-instance integration: one endpoint, one station key, any
  number of stations posting to it.
- Saving the options form no longer reloads the integration, and no longer wipes
  the per-station wind calibration.
- **New stations get shorter entity IDs.** Up to 1.0.8 the station name appeared
  twice, as in `sensor.my_station_my_station_outdoor_temperature`. Stations
  already known to Home Assistant keep their IDs, including for sensors that
  appear later, so one station never mixes two naming styles. Entity IDs stay in
  English whatever your language, so a dashboard survives being shared.
- **New stations expose water leak and connection readings as binary sensors**,
  reading *Wet* / *Dry* and *Connected* / *Disconnected* instead of `1` / `0`.
  Battery levels deliberately stay percentages, which is what the low-battery
  alerts and long-term statistics work on.

### Known fix during development

- The onboarding repair used to close as *successfully repaired* when the wait
  ran out without a station showing up, and disappeared — while its own text
  promised it would stay. Home Assistant deletes a repair for any fix flow
  ending that is not an abort.

### Optional migrations

Both appear in **Settings → System → Repairs** and can be ignored.

| Migration | What it does | What it costs |
|---|---|---|
| Shorten entity IDs | Renames `sensor.x_x_outdoor_temperature` to `sensor.x_outdoor_temperature` | History and long-term statistics follow the rename. **Automations, scripts, scenes and dashboards do not** — update them yourself. |
| Convert status readings | Turns the 27 connection and leak sensors into binary sensors | Changing platform is not a rename: the old entities are removed and rebuilt. **Their raw history is lost** (these readings have no long-term statistics), and anything pointing at them must be updated. |
