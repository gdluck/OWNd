<!-- ccr-projects-attribution: {"github_login":"gdluck"} -->
_Requested by **A** · [project thread](https://claude.ai/code/project/chan_0159fxdtgHJqHFpnbme29u2L?thread=cmsg_0159fxdtgHJqHFpnbme29u2LKAHKjwFDvBofhmvrZKsE8m)_


Before: `*25*11#0*W##` .. `*25*15*W##` parsed as a bare `OWNEvent` / `OWNCommand` (the PR 82 rule: WHO 25 WHATs other than 21-28 and 31/32 are "some other event").

After: they are `OWNScenarioPlusEvent` (`action` = on / off / increase / decrease / stop, `object` = WHERE) and `OWNScenarioPlusCommand`, with builders `turn_on`, `turn_off`, `increase`, `decrease`, `stop` producing exactly the client's frames.

### Evidence

**libqtdevices TS10_1_0_23.** `scenario_device.cpp`:
```cpp
 36: // ScenarioPlus commands
 37: #define CMD_SCENARIO_PLUS_ON "11#0"
 38: #define CMD_SCENARIO_PLUS_OFF "12"
 39: #define CMD_SCENARIO_PLUS_INC "13#0#5"
 40: #define CMD_SCENARIO_PLUS_DEC "14#0#5"
 41: #define CMD_SCENARIO_PLUS_STOP "15"
159: ScenarioPlusDevice::ScenarioPlusDevice(QString address, int openserver_id) : device(QString("25"), address, openserver_id)
163: void ScenarioPlusDevice::turnOn() const
165:         sendCommand(CMD_SCENARIO_PLUS_ON);
```
(`:163-186` send the five commands on WHO 25.)

**Firmware.** bt_luci, identical on MyHomeServer1, F454 and F459 (`results/luci*.tsv`, column 4 = monitor port):

| Frame | Reply | Bus body | Monitor port echo |
|---|---|---|---|
| `*25*11#0*11##` | ACK | `B1 01 93 00` | `*25*11#0*11##` |
| `*25*12*11##` | ACK | `B1 01 94 00` | `*25*12*11##` |
| `*25*13#0#5*11##` | ACK | `B1 01 95 40` | `*25*13#0#5*11##` |
| `*25*14#0#5*11##` | ACK | `B1 01 96 40` | `*25*14#0#5*11##` |
| `*25*15*11##` | ACK | `B1 01 97 00` | `*25*15*11##` |

Five consecutive bus commands `93`-`97`, each accepted and echoed as an event. Emitted side (`reference/hex2own_corpus.tsv`): the binaries print `*25*12*1xx##` and `*25*15*1xx##` 64 times each and `*25*11#N*W##` / `*25*14#N#M*W##` for bus frames, so the event parser must accept the firmware's `1xx` WHERE form as well as the client's plain address; both are covered by the tests.

### How

`OWNd/message/cen.py`: new `OWNScenarioPlusEvent` and `OWNScenarioPlusCommand`; `_parse_who25_event` / `_parse_who25_command` route WHAT 11-15 to them (21-28 CEN+, 31/32 dry contact unchanged). Exported from `OWNd/message/__init__.py`. `tests/test_issue_77_firmware_findings.py` fix 9 expected a bare event for these frames and now expects the new class; new `tests/test_who25_scenario_plus.py`. `pytest`: 1241 passed, 1 skipped.

---

**How to check.** `libqtdevices` quotes are from tag `TS10_1_0_23` of OpenWebNet-HA/libqtdevices (BTicino's 2010 touch-screen client, used only as a second client, not as the reference). Firmware rows are replays of the exact frame on the original gateway translator binaries (ARM, from the MyHomeServer1, F454, F459, F461 and F450 images) under QEMU on a fake SCS bus: `ACK` = `*#*1##`, `NACK` = `*#*0##`, the bus body is what the program put on the SCS bus (hex, without the A8 / checksum / A3 framing). Spec = Legrand/BTicino "Open Web Net Language, WHO = 4" v2.0.0 (2013-11-27). Raw logs, command lists, the harness and the report are in [firmware_validation.zip](https://github.com/gdluck/OWNd/raw/firmware-validation-data/firmware_validation.zip) (`results/<program>[_<image>].tsv`, `results/*.cl` / `*.stub` / `*.mon`, `REPORT.md`). The firmware images themselves are not included.

Split out of #86 so each change can be checked on its own; all eight slices merge together without conflicts (1271 tests pass on the union).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_018oHp1P4vxxoFnaLUUZpbpZ
