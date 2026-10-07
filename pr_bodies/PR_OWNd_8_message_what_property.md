<!-- ccr-projects-attribution: {"github_login":"gdluck"} -->
_Requested by **A** · [project thread](https://claude.ai/code/project/chan_0159fxdtgHJqHFpnbme29u2L?thread=cmsg_0159fxdtgHJqHFpnbme29u2LKAHKjwFDvBofhmvrZKsE8m)_


Before: a consumer that needs the raw WHAT of a status frame had to read the private `_what`.

After: read-only `OWNMessage.what` (`int`, or `None` for dimension frames). No behaviour change.

### Why

`*4*1*Z##` / `*4*0*Z##` is the zone's season frame, not a mode change: Spec p. 13, 16, 19 and 63 list it as "zone operation mode" (1 heating, 0 conditioning) next to the setpoint frames, and bt_termo emits `*4*1*Z##` together with every `*#4*Z*12*TTTT*3##` report (`reference/SCS_OWN_MAP_bt_termo.md` section 4, `hex2own_corpus.tsv`: 35 lines `*4*1*Z##`, 40 lines `*4*0*Z##`). `OWNHeatingEvent.mode` maps both to heat / cool, which is right for a central unit but wrong for a zone in automatic mode. libqtdevices keeps AUTO on these frames (`probe_device.cpp:240-253`):
```cpp
240: 	case CONDITIONING:
241: 	case HEATING:
242: 		if (!isCommandFrame(msg))
243: 			break;
244: 		if (status != ST_MANUAL && status != ST_AUTO)
246: 			values_list[DIM_STATUS] = status = ST_AUTO;
```
The companion MyHOME change (OpenWebNet-HA/MyHOME#649) applies the same rule and needs the raw WHAT to recognise the frame; it falls back to `_what` on older OWNd releases, so the two can merge in any order.

### How

`OWNd/message/base.py`: one property. Tests: `tests/test_message_what_property.py`. `pytest`: 1239 passed, 1 skipped.

---

**How to check.** `libqtdevices` quotes are from tag `TS10_1_0_23` of OpenWebNet-HA/libqtdevices (BTicino's 2010 touch-screen client, used only as a second client, not as the reference). Firmware rows are replays of the exact frame on the original gateway translator binaries (ARM, from the MyHomeServer1, F454, F459, F461 and F450 images) under QEMU on a fake SCS bus: `ACK` = `*#*1##`, `NACK` = `*#*0##`, the bus body is what the program put on the SCS bus (hex, without the A8 / checksum / A3 framing). Spec = Legrand/BTicino "Open Web Net Language, WHO = 4" v2.0.0 (2013-11-27). Raw logs, command lists, the harness and the report are in [firmware_validation.zip](https://github.com/gdluck/OWNd/raw/firmware-validation-data/firmware_validation.zip) (`results/<program>[_<image>].tsv`, `results/*.cl` / `*.stub` / `*.mon`, `REPORT.md`). The firmware images themselves are not included.

Split out of #86 so each change can be checked on its own; all eight slices merge together without conflicts (1271 tests pass on the union).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_018oHp1P4vxxoFnaLUUZpbpZ
