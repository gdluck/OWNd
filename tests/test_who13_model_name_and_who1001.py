"""WHO 13 Dimension 27 model name (live F461 2.0.11) and WHO 1001 Dimension 11
autodiagnostic masks (own-firmware-oracle ``what19`` suite)."""

from __future__ import annotations

from OWNd.message import (
    OWNEvent,
    OWNGatewayCommand,
    OWNGatewayEvent,
    OWNLightingDiagnosticEvent,
    OWNMessage,
)


# ── WHO 13 DIMENSION 27: model name as ASCII codes (live F461 2.0.11) ────────


def test_model_name_reply_parses() -> None:
    message = OWNMessage.parse("*#13**27*70#52#54#49##")

    assert isinstance(message, OWNGatewayEvent)
    assert message.is_dimension_reply
    assert message.dimension == 27
    assert message.dimension_value == ["70#52#54#49"]
    assert message.model_name == "F461"
    assert "F461" in message.human_readable_log


def test_model_name_with_non_printable_codes_is_not_decoded() -> None:
    message = OWNMessage.parse("*#13**27*70#7#300##")

    assert isinstance(message, OWNGatewayEvent)
    assert message.model_name is None


def test_model_name_request_is_a_gateway_command() -> None:
    message = OWNMessage.parse("*#13**27##")

    assert isinstance(message, OWNGatewayCommand)
    assert message.is_dimension_request


# ── WHO 1001 DIMENSION 11: actuator autodiagnostic mask (oracle what19) ───────


def test_lighting_autodiagnostic_mask_parses() -> None:
    message = OWNMessage.parse("*#1001*74*11*111110111111111111110111##")

    assert isinstance(message, OWNLightingDiagnosticEvent)
    assert isinstance(message, OWNEvent)
    assert message.who == 1001
    assert message.where == "74"
    assert message.dimension == 11
    assert message.dimension_value == ["111110111111111111110111"]
    assert message.diagnostic_mask == "111110111111111111110111"
    assert message.cleared_bits == (6, 21)
    assert "74" in message.human_readable_log


def test_lighting_autodiagnostic_other_shapes_have_no_mask() -> None:
    request = OWNMessage.parse("*#1001*74##")
    assert request is not None and request.who == 1001

    other = OWNMessage.parse("*#1001*74*12*5##")
    assert isinstance(other, OWNLightingDiagnosticEvent)
    assert other.diagnostic_mask is None
    assert other.cleared_bits is None
