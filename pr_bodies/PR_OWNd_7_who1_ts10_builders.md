<!-- ccr-projects-attribution: {"github_login":"gdluck"} -->
_Requested by **A** · [project thread](https://claude.ai/code/project/chan_0159fxdtgHJqHFpnbme29u2L?thread=cmsg_0159fxdtgHJqHFpnbme29u2LKAHKjwFDvBofhmvrZKsE8m)_


Before: `OWNLightingCommand` could switch, dim to a percentage (`*#1*W*#1*L*S##`) and request status; it had no builder for the WHO 1 frames BTicino's own client sends for presets, single steps, fixed timers and the variable timer.

After: `set_brightness_preset(where, 2..10)`, `step_up(where[, delta, speed])`, `step_down(...)`, `switch_on_timed(where, 11..18)`, `set_variable_timer(where, h, m, s)`, `get_variable_timer(where)`. Pure additions, no existing frame changes.

### Evidence

**libqtdevices TS10_1_0_23.** `lighting_device.cpp`:
```cpp
 34: 	FIXED_TIMING_MIN = 11,
 35: 	FIXED_TIMING_MAX = 18,
 38: 	DIMMER_INC = 30,
 39: 	DIMMER_DEC = 31,
 63: int dimmer100LevelTo10(int level)      // maps 0..100 % to WHAT 2..10
110: void LightingDevice::fixedTiming(int value)
112: 	int v = FIXED_TIMING_MIN + value;
114: 		sendCommand(v);
119: void LightingDevice::variableTiming(int h, int m, int s)
121: 	if ((h >= 0 && h <= 255) && (m >= 0 && m <= 59) && (s >= 0 && s <= 59))
122: 		sendFrame(createWriteDimensionFrame(who, QString("%1*%2*%3*%4").arg(DIM_VARIABLE_TIMING)
131: void LightingDevice::requestVariableTiming()
133: 	sendRequest(DIM_VARIABLE_TIMING);
230: void DimmerDevice::increaseLevel()
232: 	sendCommand(DIMMER_INC);
240: void DimmerDevice::setLevel100(int level, int speed)
244: 	sendCommand(dimmer100LevelTo10(level));
409: void Dimmer100Device::increaseLevel100(int delta, int speed)
411: 	sendCommand(QString("%1#%2#%3").arg(DIMMER_INC).arg(delta).arg(speed));
```
(`DIM_VARIABLE_TIMING = 2`, `lighting_device.h:59`.) The argument ranges of the new builders are the client's: h 0..255, m / s 0..59, timers 11..18, presets 2..10.

**Firmware.** bt_luci, identical on MyHomeServer1, F454 and F459 (`results/luci*.tsv`):

| Frame | Builder | Reply | Bus body |
|---|---|---|---|
| `*1*2*11##` | `set_brightness_preset(11, 2)` | ACK | `11 00 12 1D` |
| `*1*5*11##` | `set_brightness_preset(11, 5)` | ACK | `11 00 12 4D` |
| `*1*10*11##` | `set_brightness_preset(11, 10)` | ACK | `11 00 12 9D` |
| `*1*30*11##` | `step_up(11)` | ACK | `11 00 12 03` |
| `*1*31*11##` | `step_down(11)` | ACK | `11 00 12 04` |
| `*1*30#20#1*11##` | `step_up(11, 20, 1)` | ACK | `D1 11 01 42 0D 03 14 01` |
| `*1*31#20#255*11##` | `step_down(11, 20, 255)` | ACK | `D1 11 01 42 0D 04 14 FF` |
| `*1*11*11##` | `switch_on_timed(11, 11)` | ACK | `11 00 12 16` |
| `*1*18*11##` | `switch_on_timed(11, 18)` | ACK | `11 00 12 86` |
| `*#1*11*#2*0*1*0##` | `set_variable_timer(11, 0, 1, 0)` | ACK | `D1 11 01 42 06 00 01 00` |
| `*#1*11*2##` | `get_variable_timer(11)` | NACK (no device on the fake bus) | `D1 11 01 43 06 00 00 00` (request sent) |

Every frame is accepted with a bus frame; the delta / speed and h / m / s values are visible in the long frames (`14 01`, `14 FF`, `00 01 00`).

### How

`OWNd/message/lighting.py`: six classmethods on `OWNLightingCommand` with the client's range checks (`ValueError` outside). Tests: `tests/test_who1_ts10_builders.py`. `pytest`: 1241 passed, 1 skipped.

---

**How to check.** `libqtdevices` quotes are from tag `TS10_1_0_23` of OpenWebNet-HA/libqtdevices (BTicino's 2010 touch-screen client, used only as a second client, not as the reference). Firmware rows are replays of the exact frame on the original gateway translator binaries (ARM, from the MyHomeServer1, F454, F459, F461 and F450 images) under QEMU on a fake SCS bus: `ACK` = `*#*1##`, `NACK` = `*#*0##`, the bus body is what the program put on the SCS bus (hex, without the A8 / checksum / A3 framing). Spec = Legrand/BTicino "Open Web Net Language, WHO = 4" v2.0.0 (2013-11-27). Raw logs, command lists, the harness and the report are in [firmware_validation.zip](https://github.com/gdluck/OWNd/raw/firmware-validation-data/firmware_validation.zip) (`results/<program>[_<image>].tsv`, `results/*.cl` / `*.stub` / `*.mon`, `REPORT.md`). The firmware images themselves are not included.

Split out of #86 so each change can be checked on its own; all eight slices merge together without conflicts (1271 tests pass on the union).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_018oHp1P4vxxoFnaLUUZpbpZ
