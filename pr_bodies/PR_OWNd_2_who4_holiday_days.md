<!-- ccr-projects-attribution: {"github_login":"gdluck"} -->
_Requested by **A** · [project thread](https://claude.ai/code/project/chan_0159fxdtgHJqHFpnbme29u2L?thread=cmsg_0159fxdtgHJqHFpnbme29u2LKAHKjwFDvBofhmvrZKsE8m)_


Before: `*4*13001*1##` and `*4*23001*1##` were read as AUTO (both ranges sat in the generic-mode list next to `33xxx`).

After: `13xxx` reads as HEAT and `23xxx` as COOL, and all three ranges expose the day count as `holiday_days` (`*4*23001*1##` → `mode = cool`, `holiday_days = 1`; `*4*33004*#0##` → `auto`, `4`).

### Evidence

**Spec.** p. 5 and p. 64, WHAT table: `13xxx` = holiday days, heating mode; `23xxx` = holiday days, conditioning mode; `33xxx` = holiday days, generic mode; xxx = 1..255 days.

**libqtdevices TS10_1_0_23.** `thermal_device.cpp`:
```cpp
 58: 	SUM_HOLIDAY = 23000,             // holiday operation (programma ferie)
 68: 	WIN_HOLIDAY = 13000,             // holiday operation (programma ferie)
258: 	case SUM_HOLIDAY:
259: 		values_list[DIM_PROGRAM] = program;
260: 		values_list[DIM_STATUS] = ST_HOLIDAY;
261: 		values_list[DIM_SEASON] = SE_SUMMER;
303: 	case WIN_HOLIDAY:
304: 		values_list[DIM_PROGRAM] = program;
305: 		values_list[DIM_STATUS] = ST_HOLIDAY;
306: 		values_list[DIM_SEASON] = SE_WINTER;
```
`23xxx` sets the summer season, `13xxx` the winter season; the client never maps either to automatic.

**Firmware.** bt_termo, identical on MyHomeServer1, F454, F459, F461, F450 (`results/termo*.tsv`):

| Frame | Reply | Bus body | Reading |
|---|---|---|---|
| `*4*13004*#0##` | NACK | none | monitor-only WHAT (Spec p. 64), not a command |
| `*4*23004*#0##` | NACK | none | same |
| `*4*33002#3115*#0##` | ACK | `D1 00 03 02 C1 05 02 0E` | holiday command: byte 7 = `02` days, byte 8 = program 15 |
| `*4*33005#3102*#0##` | ACK | `D1 00 03 02 C1 05 05 01` | 5 days, program 2 |

So the firmware carries the day count of the holiday WHATs as a real value (byte 7), and the heating / conditioning variants are status reports the central unit sends, which is what OWNd parses here.

### How

`OWNd/message/heating.py`: `23001-23255` moves to the COOL range, `13001-13255` to the HEAT range, `33xxx` stays AUTO; each sets `holiday_days = mode % 1000`. New `holiday_days` property. Tests: the two `test_mode_auto_weekly_*` cases in `tests/test_message_edges.py` encoded the old reading and are replaced by `test_mode_holiday_*`. `pytest`: 1239 passed, 1 skipped.

---

**How to check.** `libqtdevices` quotes are from tag `TS10_1_0_23` of OpenWebNet-HA/libqtdevices (BTicino's 2010 touch-screen client, used only as a second client, not as the reference). Firmware rows are replays of the exact frame on the original gateway translator binaries (ARM, from the MyHomeServer1, F454, F459, F461 and F450 images) under QEMU on a fake SCS bus: `ACK` = `*#*1##`, `NACK` = `*#*0##`, the bus body is what the program put on the SCS bus (hex, without the A8 / checksum / A3 framing). Spec = Legrand/BTicino "Open Web Net Language, WHO = 4" v2.0.0 (2013-11-27). Raw logs, command lists, the harness and the report are in [firmware_validation.zip](https://github.com/gdluck/OWNd/raw/firmware-validation-data/firmware_validation.zip) (`results/<program>[_<image>].tsv`, `results/*.cl` / `*.stub` / `*.mon`, `REPORT.md`). The firmware images themselves are not included.

Split out of #86 so each change can be checked on its own; all eight slices merge together without conflicts (1271 tests pass on the union).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_018oHp1P4vxxoFnaLUUZpbpZ
