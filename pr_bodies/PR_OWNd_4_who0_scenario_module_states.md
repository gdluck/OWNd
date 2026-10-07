<!-- ccr-projects-attribution: {"github_login":"gdluck"} -->
_Requested by **A** · [project thread](https://claude.ai/code/project/chan_0159fxdtgHJqHFpnbme29u2L?thread=cmsg_0159fxdtgHJqHFpnbme29u2LKAHKjwFDvBofhmvrZKsE8m)_


Before: `*0*40#1*11##` was logged as "Scenario 40 from control panel 11 has been launched" (`scenario = 40`).

After: `OWNScenarioEvent.event` is `programming started` with `programming_scenario = 1` and `scenario = None`. WHAT 41 → `programming stopped`, 42 → `deleted`, 43 → `locked`, 44 → `unlocked`, 45 / 46 → `status 45` / `status 46`; a bare WHAT (no `#N`) targets all scenarios. WHAT 1-31 keep `event = launched`.

### Evidence

**libqtdevices TS10_1_0_23.** `scenario_device.cpp`:
```cpp
 27: enum
 28: {
 29: 	START_PROG = 40,
 30: 	STOP_PROG = 41,
 31: 	DELETE = 42,
 32: 	LOCK = 43,
 33: 	UNLOCK = 44,
 34: };
 97: 	// Here we need to check if incoming frame is in the form
 98: 	// *0*40*<where>##
 99: 	// since this locks all devices (not only our own address).
108: 	case LOCK:
109: 		status_index = DIM_LOCK;
121: 	case START_PROG:
127: 		if (what_arg_count > 0)
128: 			p = ScenarioProgrammingStatus(true, msg.whatArgN(0));
129: 		else
130: 			p = ScenarioProgrammingStatus(true, ALL_SCENARIOS);
```
`parseFrame` (`:93-156`) treats 40-44 as states of the scenario module and reads `#N` as the scenario being programmed.

**Firmware.** bt_luci, identical on MyHomeServer1, F454 and F459 (`results/luci.tsv`, `luci_f454.tsv`, `luci_F459.tsv`):

| Frame | Reply | Bus body |
|---|---|---|
| `*0*40#1*11##` | ACK | `11 00 1C 41` |
| `*0*41#1*11##` | ACK | `11 00 1C 61` |
| `*0*42*11##` | ACK | `11 00 1C 00` |
| `*0*42#1*11##` | ACK | `11 00 1C 21` |
| `*0*43*11##` | ACK | `11 00 1C FF` |
| `*0*44*11##` | ACK | `11 00 1C E0` |
| `*0*40*11##`, `*0*41*11##` | NACK | none |
| `*#0*11##` | NACK (no device on the fake bus) | `11 00 1C 80` (status request) |

Each state is a distinct command byte `1C xx` on the bus, nothing like the scenario launch `*0*N*W##` (`11 00 14 0N`). Emitted side: for bus frames the same binaries print `*0*42*31##` (5 corpus lines), `*0*43*31##`, `*0*45*99##`, `*0*46#9*99##`, `*0*42#5*01##`, `*0*42#21*00##` (`reference/hex2own_corpus.tsv`), so the parser also sees 45 and 46 with and without a parameter.

### How

`OWNd/message/scenario.py`: `OWNScenarioEvent` gains `event` and `programming_scenario`; for WHAT 40-46 `scenario` is `None` and the log names the state. No builders are added (OWNd has no WHO 0 command class and MyHOME does not program scenario modules). Tests: `tests/test_who0_scenario_module_states.py`. `pytest`: 1246 passed, 1 skipped.

---

**How to check.** `libqtdevices` quotes are from tag `TS10_1_0_23` of OpenWebNet-HA/libqtdevices (BTicino's 2010 touch-screen client, used only as a second client, not as the reference). Firmware rows are replays of the exact frame on the original gateway translator binaries (ARM, from the MyHomeServer1, F454, F459, F461 and F450 images) under QEMU on a fake SCS bus: `ACK` = `*#*1##`, `NACK` = `*#*0##`, the bus body is what the program put on the SCS bus (hex, without the A8 / checksum / A3 framing). Spec = Legrand/BTicino "Open Web Net Language, WHO = 4" v2.0.0 (2013-11-27). Raw logs, command lists, the harness and the report are in [firmware_validation.zip](https://github.com/gdluck/OWNd/raw/firmware-validation-data/firmware_validation.zip) (`results/<program>[_<image>].tsv`, `results/*.cl` / `*.stub` / `*.mon`, `REPORT.md`). The firmware images themselves are not included.

Split out of #86 so each change can be checked on its own; all eight slices merge together without conflicts (1271 tests pass on the union).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_018oHp1P4vxxoFnaLUUZpbpZ
