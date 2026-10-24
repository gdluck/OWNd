"""``set_central_mode`` and ``central_status`` checked against the firmware oracle.

- ``set_central_mode`` only on a central-unit ``#`` address: the plain zone form
  ``*4*311*Z##`` is ``nack``/``silent`` on all 12 emulated gateways
  (``thermo-zone-mode`` and ``ownd-pr82-heating``), and a live F461 2.0.11
  NACKs ``*4*311*2##`` while it ACKs ``*4*311*#2##``.
- ``central_status`` builds ``*#4*WHERE*14##``, which six gateways forward to
  the bus (``trace-corpus``); it goes unanswered without a central unit.
"""

from __future__ import annotations

import warnings

import pytest

from OWNd.message import CLIMATE_MODE_AUTO, CLIMATE_MODE_HEAT, OWNHeatingCommand


@pytest.mark.parametrize("where", ["1", "2", "0", "23#1", "", "#", "##0", "#0*22", "#a", "#0\n", "#١"])
def test_set_central_mode_requires_a_central_address(where: str) -> None:
    with pytest.raises(ValueError, match="central unit"):
        OWNHeatingCommand.set_central_mode(where, CLIMATE_MODE_AUTO)


@pytest.mark.parametrize(
    ("where", "frame"),
    [("#0", "*4*311*#0##"), ("#0#1", "*4*311*#0#1##"), ("#23", "*4*311*#23##")],
)
def test_set_central_mode_keeps_central_addresses(where: str, frame: str) -> None:
    assert str(OWNHeatingCommand.set_central_mode(where, CLIMATE_MODE_AUTO)) == frame


def test_set_central_mode_default_is_the_central_unit() -> None:
    assert str(OWNHeatingCommand.set_central_mode(mode=CLIMATE_MODE_HEAT)) == "*4*1*#0##"


def test_central_status_deprecation_names_the_real_reason() -> None:
    """``*#4*#0*14##`` is forwarded by F453, F453AV, F460, F461, MH200N and
    MyHomeServer1 in the oracle; it simply goes unanswered without a central unit."""
    doc = OWNHeatingCommand.central_status.__doc__ or ""
    assert "which gateways refuse" not in doc
    assert "unanswered without a central unit" in doc
    assert "F461" in doc

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        command = OWNHeatingCommand.central_status("#0")
    assert str(command) == "*#4*#0*14##"
    (warning,) = caught
    assert issubclass(warning.category, DeprecationWarning)
    text = str(warning.message)
    assert "refuse" not in text
    assert "central unit" in text
    assert "status('#0')" in text
