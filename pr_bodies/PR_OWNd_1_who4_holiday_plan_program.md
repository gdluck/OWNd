<!-- ccr-projects-attribution: {"github_login":"gdluck"} -->
_Requested by **A** · [project thread](https://claude.ai/code/project/chan_0159fxdtgHJqHFpnbme29u2L?thread=cmsg_0159fxdtgHJqHFpnbme29u2LKAHKjwFDvBofhmvrZKsE8m)_


Before: `*4*115#1102*#0##` was read as "heat at -10.2 °C" (`set_temperature = -10.2`, `message_type = hvac_mode_target`).

After: it is read as "heating, holiday daily plan, program 2" (`program = 2`, `set_temperature = None`, `message_type = hvac_mode`). The event also exposes `program` for the `11xx` / `21xx` / `31xx` WHATs and `scenario` for `12xx` / `22xx` / `32xx`. `110#T`, `210#T` and `312#T#2` keep reading the temperature.

### Evidence

**Spec.** p. 56 and p. 64: the WHAT of the weekend / holiday plan is `115#parameterH` (heating) or `215#parameterH` (conditioning), where parameterH is the weekly program to resume, `1101`-`1103` / `2101`-`2103`. It is not a temperature field; temperatures appear only in `110#T` / `210#T` (p. 23, p. 56).

**libqtdevices TS10_1_0_23.** `thermal_device.cpp`:
```cpp
 65: 	WIN_WEEKEND = 115,               // weekend operation (festivo)
 66: 	WIN_PROGRAM = 1100,              // weekly program (1 out of 3)
 67: 	WIN_SCENARIO = 1200,             // scenario (1 out of 16, 99zones thermal regulator only)
209: 	int command = commandRange(what);
210: 	int program = what - command;
240: 	case SUM_WEEKEND:
241: 		values_list[DIM_PROGRAM] = msg.whatArgN(0) % 100;
246: 	case SUM_PROGRAM:
247: 		values_list[DIM_PROGRAM] = program;
252: 	case SUM_SCENARIO:
253: 		values_list[DIM_SCENARIO] = program;
285: 	case WIN_WEEKEND:
286: 		values_list[DIM_PROGRAM] = msg.whatArgN(0) % 100;
```
The parameter of 115/215 is `whatArgN(0) % 100`, a program number; `commandRange()` (`:350-358`) splits `1102` into command `1100` + program `2`.

**Firmware.** bt_termo (`results/termo.tsv` and `termo_f454`, `termo_F459`, `termo_f461`, `termo_F450.tsv`, identical on all five):

| Frame | Reply | Bus body | Reading |
|---|---|---|---|
| `*4*115#1102*#0##` | ACK | `D1 00 03 02 C1 14 01 00` | byte 6 = `14` holiday plan heating, byte 7 = `01` → program 2 |
| `*4*215#2102*#0##` | ACK | `D1 00 03 02 C1 24 01 00` | same for conditioning (`24`) |
| `*4*1102*#0##` | ACK | `D1 00 03 02 C1 11 01 00` | program 2 heating, same byte 7 |
| `*4*2102*#0##` | ACK | `D1 00 03 02 C1 21 01 00` | program 2 conditioning |
| `*4*1203*#0##` | ACK | `D1 00 03 02 C1 13 02 00` | scenario 3 |
| `*4*3113*#0##` | ACK | `D1 00 03 02 C1 01 0C 00` | program 13 generic |
| `*4*3209*#0##` | ACK | `D1 00 03 02 C1 03 08 00` | scenario 9 generic |

The `#1102` parameter is forwarded as the one-byte program index (`01`, zero-based), in the same byte the plain program command uses. There is no temperature on the bus. Compare the real setpoint write `*#4*#0*#14*0250*1##` → `D1 00 03 02 C1 12 32 00` (`32` = 25.0 °C), `REPORT.md` 2.1.

### How

`OWNd/message/heating.py`: a `115/215/315` frame with a parameter sets `program = int(param) % 100` and keeps `hvac_mode`; the existing "mode with parameter = target temperature" branch now runs only for the other WHATs. New `program` / `scenario` properties. Tests: `tests/test_who4_holiday_plan_program.py`. `pytest`: 1241 passed, 1 skipped.

---

**How to check.** `libqtdevices` quotes are from tag `TS10_1_0_23` of OpenWebNet-HA/libqtdevices (BTicino's 2010 touch-screen client, used only as a second client, not as the reference). Firmware rows are replays of the exact frame on the original gateway translator binaries (ARM, from the MyHomeServer1, F454, F459, F461 and F450 images) under QEMU on a fake SCS bus: `ACK` = `*#*1##`, `NACK` = `*#*0##`, the bus body is what the program put on the SCS bus (hex, without the A8 / checksum / A3 framing). Spec = Legrand/BTicino "Open Web Net Language, WHO = 4" v2.0.0 (2013-11-27). Raw logs, command lists, the harness and the report are in [firmware_validation.zip](https://github.com/gdluck/OWNd/raw/firmware-validation-data/firmware_validation.zip) (`results/<program>[_<image>].tsv`, `results/*.cl` / `*.stub` / `*.mon`, `REPORT.md`). The firmware images themselves are not included.

Split out of #86 so each change can be checked on its own; all eight slices merge together without conflicts (1271 tests pass on the union).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_018oHp1P4vxxoFnaLUUZpbpZ
