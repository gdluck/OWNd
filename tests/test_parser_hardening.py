"""Frames real gateways send that OWNd could not read (MyHOME#139, firmware oracle who13-clock)."""

from __future__ import annotations

import datetime as dt

import pytest

from OWNd.message import (
    MESSAGE_TYPE_TARGET_TEMPERATURE,
    OWNGatewayCommand,
    OWNGatewayEvent,
    OWNHeatingEvent,
    OWNMessage,
)


# ── WHO 4 DIMENSION 14 with a '#'-prefixed setpoint (MyHOME#139) ─────────────


def test_hash_prefixed_setpoint_parses_as_dimension_14() -> None:
    message = OWNMessage.parse("*#4*#1*14*#0230*1##")

    assert isinstance(message, OWNHeatingEvent)
    assert message.is_dimension_reply
    assert message.dimension == 14
    assert message.zone == 1
    assert message.message_type == MESSAGE_TYPE_TARGET_TEMPERATURE
    assert message.set_temperature == 23.0
    assert message.dimension_value == ["#0230", "1"]
    assert str(message) == "*#4*#1*14*#0230*1##"


def test_plain_setpoint_is_unchanged() -> None:
    message = OWNMessage.parse("*#4*#1*14*0230*1##")

    assert isinstance(message, OWNHeatingEvent)
    assert message.set_temperature == 23.0
    assert message.dimension_value == ["0230", "1"]


@pytest.mark.parametrize(
    "frame",
    [
        "*#4*#1*12*#0230*1##",  # '#' value accepted for dimension 14 only
        "*#1*11*1*#5##",
        "*#4*#1*14*0230*#1##",  # only the setpoint may carry it
    ],
)
def test_hash_values_elsewhere_still_do_not_parse(frame: str) -> None:
    assert OWNMessage.parse(frame) is None


# ── WHO 13 clock echoes with timezone values the gateways ACK ────────────────
# own-firmware-oracle who13-clock: F450, F453, F453AV, F460, F461, H4684,
# MH200, MH200N and MH202 ACK `0530` and `124` and echo the write; F454 and
# F459 ACK `124` only; the F450 reports the stored `0530` on later reads.


@pytest.mark.parametrize(
    ("frame", "raw_timezone"),
    [
        ("*#13**#0*14*30*00*0530##", "0530"),
        ("*#13**#0*14*30*00*124##", "124"),
        ("*#13**#22*14*30*00*0530*03*21*10*2026##", "0530"),
        ("*#13**#22*14*30*00*124*03*21*10*2026##", "124"),
    ],
)
def test_clock_echo_with_unexpressible_timezone_parses(frame: str, raw_timezone: str) -> None:
    message = OWNMessage.parse(frame)

    assert isinstance(message, OWNGatewayCommand)
    assert message.raw_timezone == raw_timezone
    assert message.timezone == ""
    assert message.time is not None
    assert message.time.replace(tzinfo=None) == dt.time(14, 30, 0)
    assert message.time.tzinfo is None


@pytest.mark.parametrize("raw", ["0530", "124", "199", "1240"])
def test_clock_reply_with_unexpressible_timezone_parses(raw: str) -> None:
    message = OWNMessage.parse(f"*#13**0*14*30*00*{raw}##")

    assert isinstance(message, OWNGatewayEvent)
    assert message.raw_timezone == raw
    assert message.timezone == ""
    assert message.time == dt.time(14, 30, 0)


@pytest.mark.parametrize("raw", ["200", "099", "024", "2", "12", "2000", "9999"])
def test_other_malformed_timezones_are_still_rejected(raw: str) -> None:
    with pytest.raises(ValueError):
        OWNMessage.parse(f"*#13**0*14*30*00*{raw}##")


@pytest.mark.parametrize(
    ("raw", "offset"),
    [("000", "+00:00"), ("001", "+01:00"), ("002", "+02:00"), ("102", "-02:00"), ("013", "+13:00"), ("123", "-23:00")],
)
def test_whole_hour_timezones_still_decode(raw: str, offset: str) -> None:
    message = OWNMessage.parse(f"*#13**0*14*30*00*{raw}##")

    assert isinstance(message, OWNGatewayEvent)
    assert message.timezone == offset


@pytest.mark.parametrize("raw", ["999", ""])
def test_unset_timezone_is_still_local_time(raw: str) -> None:
    message = OWNMessage.parse(f"*#13**0*14*30*00*{raw}##")

    assert isinstance(message, OWNGatewayEvent)
    assert message.timezone == ""
