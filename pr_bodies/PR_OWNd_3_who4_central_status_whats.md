<!-- ccr-projects-attribution: {"github_login":"gdluck"} -->
_Requested by **A** · [project thread](https://claude.ai/code/project/chan_0159fxdtgHJqHFpnbme29u2L?thread=cmsg_0159fxdtgHJqHFpnbme29u2LKAHKjwFDvBofhmvrZKsE8m)_


Before: `*4*30*#0##` and `*4*31*#0##` logged "Zone #0's mode is unknown".

After: they log "central unit reports a failure was discovered" / "the central unit battery is KO"; `22`, `23`, `24` log the probe status. `mode` stays `None` and the message type is unchanged, so no consumer behaviour changes; only the log text is specific.

### Evidence

**Spec.** p. 5, p. 24 and p. 64, WHAT table: `22` at least one probe OFF, `23` at least one probe in protection, `24` at least one probe in manual, `30` failure discovered, `31` central unit battery KO. All five are status frames the central unit sends.

**libqtdevices TS10_1_0_23.** `thermal_device.cpp`:
```cpp
 46: 	REMOTE_CONTROL = 21,             // remote control enabled
 47: 	MALFUNCTIONING_FOUND = 30,       // malfunctioning found
 48: 	BATTERY_KO = 31,                 // battery ko
214: 	case REMOTE_CONTROL:
215: 	case MALFUNCTIONING_FOUND:
216: 	case BATTERY_KO:
217: 		break;
```
The client knows 30 and 31 by name and deliberately leaves the mode untouched for them, which is what OWNd does.

**Firmware.** Not a command: none of these WHATs is in the bt_termo command set (`REPORT.md` 2.1 lists every accepted zone / central command), and the emitted corpus (`reference/hex2own_corpus.tsv`, 26,810 lines) contains none of them, so this slice is spec-backed only. It changes no parsing result.

### How

`OWNd/message/heating.py`: one `elif self._mode in (22, 23, 24, 30, 31)` branch before the "unknown" fallback. Tests: `tests/test_who4_central_status_whats.py`. `pytest`: 1243 passed, 1 skipped.

---

**How to check.** `libqtdevices` quotes are from tag `TS10_1_0_23` of OpenWebNet-HA/libqtdevices (BTicino's 2010 touch-screen client, used only as a second client, not as the reference). Firmware rows are replays of the exact frame on the original gateway translator binaries (ARM, from the MyHomeServer1, F454, F459, F461 and F450 images) under QEMU on a fake SCS bus: `ACK` = `*#*1##`, `NACK` = `*#*0##`, the bus body is what the program put on the SCS bus (hex, without the A8 / checksum / A3 framing). Spec = Legrand/BTicino "Open Web Net Language, WHO = 4" v2.0.0 (2013-11-27). Raw logs, command lists, the harness and the report are in [firmware_validation.zip](https://github.com/gdluck/OWNd/raw/firmware-validation-data/firmware_validation.zip) (`results/<program>[_<image>].tsv`, `results/*.cl` / `*.stub` / `*.mon`, `REPORT.md`). The firmware images themselves are not included.

Split out of #86 so each change can be checked on its own; all eight slices merge together without conflicts (1271 tests pass on the union).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_018oHp1P4vxxoFnaLUUZpbpZ
