"""Shared helpers for the translation tooling."""

import re

# Kept verbatim when converting a name to sentence case: acronyms, chemical
# formulas and channel labels.
ACRONYMS = {
    "API", "AQI", "CO", "CO2", "HCHO", "HCHO/VOC", "NO2", "NO3", "NOX", "NOY",
    "PM", "PM10", "PM2.5", "SO2", "SO4", "UV", "UVI", "VOC", "WBGT", "X", "Y",
}
ACRONYMS |= {f"CH{index}" for index in range(1, 9)}

CHANNEL_RE = re.compile(r"^(CH[1-9]) (.+)$")


def sentence_case(name):
    """
    Convert a title case name to the sentence case Home Assistant expects.

    Args:
        name: Name as written in SENSOR_LIST.

    Returns:
        str: "Outdoor Temperature" becomes "Outdoor temperature", while
            "PM2.5 AQI" and "CH1 Battery Status" keep their acronyms.
    """

    words = name.split()

    return " ".join(
        word
        if index == 0 or word in ACRONYMS or word[0].isdigit()
        else word.lower()
        for index, word in enumerate(words)
    )


def split_channel(name):
    """
    Split "CH3 battery status" into its channel label and its base phrase.

    Channels 1 to 7 repeat the same wording seven times over. Translating the
    base phrase once keeps the whole set consistent and cuts the work by more
    than half.

    Args:
        name: Sentence case name.

    Returns:
        tuple: (channel or None, base phrase). The base phrase is capitalized.
    """

    match = CHANNEL_RE.match(name)

    if not match:
        return None, name

    channel, rest = match.groups()

    return channel, rest[0].upper() + rest[1:]


def compose(channel, phrase):
    """Rebuild a full name from a channel label and a translated phrase."""

    if channel is None:
        return phrase

    return f"{channel} {phrase[0].lower() + phrase[1:]}"
