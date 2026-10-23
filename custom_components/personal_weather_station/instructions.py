"""What to type into the weather station, worked out for this installation.

This integration has no "add device" button: stations appear on their own the
first time they post. Someone who has not read the documentation gets an empty
page and no hint, so the setup flow ends on these instructions and a repair
brings them back until a station actually shows up.
"""

from pathlib import Path
from urllib.parse import urlparse

from homeassistant.components.http import StaticPathConfig
from homeassistant.const import CONF_PASSWORD
from homeassistant.helpers.network import NoURLAvailableError, get_url

from .const import DATA_IMAGES_REGISTERED, ENDPOINTS, IMAGES_URL


async def async_ensure_images(hass):
    """
    Serve the walkthrough screenshots, once per Home Assistant run.

    The setup wizard runs before async_setup does — Home Assistant only sets a
    component up once an entry exists — so this cannot live there. It is called
    from the flow instead, and guarded, because Home Assistant offers no way to
    unregister a static path and registering twice stacks a second route.

    Args:
        hass: Home Assistant instance.

    Returns:
        None
    """

    if hass.data.get(DATA_IMAGES_REGISTERED):
        return

    hass.data[DATA_IMAGES_REGISTERED] = True

    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                IMAGES_URL,
                str(Path(__file__).parent / "images"),
                cache_headers=True,
            )
        ]
    )


def image(name):
    """Markdown for one walkthrough screenshot, by file name."""

    return f"![]({IMAGES_URL}/{name})"


def async_urls(hass):
    """
    Addresses a station can post to, without their scheme.

    Deliberately internal only. A weather station sits on the same network, and
    nobody should be opening a port to the internet so it can upload. The field
    in the station app takes no "http://" either.

    Returns:
        list: host:port strings, possibly empty when Home Assistant knows of none.
    """

    try:
        url = get_url(hass, allow_external=False, allow_ip=True)
    except NoURLAvailableError:
        return []

    return [urlparse(url).netloc or url]


def async_placeholders(hass, station_key):
    """
    Build the placeholders of the instructions screen.

    Args:
        hass: Home Assistant instance.
        station_key: Key the user configured, or a falsy value when blank.

    Returns:
        dict: translation placeholders.
    """

    urls = async_urls(hass)

    if urls:
        addresses = "\n".join(f"  - `{url}`" for url in urls)
    else:
        addresses = (
            "  - Home Assistant could not work out its own address. Use the one "
            "your station can reach it at on your network, port included."
        )

    # Phrased to read correctly both after a dash and after a colon, since the
    # setup screen and the failure screen both use it.
    key_hint = (
        "the one you entered here"
        if station_key
        else "not needed, you left it blank — every request is accepted"
    )

    return {
        "urls": addresses,
        "urls_inline": ", ".join(f"`{url}`" for url in urls) or "your address",
        "key_hint": key_hint,
        "endpoints": "\n".join(f"  - `{path}`" for path in ENDPOINTS),
    }


def async_placeholders_for_entry(hass, entry):
    """Same, for an entry that already exists."""

    return async_placeholders(
        hass,
        entry.options.get(CONF_PASSWORD, entry.data.get(CONF_PASSWORD)),
    )
