#!/usr/bin/env python3
"""Build the translation files of the Personal Weather Station integration.

strings.json is the single source of truth. The 163 sensor names in it are
generated from SENSOR_LIST, so a new sensor never needs a hand written English
string. Every other language is expanded from a phrase book, which holds only
the distinct phrases: the seven channels of a multi channel sensor repeat the
same wording, and translating it once keeps the whole set consistent.

Usage:
    python scripts/build_translations.py strings   # refresh the English source
    python scripts/build_translations.py phrases   # dump the phrases to translate
    python scripts/build_translations.py build     # expand every phrase book
    python scripts/build_translations.py check     # verify completeness
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from _vocab import compose, sentence_case, split_channel

ROOT = pathlib.Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "personal_weather_station"
STRINGS = COMPONENT / "strings.json"
TRANSLATIONS = COMPONENT / "translations"
PHRASEBOOKS = ROOT / "scripts" / "phrasebooks"

# The languages the Home Assistant frontend ships, from
# home-assistant/frontend:src/translations/translationMetadata.json
LANGUAGES = [
    "af", "ar", "bg", "bn", "bs", "ca", "cs", "cy", "da", "de", "el", "en",
    "en-GB", "eo", "es", "es-419", "et", "eu", "fa", "fi", "fr", "fy", "ga",
    "gl", "gsw", "he", "hi", "hr", "hu", "hy", "id", "is", "it", "ja", "ka",
    "ko", "lb", "lt", "lv", "mk", "ml", "nb", "nl", "nn", "pl", "pt", "pt-BR",
    "ro", "ru", "sk", "sl", "sq", "sr", "sr-Latn", "sv", "ta", "te", "th",
    "tr", "uk", "ur", "vi", "zh-Hans", "zh-Hant",
]



def _fixed_entities():
    """Names of the entities the integration builds itself, keyed by platform."""

    from custom_components.personal_weather_station.const import FIXED_ENTITY_NAMES

    return FIXED_ENTITY_NAMES


FIXED_ENTITIES = _fixed_entities()


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path, data):
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def sensor_names(binary_only=False):
    """
    Map each sensor translation key to its English sentence case name.

    Args:
        binary_only: Restrict to the keys served by the binary_sensor platform.

    Returns:
        dict: translation key -> name.
    """

    from custom_components.personal_weather_station.const import (
        SENSOR_LIST,
        SENSOR_TRANSLATION_KEYS,
    )

    return {
        SENSOR_TRANSLATION_KEYS[key]: sentence_case(meta["name"])
        for key, meta in SENSOR_LIST.items()
        if not binary_only or meta.get("binary")
    }


def flatten(data, prefix=()):
    """Yield (path, value) for every leaf string of a nested mapping."""

    for key, value in data.items():
        if isinstance(value, dict):
            yield from flatten(value, prefix + (key,))
        else:
            yield prefix + (key,), value


def placeholders(text):
    """Return the {placeholder} names a string carries."""

    import re

    return set(re.findall(r"\{([a-z_]+)\}", text))


def cmd_strings():
    """Regenerate the entity section of strings.json from SENSOR_LIST."""

    strings = load_json(STRINGS)

    entity = {"sensor": {}, "binary_sensor": {}, "number": {}, "button": {}}

    for key, name in sorted(sensor_names().items()):
        entity["sensor"][key] = {"name": name}

        # A sensor whose reading is a code rather than a quantity carries the
        # names of its states as well.
        if (states := sensor_states(key)) is not None:
            entity["sensor"][key]["state"] = states

    # A station upgrading from an earlier release keeps these on the sensor
    # platform, so both spellings have to carry a name.
    for key, name in sorted(sensor_names(binary_only=True).items()):
        entity["binary_sensor"][key] = {"name": name}

    for platform, names in FIXED_ENTITIES.items():
        for key, name in names.items():
            entity[platform][key] = {"name": name}
        entity[platform] = dict(sorted(entity[platform].items()))

    strings["entity"] = entity
    dump_json(STRINGS, strings)
    dump_json(TRANSLATIONS / "en.json", strings)

    total = sum(len(value) for value in entity.values())
    print(f"strings.json : {total} noms d'entités, {count_strings(strings)} chaînes")


def count_strings(data):
    return sum(1 for _ in flatten(data))


# English labels for the coded readings, keyed the way SENSOR_LIST names them.
# One entry per sensor that declares `options`; the keys must match its values.
SENSOR_STATE_LABELS = {
    "t9voclv": {
        "very_low": "Very low",
        "low": "Low",
        "moderate": "Moderate",
        "high": "High",
        "very_high": "Very high",
    },
}


def sensor_states(key):
    """The state labels of a coded sensor, or None if it reports a quantity."""

    return SENSOR_STATE_LABELS.get(key)


def phrase_list():
    """The distinct phrases a translator actually has to deal with."""

    phrases = {}

    for name in sensor_names().values():
        _, base = split_channel(name)
        phrases[base] = None

    for names in FIXED_ENTITIES.values():
        for name in names.values():
            phrases[name] = None

    return list(phrases)


def state_phrase_list():
    """The distinct state labels, which translate on their own."""

    phrases = {}

    for states in SENSOR_STATE_LABELS.values():
        for label in states.values():
            phrases[label] = None

    return list(phrases)


def cmd_phrases():
    """Print the phrase list, as a template for a new phrase book."""

    template = {phrase: "" for phrase in phrase_list()}
    states = {phrase: "" for phrase in state_phrase_list()}
    ui = {
        path[-1] if len(path) < 2 else "::".join(path): value
        for path, value in flatten(load_json(STRINGS))
        if path[0] != "entity" and not walkthrough_alias("::".join(path))
    }

    print(
        json.dumps(
            {"entities": template, "states": states, "ui": ui},
            indent=2,
            ensure_ascii=False,
        )
    )


WALKTHROUGH_STEPS = ("station", "settings", "server", "form", "confirm")


def walkthrough_alias(key):
    """
    The config key holding the same text as an options walkthrough key.

    Both flows show the same five screens of the station's app, so translating
    them twice would be asking a translator to do the same work again and
    leaving two copies to drift apart.
    """

    prefix = "options::step::"

    if not key.startswith(prefix):
        return None

    rest = key[len(prefix) :]

    if rest.split("::", 1)[0] not in WALKTHROUGH_STEPS:
        return None

    return "config::step::" + rest


def expand(language, book):
    """Expand a phrase book into a full translation file."""

    strings = load_json(STRINGS)
    entities = book.get("entities", {})
    result = json.loads(json.dumps(strings))

    names = sensor_names()

    for platform, keys in result["entity"].items():
        # The sensor platform mixes payload driven sensors with the diagnostics
        # the integration builds itself.
        source = {**names, **FIXED_ENTITIES.get(platform, {})}

        for key in keys:
            english = source.get(key)

            if english is None:
                continue

            channel, base = split_channel(english)

            translated = entities.get(base)

            if translated:
                keys[key] = {"name": compose(channel, translated)}

            # State labels are their own phrases: they say nothing about which
            # sensor they belong to, so they translate once and are reused.
            if (states := sensor_states(key)) is not None:
                book_states = book.get("states", {})
                rendered = {
                    option: book_states.get(label) or label
                    for option, label in states.items()
                }
                keys[key].setdefault("name", source.get(key, key))
                keys[key]["state"] = rendered

    for path, value in flatten(strings):
        if path[0] == "entity":
            continue

        ui = book.get("ui", {})
        key = "::".join(path)
        translated = ui.get(key) or ui.get(walkthrough_alias(key) or "")

        if not translated:
            continue

        target = result

        for part in path[:-1]:
            target = target[part]

        target[path[-1]] = translated

    return result


def cmd_build():
    """Expand every phrase book that exists into translations/."""

    built = []
    missing = []
    seeded = []

    for language in LANGUAGES:
        if language == "en":
            continue

        book_path = PHRASEBOOKS / f"{language}.json"

        if not book_path.exists():
            missing.append(language)
            continue

        book = load_json(book_path)
        dump_json(TRANSLATIONS / f"{language}.json", expand(language, book))
        built.append(language)

        if book.get("quality") != "reviewed":
            seeded.append(language)

    print(f"{len(built)} langues générées : {' '.join(built)}")

    if seeded:
        print(f"{len(seeded)} en attente de relecture : {' '.join(seeded)}")

    if missing:
        print(f"{len(missing)} sans dictionnaire : {' '.join(missing)}")


def cmd_check():
    """Verify that every translation matches the English source."""

    reference = load_json(STRINGS)
    expected = {path: value for path, value in flatten(reference)}
    failures = []

    for path in sorted(TRANSLATIONS.glob("*.json")):
        data = load_json(path)
        found = dict(flatten(data))

        for key in expected.keys() - found.keys():
            failures.append(f"{path.name}: clé manquante {'::'.join(key)}")

        for key in found.keys() - expected.keys():
            failures.append(f"{path.name}: clé orpheline {'::'.join(key)}")

        for key, value in found.items():
            if key not in expected:
                continue
            if not str(value).strip():
                failures.append(f"{path.name}: valeur vide {'::'.join(key)}")
            elif placeholders(expected[key]) - placeholders(str(value)):
                failures.append(
                    f"{path.name}: placeholder perdu dans {'::'.join(key)}"
                )

    for failure in failures[:40]:
        print(failure)

    print(
        f"{len(list(TRANSLATIONS.glob('*.json')))} fichiers, "
        f"{len(expected)} chaînes attendues, {len(failures)} problèmes"
    )

    return 1 if failures else 0


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "check"
    sys.exit(
        {
            "strings": cmd_strings,
            "phrases": cmd_phrases,
            "build": cmd_build,
            "check": cmd_check,
        }[command]()
        or 0
    )
