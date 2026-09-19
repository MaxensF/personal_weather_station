"""Value parsing and normalization."""

import pytest

from custom_components.personal_weather_station.normalizer import (
    apply_wind_offset,
    normalize_battery,
    parse_value,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, None),
        ("", None),
        ("   ", None),
        ("72", 72),
        ("-3", -3),
        ("22.5", 22.5),
        ("1e3", 1000.0),
        (" 18.1 ", 18.1),
        ("abc", "abc"),
        ("1.00", 1.0),
    ],
)
def test_parse_value(raw, expected):
    assert parse_value(raw) == expected


def test_parse_value_keeps_int_type():
    """Whole numbers must not silently become floats."""

    assert isinstance(parse_value("72"), int)
    assert isinstance(parse_value("72.0"), float)


@pytest.mark.parametrize(
    ("value", "scale", "expected"),
    [
        (1, 1, 100),
        (0, 1, 0),
        # The document's own example sends 2 for a sensor it describes as
        # binary, so the clamp has to hold.
        (2, 1, 100),
        # A 0~5 level is a band, not a charge. The lowest band is not a flat
        # battery, and the highest is not a brand new one.
        (0, 5, 5),
        (1, 5, 20),
        (2, 5, 40),
        (3, 5, 60),
        (4, 5, 80),
        (5, 5, 95),
        # Out of range in either direction still lands on a real level.
        (9, 5, 95),
        (-1, 5, 5),
        (None, 5, None),
        ("abc", 5, None),
        (-4, 1, 0),
    ],
)
def test_normalize_battery(value, scale, expected):
    assert normalize_battery(value, scale) == expected


@pytest.mark.parametrize(
    ("value", "offset", "expected"),
    [
        (237, 123, 0.0),
        (0, 0, 0),
        (10, -20, 350.0),
        (359, 1, 0.0),
        (180, 180, 0.0),
        (None, 90, None),
        ("n/a", 90, "n/a"),
        (45, 0, 45),
    ],
)
def test_apply_wind_offset(value, offset, expected):
    assert apply_wind_offset(value, offset) == expected
