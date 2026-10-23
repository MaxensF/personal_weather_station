"""Translation completeness of strings.json and the generated language files."""

import json
import pathlib
import re

import pytest

from custom_components.personal_weather_station.const import (
    SENSOR_LIST,
    SENSOR_TRANSLATION_KEYS,
)

COMPONENT = pathlib.Path("custom_components/personal_weather_station")
STRINGS = COMPONENT / "strings.json"
TRANSLATIONS = COMPONENT / "translations"

def flatten(data, prefix=()):
    for key, value in data.items():
        if isinstance(value, dict):
            yield from flatten(value, prefix + (key,))
        else:
            yield prefix + (key,), value


def placeholders(text):
    return set(re.findall(r"\{([a-z_]+)\}", str(text)))


@pytest.fixture(scope="module")
def strings():
    return json.loads(STRINGS.read_text(encoding="utf-8"))


def test_every_sensor_has_a_name(strings):
    """A missing name would leave Home Assistant showing nothing useful."""

    translated = strings["entity"]["sensor"]

    for key in SENSOR_LIST:
        translation_key = SENSOR_TRANSLATION_KEYS[key]
        assert translation_key in translated, f"{key} has no translated name"
        assert translated[translation_key]["name"].strip()


def test_translation_keys_are_slugs():
    """Home Assistant rejects anything else, and payload keys are not slugs."""

    for key, slug in SENSOR_TRANSLATION_KEYS.items():
        assert re.fullmatch(r"[a-z0-9_]+", slug), f"{key} produced {slug!r}"

    assert len(set(SENSOR_TRANSLATION_KEYS.values())) == len(SENSOR_TRANSLATION_KEYS)


def test_names_are_sentence_case(strings):
    """Home Assistant's naming convention, checked on the words we control."""

    allowed = re.compile(r"^[A-Z0-9]")

    for platform in strings["entity"].values():
        for key, value in platform.items():
            name = value["name"]
            assert allowed.match(name), f"{key}: {name!r} does not start with a capital"


@pytest.mark.parametrize(
    "path", sorted(TRANSLATIONS.glob("*.json")), ids=lambda p: p.stem
)
def test_translation_is_complete(path, strings):
    """
    Every language must carry exactly the keys of the English source.

    A generated file that drifts is the realistic failure here, and a lost
    placeholder breaks the Repairs message at runtime rather than at build time.
    """

    expected = dict(flatten(strings))
    found = dict(flatten(json.loads(path.read_text(encoding="utf-8"))))

    assert not expected.keys() - found.keys(), "clés manquantes"
    assert not found.keys() - expected.keys(), "clés orphelines"

    for key, value in found.items():
        assert str(value).strip(), f"valeur vide : {'::'.join(key)}"
        assert not placeholders(expected[key]) - placeholders(value), (
            f"placeholder perdu : {'::'.join(key)}"
        )


async def test_entity_names_come_from_translations(hass, setup_pws):
    """The names must resolve through the translation files, not hard coded."""

    _, client = await setup_pws()

    await client.get("/data/upload.php?wsid=my_station&t1tem=21.5&t1wdir=237")
    await hass.async_block_till_done()

    from .conftest import entity_id_for

    temperature = hass.states.get(entity_id_for(hass, "my_station", "t1tem"))
    assert temperature.attributes["friendly_name"] == "my_station Outdoor temperature"

    offset = hass.states.get(
        entity_id_for(hass, "my_station", "wind_offset", "number")
    )
    assert offset.attributes["friendly_name"] == "my_station Wind direction offset"
